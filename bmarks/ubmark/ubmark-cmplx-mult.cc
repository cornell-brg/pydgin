//========================================================================
// ubmark-cmlpx-mult
//========================================================================
// This is a simple micro-benchmark which does vector-vector complex
// multiply with floating point real and imaginary components. It can
// generate its own dataset which is statically included as part of the
// binary. To generate a new dataset simply use the -dump-dataset
// command line option, place the new dataset in the subproject
// directory, and make sure you correctly inlude the dataset.

#include "pinfo.h"

#include "ubmark-cmplx-mult-Complex.h"
#include "ubmark-cmplx-mult-scalar.h"

#include "stdx-Timer.h"
#include "stdx-MathUtils.h"
#include "stdx-FstreamUtils.h"
#include "stdx-Exception.h"

#include <cstring>
#include <iostream>
#include <vector>

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

#include "ubmark-cmplx-mult.dat"

//------------------------------------------------------------------------
// cmplx_mult_scalar_unopt
//------------------------------------------------------------------------

void cmplx_mult_scalar_unopt( Complex dest[], Complex src0[],
                              Complex src1[], int size )
{
  for ( int i = 0; i < size; i++ )
    dest[i] = src0[i] * src1[i];
}

//------------------------------------------------------------------------
// dump_dataset
//------------------------------------------------------------------------

void dump_dataset( const std::string& fname, int size )
{
  // Generate inputs

  std::vector<Complex> src0(size), src1(size);
  for ( int i = 0; i < size; i++ ) {

    src0.at(i) = Complex( stdx::rand_int( 1000000 ) / 1000.0f,
                          stdx::rand_int( 1000000 ) / 1000.0f );

    src1.at(i) = Complex( stdx::rand_int( 1000000 ) / 1000.0f,
                          stdx::rand_int( 1000000 ) / 1000.0f );

  }

  // Generate reference outputs

  std::vector<Complex> dest(size);
  cmplx_mult_scalar( &dest[0], &src0[0], &src1[0], size );

  // Output dataset

  stdx::DefaultStdoutFstream fout(fname);

  fout << "// Data set for ubmark-cmplx-mult\n\n";
  fout << "int dataset_sz = " << size << ";\n\n";

  fout << "Complex src0[] = {\n";
  for ( int i = 0; i < size; i++ )
    fout << "  Complex(" << src0[i].real << ","
                         << src0[i].imag << "),\n";
  fout << "};\n" << std::endl;

  fout << "Complex src1[] = {\n";
  for ( int i = 0; i < size; i++ )
    fout << "  Complex(" << src1[i].real << ","
                         << src1[i].imag << "),\n";
  fout << "};\n" << std::endl;

  fout << "Complex ref[] = {\n";
  for ( int i = 0; i < size; i++ )
    fout << "  Complex(" << dest[i].real << ","
                         << dest[i].imag << "),\n";
  fout << "};\n" << std::endl;
}

//------------------------------------------------------------------------
// verify_results
//------------------------------------------------------------------------

void verify_results( const char* name,
                     Complex dest[], Complex ref[], int size )
{
  for ( int i = 0; i < size; i++ ) {
    if ( !( dest[i] == ref[i] ) ) {
      std::cout << "  [ FAILED ] " << name << " : "
        << "dest[" << i << "] != ref[" << i << "] "
        << "( " << dest[i] << " != " << ref[i] << " )"
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

typedef void (*impl_func_ptr)(Complex[],Complex[],Complex[],int);
struct Impl
{
  const char*   str;
  impl_func_ptr func_ptr;
};

Impl impl_table[] =
{
  { "scalar",       &cmplx_mult_scalar       },
  { "scalar-unopt", &cmplx_mult_scalar_unopt },
  { "",             0                        },
};

//------------------------------------------------------------------------
// Test harness
//------------------------------------------------------------------------

// HACK: Destination array to enforce alignment
// Complex g_dest[1000] __attribute__ ((aligned (32)));
// Complex g_dest[1000];

int main( int argc, char* argv[] )
{
  // Handle any uncaught exceptions

  stdx::set_terminate();

  // Command line options

  pinfo::ProgramInfo pi;

  pi.add_arg( "--size",     "int", "1000", "Size of arrays" );
  pi.add_arg( "--ntrials",  "int", "1",    "Number of trials" );
  pi.add_arg( "--verify",   NULL,  NULL,   "Verify an implementation" );
  pi.add_arg( "--stats",    NULL,  NULL,   "Ouptut stats about run" );
  pi.add_arg( "--warmup",   NULL,  NULL,   "Warmup the cache" );

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

  int  size     = static_cast<int>(pi.get_long("--size"));
  int  ntrials  = static_cast<int>(pi.get_long("--ntrials"));
  bool verify   = static_cast<bool>(pi.get_flag("--verify"));
  bool stats    = static_cast<bool>(pi.get_flag("--stats"));
  bool warmup   = static_cast<bool>(pi.get_flag("--warmup"));

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

  // Dump data if --dump-dataset given on command line

  const char* dump_dataset_fname = pi.get_string("--dump-dataset");
  if ( strcmp( dump_dataset_fname, "none" ) != 0 ) {
    dump_dataset( dump_dataset_fname, size );
    return 0;
  }

  // Verify that size given on command line is not too large

  if ( size > dataset_sz ) {
    std::cout
      << "\n ERROR: Size is larger than dataset ( " << size << " > "
      << dataset_sz << " ). Either decrease \n size or regenerate "
      << "a larger dataset with the --dump-dataset command \n line "
      << "option.\n" << std::endl;
    return 1;
  }

  // Verify the implementations

  if ( verify ) {

    std::cout << "\n Unit Tests : " << argv[0] << "\n" << std::endl;

    if ( !impl_all ) {
      std::vector<Complex> dest(size);
      impl_ptr->func_ptr( &dest[0], src0, src1, size );
      verify_results( impl_ptr->str, &dest[0], ref, size );
    }
    else {
      Impl* impl_ptr = &impl_table[0];
      while ( impl_ptr->func_ptr != 0 ) {
        std::vector<Complex> dest(size);
        impl_ptr->func_ptr( &dest[0], src0, src1, size );
        verify_results( impl_ptr->str, &dest[0], ref, size );
        impl_ptr++;
      }
    }

    std::cout << std::endl;
    return 0;
  }

  // Execute the micro-benchmark

  // HACK: dest now declared globally to force alignment.
  std::vector<Complex> dest(size);

  if ( warmup )
    impl_ptr->func_ptr( &dest[0], src0, src1, size );

  stdx::Timer timer;
  timer.start();
  set_stats_en(true);

  for ( int i = 0; i < ntrials; i++ )
    impl_ptr->func_ptr( &dest[0], src0, src1, size );

  set_stats_en(false);
  timer.stop();

  // Display stats

  if ( stats )
    std::cout << "runtime = " << timer.get_elapsed() << std::endl;

  // Return zero upon successful completion

  return 0;
}

