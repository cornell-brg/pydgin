//========================================================================
// stdx-MathUtils : Math utility functions
//========================================================================
// This header provides a few math utility fractions for generating
// random numbers, testing the equality of floating point numbers, and
// manipulating powers of two.

#ifndef STDX_MATH_UTILS_H
#define STDX_MATH_UTILS_H

#include <inttypes.h>

namespace stdx {

  //----------------------------------------------------------------------
  // rand_frac
  //----------------------------------------------------------------------
  // Produces a random value between 0 and 1 (including 0 and not
  // including 1).

  double rand_frac();

  //----------------------------------------------------------------------
  // rand_int
  //----------------------------------------------------------------------
  // Produces a random integer from 0 to max-1. This is supposedly more
  // random than just using rand() % max which can have a very regular
  // pattern in the low order bits.

  int rand_int( int max );

  //----------------------------------------------------------------------
  // fp_close
  //----------------------------------------------------------------------
  // Floating point equality. Checks to see if given input arguments are
  // "close enough" to consider equal. User specifies the maximum allowed
  // absolute error and the maximum allowed relative error. This function
  // is templated so it works with both floats and doubles without
  // casting to one or the other.

  template < typename T >
  bool fp_close( T num0, T num1,
                 T max_abs_error = static_cast<T>(0.00001),
                 T max_rel_error = static_cast<T>(0.00001) );

  //----------------------------------------------------------------------
  // round
  //----------------------------------------------------------------------
  // Rounds double to nearest integer

  int round( double d );

  //----------------------------------------------------------------------
  // is_pow2
  //----------------------------------------------------------------------
  // Returns true if value is power of two otherwise returns false

  bool is_pow2( uint32_t num );

  //----------------------------------------------------------------------
  // ceil_pow2()
  //----------------------------------------------------------------------
  // Round up to the nearest power of two. If the given val is already a
  // power of two then do nothing.

  uint32_t ceil_pow2( uint32_t num );

  //----------------------------------------------------------------------
  // lg()
  //----------------------------------------------------------------------
  // Return the log base two of the given value. This function assumes
  // the input is a power of two.

  uint32_t lg( uint32_t num );

}

#include "stdx-MathUtils.inl"
#endif /* STDX_MATH_UTILS_H */

