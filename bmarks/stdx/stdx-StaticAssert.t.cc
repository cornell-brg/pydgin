//========================================================================
// stdx-StaticAssert Unit Tests
//========================================================================
// We can't actually write tests which will fail since then our unit
// tests won't compile. So instead we have some examples which should
// compile fine, and then some tests which would fail but are commented
// out.

#include "stdx-StaticAssert.h"
#include "utst.h"
#include <string>
#include <vector>

//------------------------------------------------------------------------
// Example assertions
//------------------------------------------------------------------------

template < int a, int b >
struct TestClass {
  STDX_STATIC_ASSERT( a >= b )
  STDX_STATIC_ASSERT( !(a < b) )
};

//------------------------------------------------------------------------
// TestBasic
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestBasic )
{
  // These are valid instantiations of the template so they will compile
  // without error. We instantiate and then use the example class to
  // avoid "unused variable" warnings.

  TestClass<2,1> test1; TestClass<2,1> test1a = test1;
  TestClass<2,2> test2; TestClass<2,2> test2a = test2;

  // This is an invalid instantiation of the template so it will not
  // compile. We have commented it out so that the unit test can pass.
  //
  // TestClass<2,3> test3;
  //
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv );
}

