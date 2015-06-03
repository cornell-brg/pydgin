//========================================================================
// stdx-MiscUtils : Miscellaneous classes and functions
//========================================================================

#ifndef STDX_MISC_UTILS_H
#define STDX_MISC_UTILS_H

#include <inttypes.h>
#include <iostream>
#include <iomanip>

namespace stdx {

  //----------------------------------------------------------------------
  // nl
  //----------------------------------------------------------------------
  // Newline io manipulator. One can use this instead of endl unless a
  // flush of the output stream is explicitly required.

  template < typename Ch, typename Tr >
  std::basic_ostream<Ch,Tr>& nl( std::basic_ostream<Ch,Tr>& os );

  //----------------------------------------------------------------------
  // extract_bit_field
  //----------------------------------------------------------------------
  // This is a simple function for extracting a bit field from a 32 bit
  // values. For example, let's assume we have two numbers (A and B)
  // that we want to pack into a single 32 bit value. Here is how we
  // might pack these two numbers:
  //
  //  |---- C ----|---- B ----|---- A ----|
  //
  // C is the field containing the bits not used by A and B. Let's
  // assume that A ranges from 0 to a_max and B ranges from 0 to b_max.
  // Here is how we can use the extract_bit_field() function to extract
  // these three fields:
  //
  //  int a_lsb = 0;
  //  int a_msb = lg(A) - 1;
  //
  //  int b_lsb = a_msb + 1;
  //  int b_msb = a_msb + lg(B);
  //
  //  int c_lsb = b_msb + 1;
  //  int c_msb = 31;
  //
  //  uint32_t a = extract_bit_field( bits, a_msb, a_lsb );
  //  uint32_t b = extract_bit_field( bits, b_msb, b_lsb );
  //  uint32_t c = extract_bit_field( bits, c_msb, c_lsb );
  //
  // If extracting bit fields is in our inner loop, we might want to use
  // the verify_bit_field() function first (ie. make sure that the msb
  // and lsb are valid) and then just use the extract_bit_field_fast()
  // function in the inner loop (which does not do the checks).
  //

  void verify_bit_field( int msb, int lsb );
  uint32_t extract_bit_field_fast( uint32_t bits, int msb, int lsb );
  uint32_t extract_bit_field( uint32_t bits, int msb, int lsb );
}

#include "stdx-MiscUtils.inl"
#endif /* STDX_MISC_UTILS_H */

