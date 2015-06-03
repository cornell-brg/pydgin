//========================================================================
// ubmark-bin-search
//========================================================================
// This is a simple micro-benchmark which does many parallel binary
// searches in a sorted set of keys to determine if a give key is
// present. It can generate its own dataset which is statically included
// as part of the binary. To generate a new dataset simply use the
// -dump-dataset command line option, place the new dataset in the
// subproject directory, and make sure you correctly inlude the dataset.

#include "pinfo.h"

#include "ubmark-bin-search-KeyValue.h"

#include "stdx-Timer.h"
#include "stdx-MathUtils.h"
#include "stdx-FstreamUtils.h"
#include "stdx-InputRange.h"
#include "stdx-Exception.h"

#include <cstring>
#include <iostream>
#include <vector>
#include <algorithm>

//------------------------------------------------------------------------
// Support for enabling stats
//------------------------------------------------------------------------

#ifdef _MIPS_ARCH_MAVEN
#include <machine/cop0.h>
#define set_stats_en( value_ ) \
  maven_set_cop0_stats_enable( value_ );
#else
#define set_stats_en( value_ )
#endif

//------------------------------------------------------------------------
// Include dataset (generated with -dump-dataset command line arg)
//------------------------------------------------------------------------

#include "ubmark-bin-search.dat"

//------------------------------------------------------------------------
// Explicit conditional move functions
//------------------------------------------------------------------------

#ifdef _MIPS_ARCH_MAVEN
inline void cmove( int* dest, int src, bool condition )
{
  asm ( "movn %0, %1, %2" : "+r"(*dest) : "r"(src), "r"(condition) );
}
#else
inline void cmove( int* dest, int src, bool condition )
{
  if ( condition )
    *dest = src;
}
#endif

//------------------------------------------------------------------------
// bin_search_scalar
//------------------------------------------------------------------------

__attribute__ ((noinline))
void bin_search_scalar( int values[], int keys[], int keys_sz,
                        KeyValue kv[], int kv_sz )
{
  for ( int i = 0; i < keys_sz; i++ ) {

    int key     = keys[i];
    int idx_min = 0;
    int idx_mid = kv_sz/2;
    int idx_max = kv_sz-1;

    bool done = false;
    values[i] = -1;
    do {
      int midkey = kv[idx_mid].key;

      if ( key == midkey ) {
        values[i] = kv[idx_mid].value;
        done = true;
      }

      if ( key > midkey )
        idx_min = idx_mid + 1;
      else if ( key < midkey )
        idx_max = idx_mid - 1;

      idx_mid = ( idx_min + idx_max ) / 2;

    } while ( !done && (idx_min <= idx_max) );

  }
}

//------------------------------------------------------------------------
// bin_search_scalar_cmove
//------------------------------------------------------------------------

__attribute__ ((noinline))
void bin_search_scalar_cmove( int values[], int keys[], int keys_sz,
                              KeyValue kv[], int kv_sz )
{
  for ( int i = 0; i < keys_sz; i++ ) {

    int key     = keys[i];
    int idx_min = 0;
    int idx_mid = kv_sz/2;
    int idx_max = kv_sz-1;

    bool done = false;
    values[i] = -1;
    do {
      int midkey = kv[idx_mid].key;

      // if ( key == midkey ) {
      //   values[i] = kv[idx_mid].value;
      //   done = true;
      // }

      bool key_eq_midkey = ( key == midkey );
      cmove( &values[i], kv[idx_mid].value, key_eq_midkey );

      // if ( key > midkey )
      //   idx_min = idx_mid + 1;
      // else if ( key < midkey )
      //   idx_max = idx_mid - 1;

      bool key_gt_midkey = ( key > midkey );
      cmove( &idx_min, idx_mid + 1,  key_gt_midkey );
      cmove( &idx_max, idx_mid - 1, !key_gt_midkey );

      idx_mid = ( idx_min + idx_max ) / 2;

      // We use the extra inline assemly to force gcc to keep this as
      // dataflow and not convert the condition into two consecutive
      // branches.

      done = key_eq_midkey || (idx_min > idx_max);
      #ifdef _MIPS_ARCH_MAVEN
        asm ( "" : "+r"(done) );
      #endif
    } while ( !done );
  }
}

//------------------------------------------------------------------------
// dump_dataset
//------------------------------------------------------------------------

void dump_dataset( const std::string& fname, int dataset_sz, int length )
{
  // Generate array of key/value pairs

  std::vector<KeyValue> kv(dataset_sz);
  for ( int i = 0; i < dataset_sz; i++ ) {
    kv.at(i)
      = KeyValue( stdx::rand_int(1000000), stdx::rand_int(1000000) );
  }

  // Sort array of key/value pairs and remove duplicates

  stdx::sort( stdx::mk_irange(kv) );
  typedef std::vector<KeyValue>::iterator ITR;
  ITR new_end = stdx::unique( stdx::mk_irange(kv) );
  kv.erase( new_end, kv.end() );

  // Randomly pick key/value pairs which we will then search for

  std::vector<int> keys(length);
  std::vector<int> values(length);
  for ( int i = 0; i < length; i++ ) {
    int idx = stdx::rand_int(kv.size());
    keys.at(i)   = kv.at(idx).key;
    values.at(i) = kv.at(idx).value;
  }

  // Output dataset

  stdx::DefaultStdoutFstream fout(fname);

  fout << "// Data set for ubmark-bin-search\n\n";
  fout << "int keys_sz = " << length << ";\n\n";
  fout << "int kv_sz = " << kv.size() << ";\n\n";

  fout << "KeyValue kv[] = {\n";
  for ( int i = 0; i < static_cast<int>(kv.size()); i++ )
    fout << "  KeyValue(" << kv[i].key << ","
                            << kv[i].value << "),\n";
  fout << "};\n" << std::endl;

  fout << "int keys[] = {\n";
  for ( int i = 0; i < length; i++ )
    fout << "  " << keys[i] << ",\n";
  fout << "};\n" << std::endl;

  fout << "int ref[] = {\n";
  for ( int i = 0; i < length; i++ )
    fout << "  " << values[i] << ",\n";
  fout << "};\n" << std::endl;
}

//------------------------------------------------------------------------
// verify_results
//------------------------------------------------------------------------

void verify_results( const char* name,
                     int values[], int ref[], int size )
{
  for ( int i = 0; i < size; i++ ) {
    if ( !( values[i] == ref[i] ) ) {
      std::cout << "  [ FAILED ] " << name << " : "
        << "dest[" << i << "] != ref[" << i << "] "
        << "( " << values[i] << " != " << ref[i] << " )"
        << std::endl;
      return;
    }
  }
  std::cout << "  [ passed ] " << name << std::endl;
}

//------------------------------------------------------------------------
// Implementation Table
//------------------------------------------------------------------------
// This table contains one structure for each of the above
// implementations. Each structure includes the name of the
// implementation used for command line parsing and verification output,
// and a function pointer to the actual implementation function.

typedef void (*impl_func_ptr)(int[],int[],int,KeyValue[],int);
struct Impl
{
  const char*   str;
  impl_func_ptr func_ptr;
};

Impl impl_table[] =
{
  { "scalar",       &bin_search_scalar         },
  { "scalar-cmove", &bin_search_scalar_cmove   },
  { "",             0                          },
};

//------------------------------------------------------------------------
// Test harness
//------------------------------------------------------------------------

// HACK: Destination array to enforce alignment
// int g_values[10000] __attribute__ ((aligned (32)));
// int g_values[10000];

int main( int argc, char* argv[] )
{
  // Handle any uncaught exceptions

  stdx::set_terminate();

  // Command line options

  pinfo::ProgramInfo pi;

  pi.add_arg( "--size",     "int", "1000", "Size of keys array" );
  pi.add_arg( "--ntrials",  "int", "1",    "Number of trials" );
  pi.add_arg( "--verify",   NULL,  NULL,   "Verify an implementation" );
  pi.add_arg( "--stats",    NULL,  NULL,   "Ouptut stats about run" );
  pi.add_arg( "--warmup",   NULL,  NULL,   "Warmup the cache" );

  pi.add_arg( "--dataset-size", "int", "1000",
              "Size of dataset for dump-dataset" );
  pi.add_arg( "--dump-dataset", "fname", "none",
              "Dump generated dataset to given file" );

  std::string impl_list_str;
  Impl* impl_ptr_tmp = &impl_table[0];
  impl_list_str += "{";
  impl_list_str += impl_ptr_tmp->str;
  impl_ptr_tmp++;
  while ( impl_ptr_tmp->func_ptr != 0 ) {
    impl_list_str += ",";
    impl_list_str += impl_ptr_tmp->str;
    impl_ptr_tmp++;
  }
  impl_list_str += "}";

  pi.add_arg( "--impl", impl_list_str.c_str(),
              "scalar", "Implementation style" );

  pi.parse_args( argc, argv );

  // Set misc local variables from command line

  int  size       = static_cast<int>(pi.get_long("--size"));
  int  dataset_sz = static_cast<int>(pi.get_long("--dataset-size"));
  int  ntrials    = static_cast<int>(pi.get_long("--ntrials"));
  bool verify     = static_cast<bool>(pi.get_flag("--verify"));
  bool stats      = static_cast<bool>(pi.get_flag("--stats"));
  bool warmup     = static_cast<bool>(pi.get_flag("--warmup"));

  // Setup implementation

  const char* impl_str = pi.get_string("--impl");
  bool impl_all = ( strcmp( impl_str, "all" ) == 0 );
  Impl* impl_ptr = &impl_table[0];
  while ( !impl_all && (impl_ptr->func_ptr != 0) ) {
    if ( strcmp( impl_str, impl_ptr->str ) == 0 )
      break;
    impl_ptr++;
  }

  if ( impl_all && !verify ) {
    std::cout
      << "\n ERROR: --impl all only valid for verification\n"
      << std::endl;
    return 1;
  }

  if ( !impl_all && (impl_ptr->func_ptr == 0) ) {
    std::cout
      << "\n ERROR: Unrecognized implementation "
      << "(" << impl_str << ")\n" << std::endl;
    return 1;
  }

  // Dump data if --dump-dataset given on command line.

  const char* dump_dataset_fname = pi.get_string("--dump-dataset");
  if ( strcmp( dump_dataset_fname, "none" ) != 0 ) {
    dump_dataset( dump_dataset_fname, dataset_sz, size );
    return 0;
  }

  // Verify that the number of seraches on command line is not too large

  if ( size > keys_sz ) {
    std::cout
      << "\n ERROR: Number of searches is larger than dataset ( "
      << size << " > " << keys_sz << " ). Either decrease "
      << "number of searches or regenerate a larger dataset with the "
      << "--dump-dataset command line option.\n" << std::endl;
    return 1;
  }

  // Verify the implementations

  if ( verify ) {

    std::cout << "\n Unit Tests : " << argv[0] << "\n" << std::endl;

    if ( !impl_all ) {
      std::vector<int> values(size);
      impl_ptr->func_ptr( &values[0], keys, size, kv, kv_sz );
      verify_results( impl_ptr->str, &values[0], ref, size );
    }
    else {
      Impl* impl_ptr = &impl_table[0];
      while ( impl_ptr->func_ptr != 0 ) {
        std::vector<int> values(size);
        impl_ptr->func_ptr( &values[0], keys, size, kv, kv_sz );
        verify_results( impl_ptr->str, &values[0], ref, size );
        impl_ptr++;
      }
    }

    std::cout << std::endl;
    return 0;
  }

  // Execute the micro-benchmark

  // HACK: dest now declared globally to force alignment.
  std::vector<int> values(size);

  if ( warmup )
    impl_ptr->func_ptr( &values[0], keys, size, kv, kv_sz );

  stdx::Timer timer;
  timer.start();
  set_stats_en(true);

  for ( int i = 0; i < ntrials; i++ )
    impl_ptr->func_ptr( &values[0], keys, size, kv, kv_sz );

  set_stats_en(false);
  timer.stop();

  // Display stats

  if ( stats )
    std::cout << "runtime = " << timer.get_elapsed() << std::endl;

  // Return zero upon successful completion

  return 0;
}

