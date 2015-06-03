//========================================================================
// ubmark-masked-filter
//========================================================================
// This is a simple micro-benchmark which does a masked filter
// operation. It can generate its own dataset which is statically
// included as part of the binary. To generate a new dataset simply use
// the -dump-dataset command line option, place the new dataset in the
// subproject directory, and make sure you correctly inlude the dataset.

#include "pinfo.h"

#include "ubmark-masked-filter-common.h"

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

#include "ubmark-masked-filter-reg.dat"
#include "ubmark-masked-filter-small.dat"
#include "ubmark-masked-filter-shot.dat"

//------------------------------------------------------------------------
// global coeffient values
//------------------------------------------------------------------------

uint g_coeff[] = { 8, 6 };

//------------------------------------------------------------------------
// masked_filter_scalar
//------------------------------------------------------------------------

__attribute__ ((noinline))
void masked_filter_scalar( byte dest[], byte mask[], byte src[],
                           int nrows, int ncols, uint coeff[] )
{
  uint coeff0 = coeff[0];
  uint coeff1 = coeff[1];
  uint norm = coeff[0] + 4*coeff[1];
  for ( int ridx = 1; ridx < nrows-1; ridx++ ) {
    for ( int cidx = 1; cidx < ncols-1; cidx++ ) {
      if ( mask[ ridx*ncols + cidx ] != 0 ) {
        uint out = ( src[ (ridx-1)*ncols + cidx     ] * coeff1 )
                 + ( src[ ridx*ncols     + (cidx-1) ] * coeff1 )
                 + ( src[ ridx*ncols     + cidx     ] * coeff0 )
                 + ( src[ ridx*ncols     + (cidx+1) ] * coeff1 )
                 + ( src[ (ridx+1)*ncols + cidx     ] * coeff1 );
        dest[ ridx*ncols + cidx ] = static_cast<byte>(out/norm);
      }
      else
        dest[ ridx*ncols + cidx ] = src[ ridx*ncols + cidx ];
    }
  }
}

//------------------------------------------------------------------------
// draw_square
//------------------------------------------------------------------------

void draw_square( byte image[], int nrows, int ncols,
                  int sq_x, int sq_y, int sq_sz, byte color )
{
  // Determine corners of square

  int tl_x = sq_x - sq_sz;
  if ( tl_x < 0 )
    tl_x = 0;

  int tl_y = sq_y - sq_sz;
  if ( tl_y < 0 )
    tl_y = 0;

  int br_x = sq_x + sq_sz;
  if ( br_x > ncols )
    br_x = ncols-1;

  int br_y = sq_y + sq_sz;
  if ( br_y > nrows )
    br_y = nrows-1;

  // Draw the square

  for ( int x = tl_x; x < br_x; x++ ) {
    for ( int y = tl_y; y < br_y; y++ ) {
      image[ x*ncols + y ] = color;
    }
  }

}

//------------------------------------------------------------------------
// dump_dataset
//------------------------------------------------------------------------

void dump_dataset( const std::string& fname, int size,
                   int nsquares, uint coeff[] )
{
  // Generate input image with random squares

  std::vector<byte> src(size*size,0xffu);
  for ( int i = 0; i < 1000; i++ ) {
    int sq_sz  = stdx::rand_int( size/6 );
    int sq_x   = stdx::rand_int( size );
    int sq_y   = stdx::rand_int( size );
    byte color = stdx::rand_int( 256 );
    draw_square( &src[0], size, size, sq_x, sq_y, sq_sz, color );
  }

  // Generate mask with random squares

  std::vector<byte> mask(size*size,0x00u);
  for ( int i = 0; i < nsquares; i++ ) {

    // These are some alternative sizes we can use to create datasets,
    // eventually we might want to make this a command line parameter.
    //
    //  int sq_sz = stdx::rand_int( size/10 );
    //  int sq_sz = stdx::rand_int( 2 );

    int sq_sz = stdx::rand_int( size/4 );
    int sq_x  = stdx::rand_int( size );
    int sq_y  = stdx::rand_int( size );
    draw_square( &mask[0], size, size, sq_x, sq_y, sq_sz, 0xffu );
  }

  // Generate reference output

  std::vector<byte> dest(size*size,0x00u);
  masked_filter_scalar( &dest[0], &mask[0], &src[0], size, size, coeff );

  // Output dataset

  stdx::DefaultStdoutFstream fout(fname);

  fout << "// Data set for ubmark-masked-filter\n\n";
  fout << "int size = " << size << ";\n\n";

  fout << "byte src[] = {\n";
  for ( int i = 0; i < size*size; i++ )
    fout << "  " << static_cast<int>(src[i]) << ",\n";
  fout << "};\n" << std::endl;

  fout << "byte mask[] = {\n";
  for ( int i = 0; i < size*size; i++ )
    fout << "  " << static_cast<int>(mask[i]) << ",\n";
  fout << "};\n" << std::endl;

  fout << "byte ref[] = {\n";
  for ( int i = 0; i < size*size; i++ )
    fout << "  " << static_cast<int>(dest[i]) << ",\n";
  fout << "};\n" << std::endl;
}

//------------------------------------------------------------------------
// dump_image
//------------------------------------------------------------------------

void dump_image( const char* fname, byte image[], int size )
{
  stdx::CheckedOutputFstream fout(fname);
  fout << "P3 " << size << " " << size << " 255\n";
  for ( int ridx = 0; ridx < size; ridx++ ) {
    for ( int cidx = 0; cidx < size; cidx++ ) {
      int idx = ridx*size + cidx;
      for ( int i = 0; i < 3; i++ )
        fout << static_cast<int>(image[idx]) << " ";
      fout << "\n";
    }
  }
}

//------------------------------------------------------------------------
// verify_results
//------------------------------------------------------------------------

void verify_results( const char* name,
                     byte dest[], byte ref[], int size )
{
  for ( int i = 0; i < size*size; i++ ) {
    if ( !( dest[i] == ref[i] ) ) {
      std::cout << "  [ FAILED ] " << name << " : "
        << "dest[" << i << "] != ref[" << i << "] "
        << "( " << static_cast<int>(dest[i])
                << " != " << static_cast<int>(ref[i]) << " )"
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

typedef void (*impl_func_ptr)(byte[],byte[],byte[],int,int,uint[]);
struct Impl
{
  const char*   str;
  impl_func_ptr func_ptr;
};

Impl impl_table[] =
{
  { "scalar",     &masked_filter_scalar     },
  { "",           0                         },
};

//------------------------------------------------------------------------
// Test harness
//------------------------------------------------------------------------

// HACK: Destination array to enforce alignment
// byte g_dest[10000] __attribute__ ((aligned (32)));
// byte g_dest[10000];

int main( int argc, char* argv[] )
{
  // Handle any uncaught exceptions

  stdx::set_terminate();

  // Command line options

  pinfo::ProgramInfo pi;

  pi.add_arg( "--mask",    "{reg,small,shot}", "reg", "Filter mask" );
  pi.add_arg( "--ntrials",  "int", "1",    "Number of trials" );
  pi.add_arg( "--verify",   NULL,  NULL,   "Verify an implementation" );
  pi.add_arg( "--stats",    NULL,  NULL,   "Ouptut stats about run" );
  pi.add_arg( "--warmup",   NULL,  NULL,   "Warmup the cache" );

  pi.add_arg( "--dataset-size", "int", "100",
              "Size of image to generate" );

  pi.add_arg( "--dataset-nsquares", "int", "10",
              "Number of squares in mask" );

  pi.add_arg( "--dump-images", NULL, NULL,
              "Dump input and output image to ppm files" );

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

  int  ntrials    = static_cast<int>(pi.get_long("--ntrials"));
  bool verify     = static_cast<bool>(pi.get_flag("--verify"));
  bool stats      = static_cast<bool>(pi.get_flag("--stats"));
  bool warmup   = static_cast<bool>(pi.get_flag("--warmup"));
  int  dataset_sz = static_cast<int>(pi.get_long("--dataset-size"));

  // Choose filter mask

  int size = 0;
  byte* src;
  byte* mask;
  byte* ref;

  const char* image_name = pi.get_string("--mask");
  if ( strcmp( image_name, "reg" ) == 0 ) {
    size = size_reg;
    src  = src_reg;
    mask = mask_reg;
    ref  = ref_reg;
  }
  else if ( strcmp( image_name, "small" ) == 0 ) {
    size = size_small;
    src  = src_small;
    mask = mask_small;
    ref  = ref_small;
  }
  else if ( strcmp( image_name, "shot" ) == 0 ) {
    size = size_shot;
    src  = src_shot;
    mask = mask_shot;
    ref  = ref_shot;
  }
  else {
    std::cout
      << "\n ERROR: Unrecognized mask"
      << "(" << image_name << ")\n" << std::endl;
    return 1;
  }

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

  int nsquares = pi.get_long("--dataset-nsquares");
  const char* dump_dataset_fname = pi.get_string("--dump-dataset");
  if ( strcmp( dump_dataset_fname, "none" ) != 0 ) {
    dump_dataset( dump_dataset_fname, dataset_sz, nsquares, g_coeff );
    return 0;
  }

  // Verify the implementations

  if ( verify ) {

    std::cout << "\n Unit Tests : " << argv[0] << "\n" << std::endl;

    if ( !impl_all ) {
      std::vector<byte> dest(size*size,0x00u);
      impl_ptr->func_ptr( &dest[0], mask, src, size, size, g_coeff );
      verify_results( impl_ptr->str, &dest[0], ref, size );
    }
    else {
      Impl* impl_ptr = &impl_table[0];
      while ( impl_ptr->func_ptr != 0 ) {
        std::vector<byte> dest(size*size,0x00u);
        impl_ptr->func_ptr( &dest[0], mask, src, size, size, g_coeff );
        verify_results( impl_ptr->str, &dest[0], ref, size );
        impl_ptr++;
      }
    }

    std::cout << std::endl;
    return 0;
  }

  // Execute the micro-benchmark

  // HACK: dest now declared globally to force alignment.
  std::vector<byte> dest(size*size,0x00u);

  if ( warmup )
    impl_ptr->func_ptr( &dest[0], mask, src, size, size, g_coeff );

  stdx::Timer timer;
  timer.start();
  set_stats_en(true);

  for ( int i = 0; i < ntrials; i++ )
    impl_ptr->func_ptr( &dest[0], mask, src, size, size, g_coeff );

  set_stats_en(false);
  timer.stop();

  // Display stats

  if ( stats )
    std::cout << "runtime = " << timer.get_elapsed() << std::endl;

  // Dump images if desired

  if ( pi.get_flag("--dump-images") ) {
    dump_image( "ubmark-masked-filter-src.ppm",  src,        size );
    dump_image( "ubmark-masked-filter-mask.ppm", mask,       size );
    dump_image( "ubmark-masked-filter-dest.ppm", &dest[0], size );
  }

  // Return zero upon successful completion

  return 0;
}

