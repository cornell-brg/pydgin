//=========================================================================
// task-trace-analyze-wsrt-schedule.cc
//=========================================================================
// Author : Shreesha Srinath
// Date   : November 6th, 2017
//
// Program reads the strand csv dumps from pydgin which have been annotated
// for spawn points, the task graph spit out by pydgin, and the
// join-constraints csv dumped by pydgin and performs work-stealing
// scheduling for strands using a given number of contexts

#include "csv.h"
#include "cxxopts.hpp"

#include <algorithm>
#include <cstdlib>
#include <deque>
#include <fstream>
#include <iostream>
#include <iomanip>
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

typedef boost::adjacency_list<boost::vecS, boost::vecS, boost::bidirectionalS, boost::no_property, int> Graph;
typedef boost::graph_traits< Graph >::vertex_descriptor Vertex_t;
typedef boost::graph_traits< Graph >::edge_descriptor Edge_t;
typedef boost::graph_traits< Graph >::vertex_iterator VertexIter;

int g_num_contexts[] = { 4, 8 };

//-------------------------------------------------------------------------
// dump_stats()
//-------------------------------------------------------------------------

void dump_stats( std::ostream& out, const int& unique_insts,
                 const int& total_insts, const int& steps )
{
  out << "Overall stats:" << std::endl;
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
  int tid;
  int pc;
  int spoint;

  TraceEntry( int pid, int tid, int pc, int spoint )
    : pid( pid ), tid( tid ), pc( pc ), spoint( spoint )
  { }
};

// Helper function to print the struct
std::ostream& operator<< ( std::ostream& o, const TraceEntry& e )
{
  o << std::hex << "[" << e.pid << "," << e.tid << ","
    << e.pc << "," << e.spoint << "]" << std::endl;
  return o;
}

//-------------------------------------------------------------------------
// utility functions for ws-scheduling
//-------------------------------------------------------------------------

typedef std::vector< std::deque< Vertex_t > > TaskQueue;

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

std::tuple< int,int,int >
ws_schedule(
  Graph& g,
  std::vector< TraceEntry >& ptrace,
  std::map<int,int>& join_constrs,
  int num_contexts,
  bool min_pc_reconverge = false,
  bool linetrace = false
)
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

  // per-core data-structures
  TaskQueue task_queue( num_contexts );
  std::vector< std::deque< TraceEntry > > core_trace( num_contexts );
  std::vector< std::vector< Vertex_t > > core_stack( num_contexts );

  // linetrace
  std::vector< Vertex_t > curr_task( num_contexts );

  // schedule the root node
  auto root = *boost::vertices( g ).first;
  auto out_degree = boost::out_degree( root, g );
  task_queue[0].push_back( root );

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
        if ( node_map[ join_constrs[stack] ] == 0 ) {
          core_stack[i].pop_back();
          core_active[i] = true;
          curr_task[i] = join_constrs[stack];
          // extract the trace for the core
          assert( core_trace[i].empty() );
          for ( auto entry: ptrace ) {
            if ( entry.tid == join_constrs[stack] ) {
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
        core_active[i] = true;
        curr_task[i] = task;
        // extract the trace for the core
        assert( core_trace[i].empty() );
        for ( auto entry: ptrace ) {
          if ( entry.tid == task ) {
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
            if ( entry.tid == task ) {
              core_trace[i].push_back( entry );
            }
          }
          total += core_trace[i].size();
        }
      }
    }

    // Print linetrace
    if ( linetrace ) {
      for ( int i = 0; i < num_contexts; ++i ) {
        if ( core_active[i] ) {
          std::cout.width(5);
          std::cout << std::right << curr_task[i];
        }
        else {
          std::cout.width(5);
          std::cout << std::right << "#";
        }
        std::cout.width(1);
        std::cout << "|";
      }
      std::cout << std::endl;
    }

    // Process active cores
    std::vector< int > pc_list;
    std::vector< int > unique_pc_list;
    for ( int i = 0; i < num_contexts; ++i ) {
      if ( !core_trace[i].empty() && core_active[i] ) {
        auto inst = core_trace[i].front();
        pc_list.push_back( inst.pc );
      }
    }

    // Calculate instruction redundancy
    if ( min_pc_reconverge ) {
      int min_pc = *std::min_element( pc_list.begin(), pc_list.end() );
      for ( int i = 0; i < num_contexts; ++i ) {
        if ( !core_trace[i].empty() && core_active[i] ) {
          if ( core_trace[i].front().pc == min_pc ) {
            auto inst = core_trace[i].front();
            core_trace[i].pop_front();
            // instruction is spawning a node
            if ( inst.spoint == 1 ) {
              assert( boost::out_degree( inst.tid, g ) == 2 );
              auto children = boost::out_edges( curr_task[i], g );
              for ( auto c = children.first; c != children.second; ++c ) {
                auto child = boost::target( *c, g );
                node_map[ child ] -= 1;
                // enqueue the child-strand in the task_queue
                if ( g[*c] == 0 ) {
                  task_queue[i].push_back( child );
                }
                // retain the continuation
                else if ( g[*c] == 1 ) {
                  for ( auto entry: ptrace ) {
                    if ( entry.tid == child ) {
                      core_trace[i].push_back( entry );
                      total += 1;
                    }
                  }
                  curr_task[i] = child;
                }
              }
            }
          }
        }
      }
      unique += 1;
    }
    // max-share
    else {
      for ( auto pc: pc_list ) {
        if ( std::find( unique_pc_list.begin(), unique_pc_list.end(), pc )
             == unique_pc_list.end() ) {
          unique_pc_list.push_back( pc );
        }
      }
      unique += unique_pc_list.size();

      for ( int i = 0; i < num_contexts; ++i ) {
        if ( !core_trace[i].empty() && core_active[i] ) {
          auto inst = core_trace[i].front();
          core_trace[i].pop_front();
          // instruction is spawning a node
          if ( inst.spoint == 1 ) {
            assert( boost::out_degree( inst.tid, g ) == 2 );
            auto children = boost::out_edges( curr_task[i], g );
            for ( auto c = children.first; c != children.second; ++c ) {
              auto child = boost::target( *c, g );
              node_map[ child ] -= 1;
              // enqueue the child-strand in the task_queue
              if ( g[*c] == 0 ) {
                task_queue[i].push_back( child );
              }
              // retain the continuation
              else if ( g[*c] == 1 ) {
                for ( auto entry: ptrace ) {
                  if ( entry.tid == child ) {
                    core_trace[i].push_back( entry );
                    total += 1;
                  }
                }
                curr_task[i] = child;
              }
            }
          }
        }
      }
    }

    // Check if any traces have finished
    active = false;
    queues_empty = true;
    stacks_empty = true;
    for ( int i = 0; i < num_contexts; ++i ) {
      // finished the current strand, hit a wait(), remember the stack
      if ( core_trace[i].empty() && core_active[i] ) {
        core_active[i] = false;
        // if a wait point, push onto the stack
        if ( join_constrs.count( curr_task[i] ) == 1 ) {
          core_stack[i].push_back( curr_task[i] );
        }
        if ( boost::out_degree( curr_task[i], g ) ) {
          assert( boost::out_degree( curr_task[i], g ) == 1 );
          auto children = boost::out_edges( curr_task[i], g );
          auto child = boost::target( *children.first, g );
          node_map[ child ] -= 1;
        }
      }
      active = active | core_active[i];
      queues_empty = queues_empty & task_queue[i].empty();
      stacks_empty = stacks_empty & core_stack[i].empty();
    }

    // advance time
    timesteps += 1;
  }

  return std::make_tuple( unique, total, timesteps );
}

//-------------------------------------------------------------------------
// level_schedule()
//-------------------------------------------------------------------------

std::tuple< int,int,int >
level_schedule(
  Graph& g,
  std::vector< TraceEntry >& ptrace,
  std::map<int,int>& join_constrs,
  int num_contexts,
  bool min_pc_reconverge = false,
  bool linetrace = false
)
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

  // active nodes in the queue
  std::deque< Vertex_t > active_nodes;

  // per-core data-structures
  std::vector< std::deque< Vertex_t > >   core_queue( num_contexts );
  std::vector< std::deque< TraceEntry > > core_trace( num_contexts );
  std::vector< std::vector< Vertex_t > >  core_stack( num_contexts );

  // linetrace
  std::vector< Vertex_t > curr_task( num_contexts );

  // schedule the root node
  auto root = *boost::vertices( g ).first;
  auto out_degree = boost::out_degree( root, g );
  active_nodes.push_back( root );

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
        if ( node_map[ join_constrs[stack] ] == 0 ) {
          core_stack[i].pop_back();
          core_active[i] = true;
          curr_task[i] = join_constrs[stack];
          // extract the trace for the core
          assert( core_trace[i].empty() );
          for ( auto entry: ptrace ) {
            if ( entry.tid == join_constrs[stack] ) {
              core_trace[i].push_back( entry );
            }
          }
          total += core_trace[i].size();
        }
      }
    }

    // If a core is idle and has an item in the active queue, pop it and
    // assign it to the core for execution.
    for ( int i = 0; i < num_contexts; ++i ) {
      if ( !active_nodes.empty() && !core_active[i] ) {
        auto task = active_nodes.back();
        active_nodes.pop_back();
        core_active[i] = true;
        curr_task[i] = task;
        // extract the trace for the core
        assert( core_trace[i].empty() );
        for ( auto entry: ptrace ) {
          if ( entry.tid == task ) {
            core_trace[i].push_back( entry );
          }
        }
        total += core_trace[i].size();
      }
    }

    // Print linetrace
    if ( linetrace ) {
      for ( int i = 0; i < num_contexts; ++i ) {
        if ( core_active[i] ) {
          std::cout.width(5);
          std::cout << std::right << curr_task[i];
        }
        else {
          std::cout.width(5);
          std::cout << std::right << "#";
        }
        std::cout.width(1);
        std::cout << "|";
      }
      std::cout << std::endl;
    }

    // Process active cores
    std::vector< int > pc_list;
    std::vector< int > unique_pc_list;
    for ( int i = 0; i < num_contexts; ++i ) {
      if ( !core_trace[i].empty() && core_active[i] ) {
        auto inst = core_trace[i].front();
        pc_list.push_back( inst.pc );
      }
    }

    // Calculate instruction redundancy
    if ( min_pc_reconverge ) {
      int min_pc = *std::min_element( pc_list.begin(), pc_list.end() );
      for ( int i = 0; i < num_contexts; ++i ) {
        if ( !core_trace[i].empty() && core_active[i] ) {
          if ( core_trace[i].front().pc == min_pc ) {
            auto inst = core_trace[i].front();
            core_trace[i].pop_front();
            // instruction is spawning a node
            if ( inst.spoint == 1 ) {
              assert( boost::out_degree( inst.tid, g ) == 2 );
              auto children = boost::out_edges( curr_task[i], g );
              for ( auto c = children.first; c != children.second; ++c ) {
                auto child = boost::target( *c, g );
                node_map[ child ] -= 1;
                // enqueue the child-strand in the task_queue
                if ( g[*c] == 0 ) {
                  core_queue[i].push_back( child );
                }
                // retain the continuation
                else if ( g[*c] == 1 ) {
                  for ( auto entry: ptrace ) {
                    if ( entry.tid == child ) {
                      core_trace[i].push_back( entry );
                      total += 1;
                    }
                  }
                  curr_task[i] = child;
                }
              }
            }
          }
        }
      }
      unique += 1;
    }
    // max-share
    else {
      for ( auto pc: pc_list ) {
        if ( std::find( unique_pc_list.begin(), unique_pc_list.end(), pc )
             == unique_pc_list.end() ) {
          unique_pc_list.push_back( pc );
        }
      }
      unique += unique_pc_list.size();

      for ( int i = 0; i < num_contexts; ++i ) {
        if ( !core_trace[i].empty() && core_active[i] ) {
          auto inst = core_trace[i].front();
          core_trace[i].pop_front();
          // instruction is spawning a node
          if ( inst.spoint == 1 ) {
            assert( boost::out_degree( inst.tid, g ) == 2 );
            auto children = boost::out_edges( curr_task[i], g );
            for ( auto c = children.first; c != children.second; ++c ) {
              auto child = boost::target( *c, g );
              node_map[ child ] -= 1;
              // enqueue the child-strand in the task_queue
              if ( g[*c] == 0 ) {
                core_queue[i].push_back( child );
              }
              // retain the continuation
              else if ( g[*c] == 1 ) {
                for ( auto entry: ptrace ) {
                  if ( entry.tid == child ) {
                    core_trace[i].push_back( entry );
                    total += 1;
                  }
                }
                curr_task[i] = child;
              }
            }
          }
        }
      }
    }

    // Check if any traces have finished
    active = false;
    stacks_empty = true;
    for ( int i = 0; i < num_contexts; ++i ) {
      // finished the current strand, hit a wait(), remember the stack
      if ( core_trace[i].empty() && core_active[i] ) {
        core_active[i] = false;
        // if a wait point, push onto the stack
        if ( join_constrs.count( curr_task[i] ) == 1 ) {
          core_stack[i].push_back( curr_task[i] );
        }
        if ( boost::out_degree( curr_task[i], g ) ) {
          assert( boost::out_degree( curr_task[i], g ) == 1 );
          auto children = boost::out_edges( curr_task[i], g );
          auto child = boost::target( *children.first, g );
          node_map[ child ] -= 1;
        }
        while ( !core_queue[i].empty() ) {
          active_nodes.push_back( core_queue[i].back() );
          core_queue[i].pop_back();
        }
      }
      active = active | core_active[i];
      stacks_empty = stacks_empty & core_stack[i].empty();
    }
    queues_empty = active_nodes.empty();

    // advance time
    timesteps += 1;
  }

  return std::make_tuple( unique, total, timesteps );
}



//-------------------------------------------------------------------------
// main()
//-------------------------------------------------------------------------

int main ( int argc, char* argv[] )
{

  //---------------------------------------------------------------------
  // Command line processing
  //---------------------------------------------------------------------

  cxxopts::Options options( argv[0], " - Options for trace analysis" );

  options.positional_help( "trace graph joins calls runtime outdir" );
  options.add_options()
    ( "h, help", "Print help" )
    ( "trace", "Trace file <task-trace.csv>", cxxopts::value<std::string>() )
    ( "graph", "Graph file <task-graph.csv>", cxxopts::value<std::string>() )
    ( "joins", "Join constrains <task-joins.csv>", cxxopts::value<std::string>() )
    ( "calls", "File with all call sites filtered <jal.csv>", cxxopts::value<std::string>() )
    ( "runtime", "Runtime metadata file", cxxopts::value<std::string>() )
    ( "outdir", "Output directory", cxxopts::value<std::string>() )
    ( "cores", "Number of cores", cxxopts::value<int>()->default_value("8") )
    ( "linetrace", "Linetrace", cxxopts::value<int>()->default_value("0") )
    ;

  const std::vector< std::string > positional_args = { "trace", "graph", "joins", "calls", "runtime", "outdir" };
  options.parse_positional( positional_args );
  options.parse( argc, argv );

  if ( options.count( "help" ) || options.count( "trace" ) == 0 ||
       options.count( "graph" ) == 0 || options.count( "joins" ) == 0 ||
       options.count( "calls" ) == 0 || options.count( "runtime" ) == 0 ||
       options.count( "outdir" ) == 0 ) {
    std::cout << options.help() << std::endl;
    return 0;
  }

  std::string tracefile   = options["trace"].as< std::string >();
  std::string graphfile   = options["graph"].as< std::string >();
  std::string joinsfile   = options["joins"].as< std::string >();
  std::string callsfile   = options["calls"].as< std::string >();
  std::string runtimefile = options["runtime"].as< std::string >();
  std::string outdir      = options["outdir"].as< std::string >();

  g_num_contexts[0] = options["cores"].as< int >();
  bool linetrace    = options["linetrace"].as< int >();

  //---------------------------------------------------------------------
  // Read the runtime metadata file
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

  //---------------------------------------------------------------------
  // Read the calls csv file
  //---------------------------------------------------------------------

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

  //---------------------------------------------------------------------
  // Read the input tracefile
  //---------------------------------------------------------------------

  // Open the trace file
  io::CSVReader<3> in_trace( tracefile.c_str() );
  in_trace.read_header( io::ignore_extra_column, "pid", "tid", "pc" );

  std::string pid, tid, pc;
  std::vector< int >   pregions;
  std::vector< TraceEntry > trace;

  while ( in_trace.read_row( pid, tid, pc ) ) {

    // Collect unique parallel regions
    if ( std::find( pregions.begin(), pregions.end(), std::stoi( pid, 0, 16 ) )
          == pregions.end() ) {
      pregions.push_back( std::stoi( pid, 0, 16 ) );
    }

    // check for a match in spawn point
    int tgt = std::stoi( pc, 0, 16 );
    int match = 0;
    for ( auto kv: runtime_jal_pcs ) {
      if ( tgt == kv.first && kv.second == "run") {
        match = 1;
        break;
      }
    }

    // Collect the trace
    trace.push_back(
      TraceEntry(
        std::stoi( pid,    0, 16 ),
        std::stoi( tid,    0, 16 ),
        std::stoi( pc,     0, 16 ),
        match
      )
    );

  }

  assert( pregions.size() == 1 );

  //---------------------------------------------------------------------
  // Read the input graphfile
  //---------------------------------------------------------------------

  io::CSVReader<4> in_graph( graphfile.c_str() );
  in_graph.read_header( io::ignore_extra_column, "pid", "parent", "child", "edge" );

  std::string parent, child, edge;

  Graph g;
  while ( in_graph.read_row( pid, parent, child, edge ) ) {
    // NOTE: In pydgin/sim.py I dump the task graph as an int
    boost::add_edge( std::stoi( parent, 0 ), std::stoi( child,  0 ), std::stoi( edge,  0 ), g );
  }

  //---------------------------------------------------------------------
  // Read the join constraints file
  //---------------------------------------------------------------------

  io::CSVReader<3> in_joins( joinsfile.c_str() );
  in_joins.read_header( io::ignore_extra_column, "pid", "parent", "child" );

  std::map<int,int> join_constrs;

  while ( in_joins.read_row( pid, parent, child ) ) {
    join_constrs[ std::stoi( parent, 0, 16 ) ] = std::stoi( child,  0, 16 );
  }

  std::ofstream out;
  out.open( ( outdir + "/trace-analysis.txt" ).c_str() );

  //---------------------------------------------------------------------
  //  Child-stealing no reconvergence
  //---------------------------------------------------------------------

  auto res0 = ws_schedule( g, trace, join_constrs, g_num_contexts[0], false, linetrace );

  out << "//" << std::string( 72, '-' ) << std::endl;
  out << "// Child-stealing " << g_num_contexts[0] << " cores" << std::endl;
  out << "//" << std::string( 72, '-' ) << std::endl;
  out << std::endl;
  dump_stats( out, std::get<0>( res0 ), std::get<1>( res0 ), std::get<2>( res0 ) );

  std::cout << std::endl;

  //---------------------------------------------------------------------
  //  Child-stealing with reconvergence
  //---------------------------------------------------------------------

  auto res1 = ws_schedule( g, trace, join_constrs, g_num_contexts[0], true, linetrace );

  out << "//" << std::string( 72, '-' ) << std::endl;
  out << "// Child-stealing with min-pc " << g_num_contexts[0] << " cores" << std::endl;
  out << "//" << std::string( 72, '-' ) << std::endl;
  out << std::endl;
  dump_stats( out, std::get<0>( res1 ), std::get<1>( res1 ), std::get<2>( res1 ) );

  std::cout << std::endl;

  //---------------------------------------------------------------------
  //  Level-by-Level no reconvergence
  //---------------------------------------------------------------------

  auto res2 = level_schedule( g, trace, join_constrs, g_num_contexts[0], false, linetrace );

  out << "//" << std::string( 72, '-' ) << std::endl;
  out << "// Level-by-level scheduling " << g_num_contexts[0] << " cores" << std::endl;
  out << "//" << std::string( 72, '-' ) << std::endl;
  out << std::endl;
  dump_stats( out, std::get<0>( res2 ), std::get<1>( res2 ), std::get<2>( res2 ) );

  std::cout << std::endl;

  //---------------------------------------------------------------------
  //  Level-by-Level with reconvergence
  //---------------------------------------------------------------------

  auto res3 = level_schedule( g, trace, join_constrs, g_num_contexts[0], true, linetrace );

  out << "//" << std::string( 72, '-' ) << std::endl;
  out << "// Level-by-level scheduling with min-pc " << g_num_contexts[0] << " cores" << std::endl;
  out << "//" << std::string( 72, '-' ) << std::endl;
  out << std::endl;
  dump_stats( out, std::get<0>( res3 ), std::get<1>( res3 ), std::get<2>( res3 ) );

  std::cout << std::endl;

  out.close();

  return 0;
}
