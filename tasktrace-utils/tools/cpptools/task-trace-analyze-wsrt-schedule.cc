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
#include <cstdlib>
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
#include <type_traits>
#include <typeinfo>

//-------------------------------------------------------------------------
// Global typedefs and constants
//-------------------------------------------------------------------------

typedef boost::adjacency_list<boost::vecS, boost::vecS, boost::bidirectionalS> Graph;
typedef boost::graph_traits< Graph >::vertex_descriptor Vertex_t;
typedef boost::graph_traits< Graph >::edge_descriptor Edge_t;
typedef boost::graph_traits< Graph >::vertex_iterator VertexIter;

int g_num_contexts[] = { 4, 8 };

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
// utility functions for ws-scheduling
//-------------------------------------------------------------------------

struct Task{
  int       core_id;
  int       stack_idx;
  Vertex_t  task_id;

  Task()
  { }

  Task( int core_id, int stack_idx, Vertex_t task_id )
    : core_id( core_id ), stack_idx( stack_idx ), task_id( task_id )
  { }

  void operator=( Task other )
  {
    core_id   = other.core_id;
    stack_idx = other.stack_idx;
    task_id   = other.task_id;
  }
};

struct StackEntry {
  int  join_counter;
  Task continuation;

  StackEntry( int join_counter, Task continuation )
    : join_counter( join_counter ), continuation( continuation )
  { }

  void operator=( StackEntry other )
  {
    join_counter = other.join_counter;
    continuation = other.continuation;
  }
};

typedef std::vector< std::deque< Task > > TaskQueue;


int random_victim( int id, int num_contexts ) {
  int ret = 0;
  do {
    ret = ( rand() % num_contexts );
  } while ( ret != id );
  return ret;
}

int occupancy_based_victim( TaskQueue& task_queue, int id, int num_contexts ) {
  int ret        = -1;
  int max_ntasks = 0;
  for( int i = 0; i < num_contexts; ++i ) {
    if( i != id ) {
      if( task_queue[i].size() > max_ntasks ) {
        max_ntasks = task_queue[i].size();
        ret = i;
      }
    }
  }
  if ( ret == -1 ) {
    return random_victim( id, num_contexts );
  }
  else {
    return ret;
  }
}

//-------------------------------------------------------------------------
// ws_schedule()
//-------------------------------------------------------------------------

void ws_schedule(
  Graph& g,
  std::vector< TraceEntry >& ptrace,
  int num_contexts,
  std::vector< std::vector< std::tuple< int,int,int > > >& per_region_stats,
  int index,
  bool linetrace = false
)
{

  std::map< Vertex_t, int > node_type;
  for ( auto entry: ptrace ) {
    node_type[entry.tid] = entry.stype;
  }
  // sink node is special
  auto num_nodes = boost::num_vertices( g );
  node_type[ num_nodes-1 ] = 1;

  // all cores are initially available
  std::vector< bool > core_active( num_contexts, false );

  // per-core data-structures
  TaskQueue task_queue( num_contexts );
  std::vector< std::deque< TraceEntry > > core_trace( num_contexts );
  std::vector< std::vector< StackEntry > > core_stack( num_contexts );

  // linetrace
  std::vector< Task > curr_task( num_contexts );

  // schedule the root node
  auto root = *boost::vertices( g ).first;
  auto out_degree = boost::out_degree( root, g );
  task_queue[0].push_back( Task( 0, -1, root ) );

  int timesteps = 0;
  int total     = 0;
  int unique    = 0;

  bool queues_empty = false;
  bool stacks_empty = false;
  bool active       = true;

  while ( !queues_empty || !stacks_empty ||  active ) {

    // If a core is idle and is waiting for it's children to return, check
    // if the children are all done and execute the continuation
    for ( int i = 0; i < num_contexts; ++i ) {
      if ( !core_stack[i].empty() && !core_active[i] ) {
        auto stack = core_stack[i].back();
        if ( stack.join_counter == 0 ) {
          core_stack[i].pop_back();
          core_active[i] = true;
          curr_task[i] = stack.continuation;
          assert( stack.continuation.task_id != -1 );
          assert( node_type[stack.continuation.task_id] == 1 );
          // extract the trace for the core
          assert( core_trace[i].empty() );
          for ( auto entry: ptrace ) {
            if ( entry.tid == stack.continuation.task_id ) {
              core_trace[i].push_back( entry );
            }
          }
          total += core_trace[i].size();
        }
      }
    }

    // If a core is idle and has an item in it's task_queue, pop it and
    // assign it to the core for execution.
    for ( int i = 0; i < num_contexts; ++i ) {
      if ( !task_queue[i].empty() && !core_active[i] ) {
        auto task = task_queue[i].back();
        task_queue[i].pop_back();
        auto out_degee = boost::out_degree( task.task_id, g );
        core_active[i] = true;
        curr_task[i] = task;
        // extract the trace for the core
        assert( core_trace[i].empty() );
        for ( auto entry: ptrace ) {
          if ( entry.tid == task.task_id ) {
            core_trace[i].push_back( entry );
          }
        }
        total += core_trace[i].size();
      }
    }

    // If a core is idle and has no work, steal from another core
    for ( int i = 0; i < num_contexts; ++i ) {
      if ( task_queue[i].empty() && !core_active[i] ) {
        // select a victim
        int victim = occupancy_based_victim( task_queue, i, num_contexts );
        if ( !task_queue[victim].empty() ) {
          auto task = task_queue[victim].front();
          task_queue[victim].pop_front();
          core_active[i] = true;
          curr_task[i] = task;
          // extract the trace for the core
          assert( core_trace[i].empty() );
          for ( auto entry: ptrace ) {
            if ( entry.tid == task.task_id ) {
              core_trace[i].push_back( entry );
            }
          }
          total += core_trace[i].size();
        }
      }
    }

    // Process active cores
    std::vector< int > pc_list;
    std::vector< int > unique_pc_list;
    for ( int i = 0; i < num_contexts; ++i ) {
      if ( !core_trace[i].empty() && core_active[i] ) {
        pc_list.push_back( core_trace[i].front().pc );
        core_trace[i].pop_front();
      }
    }

    // Calculate redundancy
    for ( auto pc: pc_list ) {
      if ( std::find( unique_pc_list.begin(), unique_pc_list.end(), pc )
           == unique_pc_list.end() ) {
        unique_pc_list.push_back( pc );
      }
    }
    unique += unique_pc_list.size();

    // Print linetrace
    if ( linetrace ) {
      for ( int i = 0; i < num_contexts; ++i ) {
        if ( core_active[i] ) {
          std::cout << curr_task[i].task_id << " | ";
        }
        else {
          std::cout << " # | ";
        }
      }
      std::cout << std::endl;
    }

    // Check if any traces have finished
    active = false;
    queues_empty = true;
    stacks_empty = true;
    for ( int i = 0; i < num_contexts; ++i ) {
      // finished the current node, schedule child if possible
      if ( core_trace[i].empty() && core_active[i] ) {
        core_active[i] = false;
        auto task = curr_task[i];
        int join_counter = 0;
        if ( boost::out_degree( task.task_id, g ) ) {
          auto children = boost::out_edges( task.task_id, g );

          // check to see if spawning a task
          for ( auto c = children.first; c != children.second; ++c ) {
            auto child = boost::target( *c, g );
            if ( node_type[child] == 0 ) {
              join_counter += 1;
            }
          }

          // if children spawn, create a stack entry and push children to
          // task queue
          if ( join_counter != 0 ) {
            core_stack[i].push_back( StackEntry( join_counter, Task( task.core_id, task.stack_idx, -1 ) ) );
            auto stack_idx = core_stack[i].size() - 1;
            for ( auto c = children.first; c != children.second; ++c ) {
              auto child = boost::target( *c, g );
              assert( node_type[child] == 0 );
              task_queue[i].push_back( Task( i, stack_idx, child ) );
            }
          }
          // if not spawning any child, notify parent
          else if ( join_counter == 0 ) {
            core_stack[ task.core_id ][ task.stack_idx ].join_counter -= 1;
            if ( core_stack[ task.core_id ][ task.stack_idx ].join_counter == 0 ) {
              // get the continuation
              auto child = boost::target( *children.first, g );
              core_stack[ task.core_id ][ task.stack_idx ].continuation.task_id = child;
            }
          }
        }
      }
      active = active | core_active[i];
      queues_empty = queues_empty & task_queue[i].empty();
      stacks_empty = stacks_empty & core_stack[i].empty();
    }

    // advance time
    timesteps += 1;
  }

  per_region_stats[index].push_back( std::make_tuple( unique, total, timesteps ) );
  per_region_stats[index+1].push_back( std::make_tuple( unique, total, timesteps ) );
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

//-------------------------------------------------------------------------
// main()
//-------------------------------------------------------------------------

int main ( int argc, char* argv[] )
{
  try {

    srand( 0 );

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
    std::vector< std::vector< std::tuple< int,int,int > > > per_region_stats( 6 );

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
        // Unbounded
        //-----------------------------------------------------------------

        auto res0 = max_share( strands );
        per_region_stats[0].push_back( res0 );

        auto res1 = min_pc( strands );
        per_region_stats[1].push_back( res1 );

        //-----------------------------------------------------------------
        // Bounded
        //-----------------------------------------------------------------

        loop_analysis( strands, per_region_stats, g_num_contexts[0], 2 );
        loop_analysis( strands, per_region_stats, g_num_contexts[1], 4 );

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
        // Unbounded
        //-----------------------------------------------------------------

        auto unbounded_schedule = asap_schedule( tg );
        task_analysis( unbounded_schedule, ptrace, per_region_stats, 0 );

        //-----------------------------------------------------------------
        // Bounded
        //-----------------------------------------------------------------

        //auto bounded_schedule_4 = bounded_greedy_schedule( tg, g_num_contexts[0] );
        ws_schedule( tg, ptrace, 4, per_region_stats, 2, true );

        //auto bounded_schedule_8 = bounded_greedy_schedule( tg, g_num_contexts[1] );
        //auto bounded_schedule_8 = ws_schedule( tg, g_num_contexts[1] );
        //print_schedule( bounded_schedule_8 );
        //task_analysis( bounded_schedule_8, ptrace, per_region_stats, 4 );
        per_region_stats[4].push_back( std::make_tuple( 0,0,0 ) );
        per_region_stats[5].push_back( std::make_tuple( 0,0,0 ) );
      }
    }

    for ( int i = 0; i < per_region_stats.size(); ++i ) {
      out << "//" << std::string( 72, '-' ) << std::endl;
      if      ( i == 0 ) { out << "// Unbounded max-share results " << std::endl; }
      else if ( i == 1 ) { out << "// Unbounded min-pc results " << std::endl; }
      else if ( i == 2 ) { out << "// Bounded-4 max-share results " << std::endl; }
      else if ( i == 3 ) { out << "// Bounded-4 min-pc results " << std::endl; }
      else if ( i == 4 ) { out << "// Bounded-8 max-share results " << std::endl; }
      else if ( i == 5 ) { out << "// Bounded-8 min-pc results " << std::endl; }
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
