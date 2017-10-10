//=========================================================================
// task-graph.cc
//=========================================================================
// Author : Shreesha Srinath
// Date   : October 10th, 2017
//
// Program reads the csv dump files from pydgin and reports plots the
// series-parallel DAG
//
// NOTE: I found this useful C++11-based CSV header library which is used
// for parsing the csv trace dumps.
//
//   https://github.com/ben-strasser/fast-cpp-csv-parser
//

#include "csv.h"
#include "cxxopts.hpp"

#include <algorithm>
#include <fstream>
#include <iostream>
#include <map>
#include <string>
#include <vector>

#include <boost/graph/graph_traits.hpp>
#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/adjacency_iterator.hpp>

//-------------------------------------------------------------------------
// Global typedefs and constants
//-------------------------------------------------------------------------

typedef boost::adjacency_list<boost::vecS, boost::vecS, boost::bidirectionalS> Graph;
typedef boost::graph_traits< Graph >::vertex_descriptor Vertex_t;
typedef boost::graph_traits< Graph >::edge_descriptor Edge_t;

//-------------------------------------------------------------------------
// g_node_attributes
//-------------------------------------------------------------------------

std::vector< std::string > g_node_attributes = {
  "[fillcolor=\"#f7f7f7\",style=\"filled\"]",
  "[fillcolor=\"#998ec3\",style=\"filled\"]",
};

//-------------------------------------------------------------------------
// TraceEntry
//-------------------------------------------------------------------------
// Struct to represent an entry in the trace csv file

struct TraceEntry {
  int pid;
  int ptype;
  int tid;
  int pc;
  int stype;

  TraceEntry( int pid, int ptype, int tid, int pc, int stype )
    : pid( pid ), ptype( ptype ), tid( tid ), pc( pc ), stype( stype )
  { }
};

// Helper function to print the struct
std::ostream& operator<< ( std::ostream& o, const TraceEntry& e )
{
  o << std::hex << "[" << e.pid << "," << e.ptype << "," << e.tid << ","
    << e.pc << "," << e.stype << "]" << std::endl;
  return o;
}

//-------------------------------------------------------------------------
// GraphEntry
//-------------------------------------------------------------------------
// Struct to represent an entry in the graph csv file

struct GraphEntry {
  int pid;
  int parent;
  int child;

  GraphEntry( int pid, int parent, int child )
    : pid( pid ), parent( parent ), child( child )
  { }
};

// Helper function to print the struct
std::ostream& operator<< ( std::ostream& o, const GraphEntry& e )
{
  o << "[" << e.pid << "," << e.parent << "," << e.child << "]" << std::endl;
  return o;
}

//-------------------------------------------------------------------------
// main()
//-------------------------------------------------------------------------

int main ( int argc, char* argv[] )
{
  try {

    //---------------------------------------------------------------------
    // Command line processing
    //---------------------------------------------------------------------

    cxxopts::Options options( argv[0], " - Options for trace analysis" );

    options.positional_help( "trace graph outdir" );
    options.add_options()
      ( "h, help", "Print help" )
      ( "trace", "Trace file <trace.csv>", cxxopts::value<std::string>() )
      ( "graph", "Graph file <graph.csv>", cxxopts::value<std::string>() )
      ( "outdir", "Output directory", cxxopts::value<std::string>() )
      ;

    const std::vector< std::string > positional_args = { "trace", "graph", "outdir" };
    options.parse_positional( positional_args );
    options.parse( argc, argv );

    if ( options.count( "help" ) || options.count( "trace" ) == 0 ||
         options.count( "graph" ) == 0 || options.count( "outdir" ) == 0 ) {
      std::cout << options.help() << std::endl;
      return 0;
    }

    std::string tracefile = options["trace"].as< std::string >();
    std::string graphfile = options["graph"].as< std::string >();
    std::string outdir    = options["outdir"].as< std::string >();

    //---------------------------------------------------------------------
    // Read the input tracefile
    //---------------------------------------------------------------------

    // Open the trace file
    io::CSVReader<5> in_trace( tracefile.c_str() );
    in_trace.read_header( io::ignore_extra_column, "pid", "ptype", "tid", "pc", "stype" );

    std::string pid, ptype, tid, pc, stype;
    std::vector< int >   pregions;
    std::vector< TraceEntry > trace;

    while ( in_trace.read_row( pid, ptype, tid, pc, stype ) ) {
      // Collect unique parallel regions
      if ( std::find( pregions.begin(), pregions.end(), std::stoi( pid, 0, 16 ) )
            == pregions.end() ) {
        pregions.push_back( std::stoi( pid, 0, 16 ) );
      }

      // Collect the trace
      trace.push_back(
        TraceEntry(
          std::stoi( pid,     0, 16 ),
          std::stoi( ptype,   0, 16 ),
          std::stoi( tid,     0, 16 ),
          std::stoi( pc,      0, 16 ),
          std::stoi( stype,   0, 16 )
        )
      );
    }

    //---------------------------------------------------------------------
    // Read the input graphfile
    //---------------------------------------------------------------------

    io::CSVReader<3> in_graph( graphfile.c_str() );
    in_graph.read_header( io::ignore_extra_column, "pid", "parent", "child" );

    std::string parent, child;
    std::vector< GraphEntry > graph;

    while ( in_graph.read_row( pid, parent, child ) ) {
      graph.push_back(
        // NOTE: In pydgin/sim.py I dump the task graph as an int
        GraphEntry(
          std::stoi( pid,    0 ),
          std::stoi( parent, 0 ),
          std::stoi( child,  0 )
        )
      );
    }

    //---------------------------------------------------------------------
    // Analysis
    //---------------------------------------------------------------------

    // Loop through for each parallel region
    for ( auto const& region: pregions ) {

      // Collect the trace entries in a given parallel region
      std::vector< TraceEntry > ptrace;
      std::map< int, int >      strand_type;
      for ( auto const& entry: trace ) {
        if ( entry.pid == region ) {
          strand_type[entry.tid] = entry.stype;
          ptrace.push_back( entry );
        }
      }

      // Data-parallel region
      if ( ptrace[0].ptype == 1 ) {
        continue;
      }
      // Task-parallel region
      else {
        std::ofstream out;
        out.open( ( outdir + "/graph-" + std::to_string( region ) + ".dot" ).c_str() );
        out << "digraph G{" << std::endl;

        Graph tg;
        for ( auto const& entry: graph ) {
          if ( entry.pid == region ) {
            boost::add_edge( entry.parent, entry.child, tg );
          }
        }

        auto nodes = boost::vertices( tg );
        for ( auto node = nodes.first; node != nodes.second; ++node ) {
          auto children = boost::out_edges( *node, tg );
          for ( auto c = children.first; c != children.second; ++c ) {
            int child = boost::target( *c, tg );
            out << "  " << *node << "->" << child << ";" << std::endl;
          }
          out << "  " << *node << "  " << g_node_attributes[ strand_type[*node] ] <<  std::endl;
        }

        out << "}" << std::endl;
        out.close();
      }
    }
  }
  catch ( const cxxopts::OptionException& e ) {
    std::cout << "error parsing options: " << e.what() << std::endl;
    exit( 1 );
  }

  return 0;
}
