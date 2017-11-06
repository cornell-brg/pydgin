//=========================================================================
// task-trace-annotate.cc
//=========================================================================
// Author : Shreesha Srinath
// Date   : November 5th, 2017
//
// Program reads the task-trace.csv file, jal.csv file dumped by
// disassemble.py script, runtime-metadata and dumps out a trace file that
// is annotated with spawn locations.
//
// NOTE: I found this useful C++11-based CSV header library which is used
// for parsing the csv trace dumps.
//
//   https://github.com/ben-strasser/fast-cpp-csv-parser
//

#include "csv.h"
#include "cxxopts.hpp"

#include <algorithm>
#include <deque>
#include <fstream>
#include <iostream>
#include <limits>
#include <map>
#include <string>
#include <vector>

//-------------------------------------------------------------------------
// TraceEntry
//-------------------------------------------------------------------------
// Struct to represent an entry in the trace csv file

struct TraceEntry {
  int pid;
  int tid;
  int pc;
  int stype;

  TraceEntry( int pid, int tid, int pc, int stype )
    : pid( pid ), tid( tid ), pc( pc ), stype( stype )
  { }
};

// Helper function to print the struct
std::ostream& operator<< ( std::ostream& o, const TraceEntry& e )
{
  o << std::hex << "[" << e.pid << "," << e.tid << ","
    << e.pc << "," << e.stype << "]" << std::endl;
  return o;
}

//-------------------------------------------------------------------------
// main()
//-------------------------------------------------------------------------

int main ( int argc, char* argv[] )
{

  //-----------------------------------------------------------------------
  // Command line processing
  //-----------------------------------------------------------------------

  cxxopts::Options options( argv[0], " - Options for trace analysis" );

  options.positional_help( "trace calls runtime outdir" );
  options.add_options()
    ( "h, help", "Print help" )
    ( "trace", "Trace file <task-trace.csv>", cxxopts::value<std::string>() )
    ( "calls", "File with all call sites filtered <jal.csv>", cxxopts::value<std::string>() )
    ( "runtime", "Runtime metadata file", cxxopts::value<std::string>() )
    ( "outdir", "Output directory", cxxopts::value<std::string>() )
    ;

  const std::vector< std::string > positional_args = { "trace", "calls", "runtime", "outdir" };
  options.parse_positional( positional_args );
  options.parse( argc, argv );

  if ( options.count( "help" ) || options.count( "trace" ) == 0 ||
       options.count( "calls" ) == 0 || options.count( "runtime" ) == 0 || options.count( "outdir" ) == 0 ) {
    std::cout << options.help() << std::endl;
    return 0;
  }

  std::string tracefile   = options["trace"].as< std::string >();
  std::string callsfile   = options["calls"].as< std::string >();
  std::string runtimefile = options["runtime"].as< std::string >();
  std::string outdir      = options["outdir"].as< std::string >();

  //---------------------------------------------------------------------
  // Read the input tracefile
  //---------------------------------------------------------------------

  // Open the runtime metadata file
  io::CSVReader<7> runtime_md( runtimefile.c_str() );
  std::string col0, col1, col2, col3, col4, col5, col6;
  // Dummy header
  runtime_md.set_header( "col0", "col1", "col2", "col3", "col4", "col5", "col6" );
  // Read the pc values
  runtime_md.read_row( col0, col1, col2, col3, col4, col5, col6 );
  std::vector<int> pc_values = {
    std::stoi(col0), std::stoi(col1), std::stoi(col2), std::stoi(col3), std::stoi(col4), std::stoi(col5), std::stoi(col6)
  };
  // Read the function names
  runtime_md.read_row( col0, col1, col2, col3, col4, col5, col6 );
  std::vector< std::string > func_names = {
    col0, col1, col2, col3, col4, col5, col6
  };

  // Open the jal file
  io::CSVReader<3> calls_trace( callsfile.c_str() );
  calls_trace.read_header( io::ignore_extra_column, "pc", "asm", "dest" );
  std::string str0, str1, str2;

  std::map<int,std::string> runtime_jal_pcs;
  while ( calls_trace.read_row( str0, str1, str2 ) ) {
    std::ptrdiff_t pos = std::distance( pc_values.begin(), std::find( pc_values.begin(), pc_values.end(), std::stoi( str2, 0, 16 ) ) );
    if ( pos < pc_values.size() ) {
      runtime_jal_pcs[std::stoi(str0,0,16)] = func_names[pos];
    }
  }

  // Open the trace file
  io::CSVReader<4> in_trace( tracefile.c_str() );
  in_trace.read_header( io::ignore_extra_column, "pid", "tid", "pc", "stype" );

  std::string pid, tid, pc, stype;
  std::ofstream outfile;
  outfile.open( outdir + "/task-trace-annotated.csv" );
  outfile << "pid,tid,pc,spoint" << std::endl;
  while ( in_trace.read_row( pid, tid, pc, stype ) ) {
    outfile << std::hex << std::stoi( pid, 0, 16 ) << ",";
    outfile << std::hex << std::stoi( tid, 0, 16 ) << ",";
    outfile << std::hex << std::stoi( pc, 0, 16 ) << ",";
    // check if pc matches a target annotation loc
    int tgt = std::stoi( pc, 0, 16 );
    int match = 0;
    for ( auto kv: runtime_jal_pcs ) {
      if ( tgt == kv.first && kv.second == "run") {
        match = 1;
        break;
      }
    }
    outfile << match << std::endl;
  }
  outfile.close();

}
