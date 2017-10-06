//=========================================================================
// trace-analyze.cc
//=========================================================================
// Author : Shreesha Srinath
// Date   : October 5th, 2017
//
// Program reads the csv dump files from pydgin and reports the trace
// analysis for a given divergence mechanism.
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
// Entry
//-------------------------------------------------------------------------
// Struct to represent an entry in the csv file

struct Entry {
  int pid;
  int cid;
  int pc;
  int ret_cnt;

  Entry( int pid, int cid, int pc, int ret_cnt )
    : pid( pid ), cid( cid ), pc( pc ), ret_cnt( ret_cnt )
  { }
};

// Helper function to print the struct
std::ostream& operator<< ( std::ostream& o, const Entry& e )
{
  o << "[ " << e.pid << "," << e.cid << "," << e.pc << ","
    << e.ret_cnt << "]" << std::endl;
  return o;
}

//-------------------------------------------------------------------------
// max_share()
//-------------------------------------------------------------------------
// Given a vector of strands where each entry is a deque of pcs
// that correspond to the execution trace, the function returns a tuple
// of the unique instructions seen and the total number of instructions
// using no reconvergence

std::tuple< int,int > max_share( std::vector< std::deque<int> >& strands )
{
  int unique = 0;
  int total  = 0;
  int ncores = strands.size();

  if ( ncores == 1 ) {
    return std::make_tuple(strands[0].size(), strands[0].size());
  }
  else {
    // collect the total number of instructions that are to be analyzed
    int max_timesteps = 0;
    for ( auto const& strand: strands ) {
      total += strand.size();
      if ( max_timesteps < strand.size() )
        max_timesteps = strand.size();
    }

    for ( int i = 0; i < max_timesteps; ++i ) {
      std::vector< int > pc_list;
      for ( int i = 0; i < ncores; ++i ) {
        if ( !strands[i].empty() ) {
          pc_list.push_back( strands[i].front() );
          strands[i].pop_front();
        }
      }
      auto new_end = std::unique(pc_list.begin(), pc_list.end());
      pc_list.erase( new_end, pc_list.end() );
      unique += pc_list.size();
    }
    return std::make_tuple(unique, total);
  }
}


//-------------------------------------------------------------------------
// min_pc()
//-------------------------------------------------------------------------
// Given a vector of strands where each entry is a deque of pcs
// that correspond to the execution trace, the function returns a tuple
// of the unique instructions seen and the total number of instructions
// using the min_pc based reconvergence heuristic

std::tuple< int,int > min_pc( std::vector< std::deque<int> >& strands )
{
  int unique = 0;
  int total  = 0;
  int ncores = strands.size();

  if ( ncores == 1 ) {
    return std::make_tuple(strands[0].size(), strands[0].size());
  }
  else {
    // collect the total number of instructions that are to be analyzed
    for ( auto const& strand: strands ) {
      total += strand.size();
    }

    bool all_done = false;
    std::vector< bool > done( ncores, false );

    // min-pc based reconvergence loop
    while ( !all_done ) {

      std::vector< int > pc_list;
      for ( int i = 0; i < ncores; ++i ) {
        if ( !strands[i].empty() ) {
          pc_list.push_back( strands[i].front() );
        }
        else {
          pc_list.push_back( std::numeric_limits< int >::max() );
          done[i] = true;
        }
      }

      int min_pc = *std::min_element( pc_list.begin(), pc_list.end() );
      if ( min_pc == std::numeric_limits< int >::max() ) {
        break;
      }

      for ( int i = 0; i < ncores; ++i ) {
        if ( !done[i] && ( strands[i].front() == min_pc ) ) {
          strands[i].pop_front();
        }
      }

      unique = unique + 1;

      all_done = true;
      for ( int i = 0; i < ncores; ++i ) {
        all_done =  all_done & done[i];
      }

    }
    return std::make_tuple(unique, total);
  }
}

//-------------------------------------------------------------------------
// main()
//-------------------------------------------------------------------------

int main ( int argc, char* argv[] )
{
  try {

    // Command line processing
    cxxopts::Options options( argv[0], " - Options for trace analysis" );

    options.positional_help( "trace outdir" );
    options.add_options()
      ( "h, help", "Print help" )
      ( "trace", "Trace file <trace.csv>", cxxopts::value<std::string>() )
      ( "outdir", "Output directory", cxxopts::value<std::string>() )
      ;

    const std::vector< std::string > positional_args = { "trace", "outdir" };
    options.parse_positional( positional_args );
    options.parse( argc, argv );

    if ( options.count( "help" ) || options.count( "trace" ) == 0 ||
         options.count( "outdir" ) == 0 ) {
      std::cout << options.help() << std::endl;
      return 0;
    }


    std::string tracefile = options["trace"].as< std::string >();
    std::string outdir    = options["outdir"].as< std::string >();

    // Open the trace file
    io::CSVReader<4> in( tracefile.c_str() );
    in.read_header( io::ignore_extra_column, "pid", "cid", "pc", "ret_cnt" );

    std::string pid, cid, pc, ret_cnt;
    std::vector< int >   pregions;
    std::vector< int >   num_cores;
    std::vector< Entry > trace;

    // Read the input tracefile
    while( in.read_row( pid, cid, pc, ret_cnt ) ) {
      // Collect unique parallel regions
      if ( std::find( pregions.begin(), pregions.end(), std::stoi( pid, 0, 16 ) )
            == pregions.end() ) {
        pregions.push_back( std::stoi( pid, 0, 16 ) );
      }

      // Collect unique cores seen
      if ( std::find( num_cores.begin(), num_cores.end(), std::stoi( cid, 0, 16 ) )
            == num_cores.end() ) {
        num_cores.push_back( std::stoi( cid, 0, 16 ) );
      }

      // Collect the trace
      trace.push_back(
        Entry(
        std::stoi( pid,     0, 16 ),
        std::stoi( cid,     0, 16 ),
        std::stoi( pc,      0, 16 ),
        std::stoi( ret_cnt, 0, 16 )
        )
      );
    }

    // Stats
    int g_unique_insts = 0;
    int g_total_insts  = 0;
    int g_ncores       = num_cores.size();

    std::ofstream out;
    out.open( ( outdir + "/trace-analysis.txt" ).c_str() );

    // Loop through for each parallel region
    for ( auto const& region: pregions ) {
      // Data-structure for the strands in a given parallel region
      std::vector< std::deque< int > > strands( g_ncores );
      for ( int core = 0; core < g_ncores; ++core ) {
        for ( auto const& entry: trace ) {
          if ( entry.pid == region && entry.cid == core ) {
            strands[core].push_back( entry.pc );
          }
        }
      }

      // analyze strands in the region
      auto res = max_share( strands );
      //auto res = min_pc( strands );

      int unique_insts = std::get<0>( res );
      int total_insts  = std::get<1>( res );

      out << "Parallel region " << region << ":" << std::endl;
      out << "  unique    insts: " << unique_insts << std::endl;
      out << "  total     insts: " << total_insts << std::endl;
      out << "  redundant insts: " << ( total_insts - unique_insts ) << std::endl;
      out << "  savings: " << (static_cast<float>( total_insts - unique_insts )/( total_insts ) )*100 << "%" << std::endl;

      g_unique_insts += unique_insts;
      g_total_insts  += total_insts;
    }

    out << "Overall stats\n";
    out << "  unique    insts: " << g_unique_insts << std::endl;
    out << "  total     insts: " << g_total_insts << std::endl;
    out << "  redundant insts: " << ( g_total_insts - g_unique_insts ) << std::endl;
    out << "  savings: " << (static_cast<float>( g_total_insts - g_unique_insts )/( g_total_insts ) )*100 << "%" << std::endl;

  }
  catch ( const cxxopts::OptionException& e ) {
    std::cout << "error parsing options: " << e.what() << std::endl;
    exit( 1 );
  }

  return 0;
}
