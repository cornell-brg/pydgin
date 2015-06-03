//========================================================================
// stdx-PairUtils Unit Tests
//========================================================================

#include "stdx-PairUtils.h"
#include "utst.h"

//------------------------------------------------------------------------
// TestMkPair
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestMkPair )
{
  using namespace std;

  std::pair<int,int> int_pair(42,42);
  UTST_CHECK_EQ( stdx::mk_pair(42,42), int_pair );

  std::pair<float,float> float_pair(42.0,42.0);
  UTST_CHECK_EQ( stdx::mk_pair(42.0f,42.0f), float_pair );

  std::pair<std::string,std::string> str_pair("A","B");
  UTST_CHECK_EQ( (stdx::mk_pair<string,string>("A","B")), str_pair );
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv );
}

