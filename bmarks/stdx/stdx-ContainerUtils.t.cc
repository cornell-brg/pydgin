//========================================================================
// stdx-ContainerUtils Unit Tests
//========================================================================

#include "stdx-ContainerUtils.h"
#include "utst.h"
#include <vector>
#include <list>
#include <string>

//------------------------------------------------------------------------
// TestAppendOperators
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestAppendOperators )
{
  std::vector<int> int_vec(4);
  int_vec.at(0) = 0;
  int_vec.at(1) = 1;
  int_vec.at(2) = 2;
  int_vec.at(3) = 3;

  std::vector<std::string> str_vec(4);
  str_vec.at(0) = "0";
  str_vec.at(1) = "1";
  str_vec.at(2) = "2";
  str_vec.at(3) = "3";

  std::vector<int> test_int_vec;
  test_int_vec += 0, 1, 2, 3;
  UTST_CHECK_CONT_EQ( test_int_vec, int_vec );

  std::list<int> test_int_list;
  test_int_list += 0, 1, 2, 3;
  UTST_CHECK_CONT_EQ( test_int_list, int_vec );

  std::vector<std::string> test_str_vec;
  test_str_vec += "0", "1", "2", "3";
  UTST_CHECK_CONT_EQ( test_str_vec, str_vec );

  std::list<std::string> test_str_list;
  test_str_list += "0", "1", "2", "3";
  UTST_CHECK_CONT_EQ( test_str_list, str_vec );
}

//------------------------------------------------------------------------
// TestMkContainer
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestMkContainer )
{
  using namespace std;

  UTST_CHECK_CONT_EQ( stdx::mk_vec<int>(),  std::vector<int>() );
  UTST_CHECK_CONT_EQ( stdx::mk_list<int>(), std::list<int>()   );

  std::vector<int> single_int_vec(1);
  single_int_vec.at(0) = 0;

  UTST_CHECK_CONT_EQ( stdx::mk_vec(0),  single_int_vec );
  UTST_CHECK_CONT_EQ( stdx::mk_list(0), single_int_vec );

  std::vector<int> int_vec(4);
  int_vec.at(0) = 0;
  int_vec.at(1) = 1;
  int_vec.at(2) = 2;
  int_vec.at(3) = 3;

  UTST_CHECK_CONT_EQ( stdx::mk_vec( 0, 1, 2, 3 ),  int_vec );
  UTST_CHECK_CONT_EQ( stdx::mk_list( 0, 1, 2, 3 ), int_vec );

  std::vector<std::string> single_str_vec(1);
  single_str_vec.at(0) = "0";

  UTST_CHECK_CONT_EQ( stdx::mk_vec<string>("0"),  single_str_vec );
  UTST_CHECK_CONT_EQ( stdx::mk_list<string>("0"), single_str_vec );

  std::vector<std::string> str_vec(4);
  str_vec.at(0) = "0";
  str_vec.at(1) = "1";
  str_vec.at(2) = "2";
  str_vec.at(3) = "3";

  UTST_CHECK_CONT_EQ( stdx::mk_vec<string>("0","1","2","3"),  str_vec );
  UTST_CHECK_CONT_EQ( stdx::mk_list<string>("0","1","2","3"), str_vec );
}

//------------------------------------------------------------------------
// TestMkContainerSeq
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestMkContainerSeq )
{
  using namespace std;

  std::vector<int> single_int_vec(1);
  single_int_vec.at(0) = 0;

  UTST_CHECK_CONT_EQ( stdx::mk_vec_seq(0,0),  single_int_vec );
  UTST_CHECK_CONT_EQ( stdx::mk_list_seq(0,0), single_int_vec );

  std::vector<int> int_vec(4);
  int_vec.at(0) = 0;
  int_vec.at(1) = 1;
  int_vec.at(2) = 2;
  int_vec.at(3) = 3;

  UTST_CHECK_CONT_EQ( stdx::mk_vec_seq(0,3),  int_vec );
  UTST_CHECK_CONT_EQ( stdx::mk_list_seq(0,3), int_vec );

  std::vector<char> single_char_vec(1);
  single_char_vec.at(0) = '0';

  UTST_CHECK_CONT_EQ( stdx::mk_vec_seq('0','0'),  single_char_vec );
  UTST_CHECK_CONT_EQ( stdx::mk_list_seq('0','0'), single_char_vec );

  std::vector<char> char_vec(4);
  char_vec.at(0) = '0';
  char_vec.at(1) = '1';
  char_vec.at(2) = '2';
  char_vec.at(3) = '3';

  UTST_CHECK_CONT_EQ( stdx::mk_vec_seq('0','3'),  char_vec );
  UTST_CHECK_CONT_EQ( stdx::mk_list_seq('0','3'), char_vec );
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv );
}

