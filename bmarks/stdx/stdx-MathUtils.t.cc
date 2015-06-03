//========================================================================
// stdx-MathUtils Unit Tests
//========================================================================

#include "stdx-MathUtils.h"
#include "utst.h"

//------------------------------------------------------------------------
// TestFpClose
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestFpClose )
{
  UTST_CHECK( stdx::fp_close( 0.5,       0.5 ) );
  UTST_CHECK( stdx::fp_close( 0.5 + 0.5, 1.0 ) );

  UTST_CHECK( stdx::fp_close( 0.1,       0.1 ) );
  UTST_CHECK( stdx::fp_close( 0.1 + 0.1, 0.2 ) );

  UTST_CHECK( stdx::fp_close( 0.3,       0.3 ) );
  UTST_CHECK( stdx::fp_close( 0.3 + 0.3, 0.6 ) );

  UTST_CHECK( stdx::fp_close( 10000.5,           10000.5 ) );
  UTST_CHECK( stdx::fp_close( 10000.5 + 10000.5, 20001.0 ) );

  UTST_CHECK( stdx::fp_close( 10000.1,           10000.1 ) );
  UTST_CHECK( stdx::fp_close( 10000.1 + 10000.1, 20000.2 ) );

  UTST_CHECK( stdx::fp_close( 10000.3,           10000.3 ) );
  UTST_CHECK( stdx::fp_close( 10000.3 + 10000.3, 20000.6 ) );
}

//------------------------------------------------------------------------
// TestRound
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestRound )
{
  UTST_CHECK_EQ( stdx::round(0.0), 0 );
  UTST_CHECK_EQ( stdx::round(0.2), 0 );
  UTST_CHECK_EQ( stdx::round(0.4), 0 );
  UTST_CHECK_EQ( stdx::round(0.5), 1 );
  UTST_CHECK_EQ( stdx::round(0.6), 1 );
  UTST_CHECK_EQ( stdx::round(0.8), 1 );
  UTST_CHECK_EQ( stdx::round(1.0), 1 );
}

//------------------------------------------------------------------------
// TestIsPow2
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestIsPow2 )
{
  UTST_CHECK( !stdx::is_pow2(0) );
  UTST_CHECK(  stdx::is_pow2(1) );
  UTST_CHECK(  stdx::is_pow2(2) );
  UTST_CHECK( !stdx::is_pow2(3) );
  UTST_CHECK(  stdx::is_pow2(4) );
  UTST_CHECK( !stdx::is_pow2(5) );
  UTST_CHECK( !stdx::is_pow2(6) );
  UTST_CHECK( !stdx::is_pow2(7) );
  UTST_CHECK(  stdx::is_pow2(8) );
}

//------------------------------------------------------------------------
// TestCeilPow2
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestCeilPow2 )
{
  UTST_CHECK_EQ( stdx::ceil_pow2(0), 1u );
  UTST_CHECK_EQ( stdx::ceil_pow2(1), 1u );
  UTST_CHECK_EQ( stdx::ceil_pow2(2), 2u );
  UTST_CHECK_EQ( stdx::ceil_pow2(3), 4u );
  UTST_CHECK_EQ( stdx::ceil_pow2(4), 4u );
  UTST_CHECK_EQ( stdx::ceil_pow2(5), 8u );
  UTST_CHECK_EQ( stdx::ceil_pow2(6), 8u );
  UTST_CHECK_EQ( stdx::ceil_pow2(7), 8u );
  UTST_CHECK_EQ( stdx::ceil_pow2(8), 8u );
}


//------------------------------------------------------------------------
// TestLg
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestLg )
{
  UTST_CHECK_EQ( stdx::lg(  1), 0u );
  UTST_CHECK_EQ( stdx::lg(  2), 1u );
  UTST_CHECK_EQ( stdx::lg(  4), 2u );
  UTST_CHECK_EQ( stdx::lg(  8), 3u );
  UTST_CHECK_EQ( stdx::lg( 16), 4u );
  UTST_CHECK_EQ( stdx::lg( 32), 5u );
  UTST_CHECK_EQ( stdx::lg( 64), 6u );
  UTST_CHECK_EQ( stdx::lg(128), 7u );
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv );
}

