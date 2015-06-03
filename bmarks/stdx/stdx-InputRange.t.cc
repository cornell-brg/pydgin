//========================================================================
// stdx-InputRange Unit Tests
//========================================================================

#include "stdx-InputRange.h"
#include "utst.h"
#include <vector>
#include <algorithm>
#include <functional>

//------------------------------------------------------------------------
// TestBasic
//------------------------------------------------------------------------
// We are not trying to test all the standard overloaded algorithms but
// we are just making sure that creating and using input ranges works.

UTST_AUTO_TEST_CASE( TestBasic )
{
  using namespace stdx;
  using namespace std;

  vector<int> int_vec(5);
  int_vec.at(0) = 0;
  int_vec.at(1) = 1;
  int_vec.at(2) = 2;
  int_vec.at(3) = 3;
  int_vec.at(4) = 4;

  vector<int> copy_vec;
  copy( mk_irange(int_vec), back_inserter(copy_vec) );
  UTST_CHECK_CONT_EQ( copy_vec, int_vec );

  vector<int> rotated_vec(5);
  rotated_vec.at(0) = 3;
  rotated_vec.at(1) = 4;
  rotated_vec.at(2) = 0;
  rotated_vec.at(3) = 1;
  rotated_vec.at(4) = 2;

  rotate( mk_irange(copy_vec), copy_vec.begin()+3 );
  UTST_CHECK_CONT_EQ( copy_vec, rotated_vec );

  sort( mk_irange(copy_vec) );
  UTST_CHECK_CONT_EQ( copy_vec, int_vec );
}

//------------------------------------------------------------------------
// TestCopyIf
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestCopyIf )
{
  using namespace std;
  using namespace stdx;

  vector<int> input_vec(5);
  input_vec.at(0) = 0;
  input_vec.at(1) = 1;
  input_vec.at(2) = 2;
  input_vec.at(3) = 3;
  input_vec.at(4) = 4;

  vector<int> test_vec;
  copy_if( input_vec.begin(), input_vec.end(), back_inserter(test_vec),
           bind2nd(greater<int>(),2) );

  vector<int> correct_vec(2);
  correct_vec.at(0) = 3;
  correct_vec.at(1) = 4;

  UTST_CHECK_CONT_EQ( test_vec, correct_vec );
}

//------------------------------------------------------------------------
// TestEqual
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestEqual )
{
  using namespace std;
  using namespace stdx;

  vector<int> vec, copy_vec;
  generate_n( back_inserter(vec), 10, rand );
  copy( mk_irange(vec), back_inserter(copy_vec) );
  UTST_CHECK( equal( mk_irange(copy_vec), mk_irange(vec) ) );
}

//------------------------------------------------------------------------
// TestBooleanReduce
//------------------------------------------------------------------------

struct bool_identity {
  bool operator()( bool value ) { return value; }
};

UTST_AUTO_TEST_CASE( TestBooleanReduce )
{
  using namespace std;
  using namespace stdx;

  vector<bool> vec(2);
  vec.at(0) = true;
  vec.at(1) = true;

  UTST_CHECK_EQ( reduce_or( mk_irange(vec), bool_identity() ),  true );
  UTST_CHECK_EQ( reduce_and( mk_irange(vec), bool_identity() ), true );

  vec.at(0) = true;
  vec.at(1) = false;

  UTST_CHECK_EQ( reduce_or( mk_irange(vec), bool_identity() ),  true  );
  UTST_CHECK_EQ( reduce_and( mk_irange(vec), bool_identity() ), false );

  vec.at(0) = false;
  vec.at(1) = false;

  UTST_CHECK_EQ( reduce_or( mk_irange(vec), bool_identity() ),  false );
  UTST_CHECK_EQ( reduce_and( mk_irange(vec), bool_identity() ), false );
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv );
}

