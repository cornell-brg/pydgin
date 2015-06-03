//========================================================================
// stdx-MiscUtils Unit Tests
//========================================================================

#include "stdx-MiscUtils.h"
#include "utst.h"
#include <vector>

//------------------------------------------------------------------------
// TestExtractBitField
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestExtractBitField )
{
  //      28   24   20   16   12    8    4    0
  // 0b_1111_1111_1110_1110_1101_1101_1100_1100
  uint32_t bits = 0xffeeddcc;

  UTST_CHECK_EQ( 0xffeeddccu, stdx::extract_bit_field( bits, 31, 0 ) );

  UTST_CHECK_EQ( 0x0000ffeeu, stdx::extract_bit_field( bits, 31, 16) );
  UTST_CHECK_EQ( 0x000000ffu, stdx::extract_bit_field( bits, 31, 24) );
  UTST_CHECK_EQ( 0x00000001u, stdx::extract_bit_field( bits, 31, 31) );

  UTST_CHECK_EQ( 0x0000ddccu, stdx::extract_bit_field( bits, 15, 0 ) );
  UTST_CHECK_EQ( 0x000000ccu, stdx::extract_bit_field( bits,  7, 0 ) );
  UTST_CHECK_EQ( 0x00000000u, stdx::extract_bit_field( bits,  0, 0 ) );

  UTST_CHECK_EQ( 0x00000003u, stdx::extract_bit_field( bits, 20, 18) );
  UTST_CHECK_EQ( 0x00000005u, stdx::extract_bit_field( bits, 17, 15) );
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv );
}

