//=========================================================================
// task-trace-analyze.cc
//=========================================================================
// Author : Shreesha Srinath
// Date   : October 9th, 2017
//
// Program reads the csv dump files from pydgin and reports the trace
// analysis for a given divergence mechanism for the a given
// series-parallel DAG program.
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

#include <boost/graph/graph_traits.hpp>
#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/adjacency_iterator.hpp>

//-------------------------------------------------------------------------
// Global typedefs and constants
//-------------------------------------------------------------------------

typedef boost::adjacency_list<boost::vecS, boost::vecS, boost::bidirectionalS> Graph;
typedef boost::graph_traits< Graph >::vertex_descriptor Vertex_t;
typedef boost::graph_traits< Graph >::edge_descriptor Edge_t;

int g_num_contexts[] = { 8 };

//-------------------------------------------------------------------------
// dump_stats()
//-------------------------------------------------------------------------

void dump_stats( std::ostream& out, const int& unique_insts,
                 const int& total_insts, const int& steps, const int& region,
                 bool summary = false )
{
  if ( summary ) {
    out << "Overall stats:" << std::endl;
  } else {
    out << "Parallel region " << region << ":" << std::endl;
  }

  out << "  unique    insts: " << unique_insts << std::endl;
  out << "  total     insts: " << total_insts << std::endl;
  out << "  redundant insts: " << ( total_insts - unique_insts ) << std::endl;
  out << "          savings: " << (static_cast<float>( total_insts - unique_insts )/( total_insts ) )*100 << "%" << std::endl;
  out << "  total     steps: " << steps << std::endl;
  out << std::endl;
}

//-------------------------------------------------------------------------
// print_schedule
//-------------------------------------------------------------------------

void print_schedule( const std::map< int, std::vector<int> >& schedule ) {
  for ( auto& kv: schedule ) {
    std::cout << "Level: " << kv.first << "; nodes: [";
    for ( auto& node: kv.second ) {
      std::cout << node << ",";
    }
    std::cout << "]" << std::endl;
  }
}

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
// asap_schedule()
//-------------------------------------------------------------------------

std::map< int, std::vector< int > > asap_schedule( Graph& g ) {

  int num_nodes = boost::num_vertices( g );

  std::vector< int > asap_labels( num_nodes, 0 );

  // Assign the source node a timestep 1
  asap_labels[0] = 1;

  auto nodes = boost::vertices( g );
  for ( auto node = nodes.first; node != nodes.second; ++node ) {
    if ( asap_labels[*node] == 0 ) {
      int label = 0;
      // find the max of parent labels
      auto parents = boost::in_edges( *node, g );
      for ( auto p = parents.first; p != parents.second; ++ p ) {
        int parent = boost::source( *p, g );
        if ( asap_labels[ parent ] > label ) {
          label = asap_labels[ parent ];
        }
      }
      // assign label to the current node
      asap_labels[*node] = label + 1;
    }
  }

  // create schedule
  std::map< int, std::vector< int > > schedule;
  for ( auto node = nodes.first; node != nodes.second; ++node ) {
    schedule[ asap_labels[*node] ].push_back( *node );
  }

  return schedule;
}

//-------------------------------------------------------------------------
// bounded_greedy_schedule()
//-------------------------------------------------------------------------

std::map< int, std::vector< int > > bounded_greedy_schedule( Graph& g, const int& num_contexts ) {

  auto ubounded_schedule = asap_schedule( g );

  int num_nodes = boost::num_vertices( g );

  std::vector< int > greedy_labels( num_nodes, 0 );

  int label = 1;

  for ( auto& kv: ubounded_schedule ) {
    auto num_nodes = kv.second.size();
    auto nodes = kv.second;
    int start_idx = 0;
    do {

      int end_idx = ( ( start_idx + num_contexts ) < num_nodes )
                    ? ( start_idx + num_contexts ) : num_nodes;

      for ( int i = start_idx; i < end_idx; ++i ) {
        greedy_labels[ nodes[i] ] = label;
      }

      start_idx += num_contexts;
      label += 1;

    } while ( start_idx < num_nodes );
  }

  // create schedule
  std::map< int, std::vector< int > > schedule;
  auto nodes = boost::vertices( g );
  for ( auto node = nodes.first; node != nodes.second; ++node ) {
    schedule[ greedy_labels[*node] ].push_back( *node );
  }

  return schedule;
}

//-------------------------------------------------------------------------
// max_share()
//-------------------------------------------------------------------------
// Given a vector of strands where each entry is a deque of pcs
// that correspond to the execution trace, the function returns a tuple
// of the unique instructions seen and the total number of instructions
// using no reconvergence

std::tuple< int,int,int > max_share( std::vector< std::deque< TraceEntry > > strands )
{
  int unique   = 0;
  int total    = 0;
  int nstrands = strands.size();

  if ( nstrands == 1 ) {
    return std::make_tuple( strands[0].size(), strands[0].size(), strands[0].size() );
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
      std::vector< int > unique_pc_list;
      for ( int i = 0; i < nstrands; ++i ) {
        if ( !strands[i].empty() ) {
          pc_list.push_back( strands[i].front().pc );
          strands[i].pop_front();
        }
      }
      for ( auto pc: pc_list ) {
        if ( std::find( unique_pc_list.begin(), unique_pc_list.end(), pc )
             == unique_pc_list.end() ) {
          unique_pc_list.push_back( pc );
        }
      }
      unique += unique_pc_list.size();
    }
    return std::make_tuple( unique, total, max_timesteps );
  }
}

//-------------------------------------------------------------------------
// min_pc()
//-------------------------------------------------------------------------
// Given a vector of strands where each entry is a deque of pcs
// that correspond to the execution trace, the function returns a tuple
// of the unique instructions seen and the total number of instructions
// using the min_pc based reconvergence heuristic

std::tuple< int,int,int > min_pc( std::vector< std::deque< TraceEntry > > strands )
{
  int unique = 0;
  int total  = 0;
  int nstrands = strands.size();

  if ( nstrands == 1 ) {
    return std::make_tuple( strands[0].size(), strands[0].size(), strands[0].size() );
  }
  else {
    // collect the total number of instructions that are to be analyzed
    for ( auto const& strand: strands ) {
      total += strand.size();
    }

    bool all_done = false;
    std::vector< bool > done( nstrands, false );

    // min-pc based reconvergence loop
    int max_timesteps = 0;
    while ( !all_done ) {

      std::vector< int > pc_list;
      for ( int i = 0; i < nstrands; ++i ) {
        if ( !strands[i].empty() ) {
          pc_list.push_back( strands[i].front().pc );
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

      for ( int i = 0; i < nstrands; ++i ) {
        if ( !done[i] && ( strands[i].front().pc == min_pc ) ) {
          strands[i].pop_front();
        }
      }

      unique += 1;
      max_timesteps += 1;

      all_done = true;
      for ( int i = 0; i < nstrands; ++i ) {
        all_done =  all_done & done[i];
      }

    }
    return std::make_tuple(unique, total, max_timesteps);
  }
}

//------------------------------------------------------------------------
// loop_analysis()
//------------------------------------------------------------------------

void
loop_analysis( std::vector< std::deque< TraceEntry > > strands,
               std::vector< std::vector< std::tuple< int,int,int > > >& per_region_stats,
               const int& num_contexts,
               int index ) {

  int start_idx    = 0;
  std::vector< int > unique_insts( 2, 0);
  std::vector< int > total_insts( 2, 0 );
  std::vector< int > total_steps( 2, 0 );

  do {

    int end_idx = ( ( start_idx + num_contexts ) < strands.size() )
                  ? ( start_idx + num_contexts ) : strands.size();

    std::vector< std::deque< TraceEntry > > bstrands( &strands[start_idx], &strands[end_idx] );

    auto res0 = max_share( bstrands );
    unique_insts[0] += std::get<0>( res0 );
    total_insts[0]  += std::get<1>( res0 );
    total_steps[0]  += std::get<2>( res0 );

    auto res1 = min_pc( bstrands );
    unique_insts[1] += std::get<0>( res1 );
    total_insts[1]  += std::get<1>( res1 );
    total_steps[1]  += std::get<2>( res1 );

    start_idx += num_contexts;

  } while ( start_idx < strands.size() );

  per_region_stats[index].push_back( std::make_tuple( unique_insts[0], total_insts[0], total_steps[0] ) );
  per_region_stats[index+1].push_back( std::make_tuple( unique_insts[1], total_insts[1], total_steps[1] ) );

}

//------------------------------------------------------------------------
// task_analysis()
//------------------------------------------------------------------------

void
task_analysis( std::map< int, std::vector< int > > schedule,
               std::vector< TraceEntry > ptrace,
               std::vector< std::vector< std::tuple< int,int,int > > >& per_region_stats,
               int index ) {

  std::vector< int > unique_insts( 2, 0);
  std::vector< int > total_insts( 2, 0 );
  std::vector< int > total_steps( 2, 0 );

  for ( auto const& kv: schedule ) {
    int num_tasks = kv.second.size();
    std::vector< std::deque< TraceEntry > > strands( num_tasks );
    int i = 0;
    for ( auto const& node: kv.second ) {
      for ( auto const& entry: ptrace ) {
        if ( entry.tid == node ) {
          strands[i].push_back( entry );
        }
      }
      ++i;
    }
    auto res0 = max_share( strands );
    unique_insts[0] += std::get<0>( res0 );
    total_insts[0]  += std::get<1>( res0 );
    total_steps[0]  += std::get<2>( res0 );

    auto res1 = min_pc( strands );
    unique_insts[1] += std::get<0>( res1 );
    total_insts[1]  += std::get<1>( res1 );
    total_steps[1]  += std::get<2>( res1 );
  }

  per_region_stats[index].push_back( std::make_tuple( unique_insts[0], total_insts[0], total_steps[0] ) );
  per_region_stats[index+1].push_back( std::make_tuple( unique_insts[1], total_insts[1], total_steps[1] ) );

}

//------------------------------------------------------------------------
// compact_loop_analysis
//------------------------------------------------------------------------

void compact_loop_analysis(
  std::vector< std::deque< TraceEntry > >& strands,
  std::vector< std::vector< std::tuple< int,int,int > > >& per_region_stats,
  int num_contexts,
  int index )
{

  // all cores are initially available
  std::vector< bool > core_active( num_contexts, false );

  // per-core trace
  std::vector< std::deque< TraceEntry > > core_trace( num_contexts );

  int timestep = 0;
  int total    = 0;
  int unique   = 0;
  int iter     = 0;
  bool active  = false;

  while ( ( iter < strands.size() ) || active ) {
    // if a core is available assign an available strand to it
    for ( int i = 0; i < num_contexts; ++i ) {
      if ( !core_active[i] && ( iter < strands.size() ) ) {
        core_active[i] = true;
        // extract the trace for the core
        assert( core_trace[i].empty() );
        for ( auto it = strands[iter].begin(); it != strands[iter].end(); ++it ) {
          core_trace[i].push_back( *it );
        }
        total += core_trace[i].size();
        iter += 1;
      }
    }

    // process stuff in flight
    std::vector< int > pc_list;
    std::vector< int > unique_pc_list;
    for ( int i = 0; i < num_contexts; ++i ) {
      if ( !core_trace[i].empty() && core_active[i] ) {
        pc_list.push_back( core_trace[i].front().pc );
        core_trace[i].pop_front();
      }
    }

    // calculate redundancy
    for ( auto pc: pc_list ) {
      if ( std::find( unique_pc_list.begin(), unique_pc_list.end(), pc )
           == unique_pc_list.end() ) {
        unique_pc_list.push_back( pc );
      }
    }
    unique += unique_pc_list.size();

    // check if any traces have finished
    active = false;
    for ( int i = 0; i < num_contexts; ++i ) {
      // finished the current node, schedule child if possible
      if ( core_trace[i].empty() && core_active[i] ) {
        core_active[i] = false;
      }
      active = active | core_active[i];
    }

    // advance time
    timestep += 1;
  }

  per_region_stats[index].push_back( std::make_tuple( unique, total, timestep ) );

}

//------------------------------------------------------------------------
// compact_task_analysis
//------------------------------------------------------------------------

void compact_task_analysis(
  Graph& g,
  std::vector< TraceEntry >& ptrace,
  std::vector< std::vector< std::tuple< int,int,int > > >& per_region_stats,
  int num_contexts,
  int index )
{

  // initialze a node map
  auto nodes = boost::vertices( g );
  std::map< int,int > node_map;
  for ( auto node = nodes.first; node != nodes.second; ++node ) {
    auto in_degree = boost::in_degree( *node, g );
    node_map[ *node ] = in_degree;
  }

  // all cores are initially available
  std::vector< bool > core_active( num_contexts, false );

  // queue of active nodes
  std::deque< Vertex_t > active_nodes;

  // per-core trace
  std::vector< std::deque< TraceEntry > > core_trace( num_contexts );
  std::vector< int >                      core_node( num_contexts );

  // schedule the root node
  active_nodes.push_back( *boost::vertices( g ).first );

  int timestep = 0;
  int total    = 0;
  int unique   = 0;
  bool active  = false;
  while ( !active_nodes.empty() || active ) {
    // if a core is available assign any ready node to it
    for ( int i = 0; i < num_contexts; ++i ) {
      if ( !core_active[i] && !active_nodes.empty() ) {
        auto node = active_nodes.front();
        active_nodes.pop_front();
        core_active[i] = true;
        core_node[i] = node;
        // extract the trace for the core
        assert( core_trace[i].empty() );
        for ( auto entry: ptrace ) {
          if ( entry.tid == node ) {
            core_trace[i].push_back( entry );
          }
        }
        total += core_trace[i].size();
      }
    }

    // process stuff in flight
    std::vector< int > pc_list;
    std::vector< int > unique_pc_list;
    for ( int i = 0; i < num_contexts; ++i ) {
      if ( !core_trace[i].empty() && core_active[i] ) {
        pc_list.push_back( core_trace[i].front().pc );
        core_trace[i].pop_front();
      }
    }

    // calculate redundancy
    for ( auto pc: pc_list ) {
      if ( std::find( unique_pc_list.begin(), unique_pc_list.end(), pc )
           == unique_pc_list.end() ) {
        unique_pc_list.push_back( pc );
      }
    }
    unique += unique_pc_list.size();

    // check if any traces have finished
    active = false;
    for ( int i = 0; i < num_contexts; ++i ) {
      // finished the current node, schedule child if possible
      if ( core_trace[i].empty() && core_active[i] ) {
        core_active[i] = false;
        auto node = core_node[i];
        auto children = boost::out_edges( node, g );
        for ( auto c = children.first; c != children.second; ++c ) {
          auto child = boost::target( *c, g );
          node_map[child] -= 1;
          assert( node_map[child] >= 0 );
          if ( node_map[child] == 0 ) {
            active_nodes.push_back( child );
          }
        }
      }
      active = active | core_active[i];
    }

    // advance time
    timestep += 1;
  }

  per_region_stats[index].push_back( std::make_tuple( unique, total, timestep-2 ) );

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

    // Stats
    std::vector< std::vector< std::tuple< int,int,int > > > per_region_stats( 3 );

    std::ofstream out;
    out.open( ( outdir + "/trace-analysis.txt" ).c_str() );

    // Loop through for each parallel region
    for ( auto const& region: pregions ) {

      // Collect the trace entries in a given parallel region
      std::vector< TraceEntry > ptrace;
      std::vector< int >        strand_ids;
      for ( auto const& entry: trace ) {
        if ( entry.pid == region ) {
          // Collect unique strand ids
          if ( std::find( strand_ids.begin(), strand_ids.end(), entry.tid )
               == strand_ids.end() ) {
            strand_ids.push_back( entry.tid );
          }
          ptrace.push_back( entry );
        }
      }

      // Data-parallel region
      if ( ptrace[0].ptype == 1 ) {

        // Data-structure to store strands
        std::vector< std::deque< TraceEntry > > strands( strand_ids.size() );

        // Collect the strands
        int tid = 0;
        for ( auto const& id: strand_ids ) {
          for ( auto const& entry: ptrace ) {
            if ( id == entry.tid ) {
              strands[tid].push_back( entry );
            }
          }
          ++tid;
        }

        //-----------------------------------------------------------------
        // Unbounded analysis
        //-----------------------------------------------------------------
        // FIXME: NOTE: 10/25/2107
        // Turning off unbounded analysis

        //auto res0 = max_share( strands );
        //per_region_stats[0].push_back( res0 );

        //auto res1 = min_pc( strands );
        //per_region_stats[1].push_back( res1 );

        //-----------------------------------------------------------------
        // Compact analysis
        //-----------------------------------------------------------------

        compact_loop_analysis( strands, per_region_stats, g_num_contexts[0], 0 );

        //-----------------------------------------------------------------
        // Bounded analysis
        //-----------------------------------------------------------------

        loop_analysis( strands, per_region_stats, g_num_contexts[0], 1 );

      }
      // Task-parallel region
      else {

        Graph tg( strand_ids.size() );
        for ( auto const& entry: graph ) {
          if ( entry.pid == region ) {
            boost::add_edge( entry.parent, entry.child, tg );
          }
        }

        //-----------------------------------------------------------------
        // Unbounded analysis
        //-----------------------------------------------------------------
        // FIXME: NOTE: 10/25/2107
        // Turning off unbounded analysis

        //auto unbounded_schedule = asap_schedule( tg );
        //task_analysis( unbounded_schedule, ptrace, per_region_stats, 0 );

        //-----------------------------------------------------------------
        // Compact analysis
        //-----------------------------------------------------------------

        compact_task_analysis( tg, ptrace, per_region_stats, g_num_contexts[0], 0 );

        //-----------------------------------------------------------------
        // Bounded analysis
        //-----------------------------------------------------------------

        auto bounded_schedule = bounded_greedy_schedule( tg, g_num_contexts[0] );
        task_analysis( bounded_schedule, ptrace, per_region_stats, 1 );

      }
    }

    for ( int i = 0; i < per_region_stats.size(); ++i ) {
      out << "//" << std::string( 72, '-' ) << std::endl;
      if      ( i == 0 ) { out << "// Compact-8 results " << std::endl; }
      else if ( i == 1 ) { out << "// Bounded-8 max-share results " << std::endl; }
      else if ( i == 2 ) { out << "// Bounded-8 min-pc results " << std::endl; }
      out << "//" << std::string( 72, '-' ) << std::endl << std::endl;

      int g_unique_insts = 0;
      int g_total_insts  = 0;
      int g_total_steps  = 0;

      for ( int region = 0; region < pregions.size(); ++region ) {

        int unique_insts = std::get<0>( per_region_stats[i][region] );
        int total_insts  = std::get<1>( per_region_stats[i][region] );
        int total_steps  = std::get<2>( per_region_stats[i][region] );

        g_unique_insts += unique_insts;
        g_total_insts  += total_insts;
        g_total_steps  += total_steps;

        dump_stats( out, unique_insts, total_insts, total_steps, region+1 );
      }

      dump_stats( out, g_unique_insts, g_total_insts, g_total_steps, 0, true );
    }

    out.close();
  }
  catch ( const cxxopts::OptionException& e ) {
    std::cout << "error parsing options: " << e.what() << std::endl;
    exit( 1 );
  }

  return 0;
}
