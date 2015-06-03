//========================================================================
// stdx-PreprocessorUtils Unit Tests
//========================================================================

#include "stdx-PreprocessorUtils.h"
#include "utst.h"
#include <vector>
#include <list>

//------------------------------------------------------------------------
// gen_vec
//------------------------------------------------------------------------
// This helper functions fills a vector with an increasing sequence of
// integers. It is useful for generating reference vectors.

std::vector<int> gen_vec( int size )
{
  std::vector<int> vec(size);
  for ( int i = 0; i < size; i++ )
    vec.at(i) = i;
  return vec;
}

//------------------------------------------------------------------------
// TestConcat
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestConcat )
{
  // Concatenate var and 0 to create var0

  int STDX_PP_CONCAT( var, 0 ) = 12;
  UTST_CHECK_EQ( var0, 12 );

  // Check with one level of required expansion

  #define TEST_CONCAT_0 var
  #define TEST_CONCAT_1 1
  int STDX_PP_CONCAT( TEST_CONCAT_0, TEST_CONCAT_1 ) = 22;
  UTST_CHECK_EQ( var1, 22 );

  // Check with two levels of required expansion

  #define TEST_CONCAT_2 TEST_CONCAT_0
  int STDX_PP_CONCAT( TEST_CONCAT_2, 2 ) = 32;
  UTST_CHECK_EQ( var2, 32 );

  // Check with three levels of required expansion

  #define TEST_CONCAT_3 TEST_CONCAT_2
  int STDX_PP_CONCAT( TEST_CONCAT_3, 3 ) = 42;
  UTST_CHECK_EQ( var3, 42 );

  // Check nested concats

  #define TEST_CONCAT_4 multi
  #define TEST_CONCAT_5 concat
  int STDX_PP_CONCAT(
        STDX_PP_CONCAT( TEST_CONCAT_3, _ ),
        STDX_PP_CONCAT( TEST_CONCAT_4, TEST_CONCAT_5 ) ) = 52;

  UTST_CHECK_EQ( var_multiconcat, 52 );

  // Check concat with more than 2 arguments

  int STDX_PP_CONCAT2( var, 4 ) = 62;
  UTST_CHECK_EQ( var4, 62 );

  int STDX_PP_CONCAT3( var, 4, a ) = 72;
  UTST_CHECK_EQ( var4a, 72 );

  int STDX_PP_CONCAT4( var, 4, a, b ) = 82;
  UTST_CHECK_EQ( var4ab, 82 );

  int STDX_PP_CONCAT5( var, 4, a, b, c ) = 92;
  UTST_CHECK_EQ( var4abc, 92 );
}

//------------------------------------------------------------------------
// TestStringify
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestStringify )
{
  // Stringify token

  UTST_CHECK_EQ( STDX_PP_STRINGIFY( foo ), "foo" );

  // Check with one level of required expansion

  #define TEST_STRINGIFY_0 foo
  UTST_CHECK_EQ( STDX_PP_STRINGIFY( TEST_STRINGIFY_0 ), "foo" );

  // Check with two levels of required expansion

  #define TEST_STRINGIFY_1 TEST_STRINGIFY_0
  UTST_CHECK_EQ( STDX_PP_STRINGIFY( TEST_STRINGIFY_1 ), "foo" );

  // Check with three levels of required expansion

  #define TEST_STRINGIFY_2 TEST_STRINGIFY_1
  UTST_CHECK_EQ( STDX_PP_STRINGIFY( TEST_STRINGIFY_2 ), "foo" );
}

//------------------------------------------------------------------------
// TestLogic
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestLogic )
{
  // Check number to bool conversion

  UTST_CHECK_EQ( STDX_PP_NUM_TO_BOOL(0),  0 );
  UTST_CHECK_EQ( STDX_PP_NUM_TO_BOOL(1),  1 );
  UTST_CHECK_EQ( STDX_PP_NUM_TO_BOOL(2),  1 );
  UTST_CHECK_EQ( STDX_PP_NUM_TO_BOOL(3),  1 );
  UTST_CHECK_EQ( STDX_PP_NUM_TO_BOOL(32), 1 );

  // Check logical and

  UTST_CHECK_EQ( STDX_PP_AND(0,0), 0 );
  UTST_CHECK_EQ( STDX_PP_AND(0,1), 0 );
  UTST_CHECK_EQ( STDX_PP_AND(1,0), 0 );
  UTST_CHECK_EQ( STDX_PP_AND(1,1), 1 );

  UTST_CHECK_EQ( STDX_PP_AND(0,0), 0 );
  UTST_CHECK_EQ( STDX_PP_AND(0,2), 0 );
  UTST_CHECK_EQ( STDX_PP_AND(2,0), 0 );
  UTST_CHECK_EQ( STDX_PP_AND(2,2), 1 );

  // Check logical or

  UTST_CHECK_EQ( STDX_PP_OR(0,0), 0 );
  UTST_CHECK_EQ( STDX_PP_OR(0,1), 1 );
  UTST_CHECK_EQ( STDX_PP_OR(1,0), 1 );
  UTST_CHECK_EQ( STDX_PP_OR(1,1), 1 );

  UTST_CHECK_EQ( STDX_PP_OR(0,0), 0 );
  UTST_CHECK_EQ( STDX_PP_OR(0,2), 1 );
  UTST_CHECK_EQ( STDX_PP_OR(2,0), 1 );
  UTST_CHECK_EQ( STDX_PP_OR(2,2), 1 );

  // Test nested logic

  #define TEST_LOGIC_0 0
  #define TEST_LOGIC_1 1
  #define TEST_LOGIC_2 0
  #define TEST_LOGIC_3 1

  bool res_0
    = ((TEST_LOGIC_0 || TEST_LOGIC_1) && (TEST_LOGIC_2 || TEST_LOGIC_3));

  #define TEST_LOGIC_RES_0 \
    STDX_PP_AND( STDX_PP_OR( TEST_LOGIC_0, TEST_LOGIC_1 ), \
                 STDX_PP_OR( TEST_LOGIC_2, TEST_LOGIC_3 ) )

  UTST_CHECK_EQ( TEST_LOGIC_RES_0, res_0 );

  bool res_1
    = ((TEST_LOGIC_0 && TEST_LOGIC_1) || (TEST_LOGIC_2 && TEST_LOGIC_3));

  #define TEST_LOGIC_RES_1 \
    STDX_PP_OR( STDX_PP_AND( TEST_LOGIC_0, TEST_LOGIC_1 ), \
                STDX_PP_AND( TEST_LOGIC_2, TEST_LOGIC_3 ) )

  UTST_CHECK_EQ( TEST_LOGIC_RES_1, res_1 );
}

//------------------------------------------------------------------------
// TestIf
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestIf )
{
  // Check with literal true/false expressions

  UTST_CHECK_EQ( STDX_PP_IF(  0, true, false ), false );
  UTST_CHECK_EQ( STDX_PP_IF(  1, true, false ), true  );
  UTST_CHECK_EQ( STDX_PP_IF(  2, true, false ), true  );
  UTST_CHECK_EQ( STDX_PP_IF(  3, true, false ), true  );
  UTST_CHECK_EQ( STDX_PP_IF( 32, true, false ), true  );

  // Check with macro arguments

  #define TEST_IF_0  0
  #define TEST_IF_1  1
  #define TEST_IF_2  2
  #define TEST_IF_3  3
  #define TEST_IF_32 32

  #define TEST_IF_T true
  #define TEST_IF_F false

  UTST_CHECK_EQ( STDX_PP_IF( TEST_IF_0,  TEST_IF_T, TEST_IF_F ), false );
  UTST_CHECK_EQ( STDX_PP_IF( TEST_IF_1,  TEST_IF_T, TEST_IF_F ), true  );
  UTST_CHECK_EQ( STDX_PP_IF( TEST_IF_2,  TEST_IF_T, TEST_IF_F ), true  );
  UTST_CHECK_EQ( STDX_PP_IF( TEST_IF_3,  TEST_IF_T, TEST_IF_F ), true  );
  UTST_CHECK_EQ( STDX_PP_IF( TEST_IF_32, TEST_IF_T, TEST_IF_F ), true  );
}

//------------------------------------------------------------------------
// TestCommaIf
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestCommaIf )
{
  // Check with literal true/false expressions

  int a1 = 1 STDX_PP_COMMA_IF(1) a2  = 2  STDX_PP_COMMA_IF(2)
      a3 = 3 STDX_PP_COMMA_IF(3) a32 = 32 STDX_PP_COMMA_IF(32)
      a0 = 0 STDX_PP_COMMA_IF(0);

  UTST_CHECK_EQ( a0,  0  );
  UTST_CHECK_EQ( a1,  1  );
  UTST_CHECK_EQ( a2,  2  );
  UTST_CHECK_EQ( a3,  3  );
  UTST_CHECK_EQ( a32, 32 );

  // Check with macro arguments

  #define TEST_COMMA_IF_0  0
  #define TEST_COMMA_IF_1  1
  #define TEST_COMMA_IF_2  2
  #define TEST_COMMA_IF_3  3
  #define TEST_COMMA_IF_32 32

  int b1  = 1  STDX_PP_COMMA_IF(TEST_COMMA_IF_1)
      b2  = 2  STDX_PP_COMMA_IF(TEST_COMMA_IF_2)
      b3  = 3  STDX_PP_COMMA_IF(TEST_COMMA_IF_3)
      b32 = 32 STDX_PP_COMMA_IF(TEST_COMMA_IF_32)
      b0  = 0  STDX_PP_COMMA_IF(TEST_COMMA_IF_0);

  UTST_CHECK_EQ( b0,  0  );
  UTST_CHECK_EQ( b1,  1  );
  UTST_CHECK_EQ( b2,  2  );
  UTST_CHECK_EQ( b3,  3  );
  UTST_CHECK_EQ( b32, 32 );
}

//------------------------------------------------------------------------
// TestLoop
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestLoop )
{
  // Loop with zero iterations

  std::vector<int> vec_0;
  #define TEST_LOOP_LB0( count_ ) \
    vec_0.push_back( count_ );
  STDX_PP_LOOP( 0, TEST_LOOP_LB0 );
  UTST_CHECK_CONT_EQ( gen_vec(0), vec_0 );

  // Loop with one iteration

  std::vector<int> vec_1;
  #define TEST_LOOP_LB1( count_ ) \
    vec_1.push_back( count_ );
  STDX_PP_LOOP( 1, TEST_LOOP_LB1 );
  UTST_CHECK_CONT_EQ( gen_vec(1), vec_1 );

  // Loop with three iterations

  std::vector<int> vec_2;
  #define TEST_LOOP_LB2( count_ ) \
    vec_2.push_back( count_ );
  STDX_PP_LOOP( 3, TEST_LOOP_LB2 );
  UTST_CHECK_CONT_EQ( gen_vec(3), vec_2 );

  // Loop with 32 iterations

  std::vector<int> vec_3;
  #define TEST_LOOP_LB3( count_ ) \
    vec_3.push_back( count_ );
  STDX_PP_LOOP( 32, TEST_LOOP_LB3 );
  UTST_CHECK_CONT_EQ( gen_vec(32), vec_3 );

  // Loop with three iterations and extra arguments

  std::vector<int> vec_4;
  #define TEST_LOOP_LB4( count_, vecname_ ) \
    vecname_.push_back( count_ );
  STDX_PP_LOOP( 3, TEST_LOOP_LB4, vec_4 );
  UTST_CHECK_CONT_EQ( gen_vec(3), vec_4 );

  // Nested loops

  std::vector<int> vec_5;

  #define TEST_LOOP_LB5_INNER( count_, outer_count_ ) \
    vec_5.push_back( outer_count_*2 + count_ );

  #define TEST_LOOP_LB5_OUTER( count_ ) \
    STDX_PP_LOOP_X1( 2, TEST_LOOP_LB5_INNER, count_ )

  STDX_PP_LOOP( 3, TEST_LOOP_LB5_OUTER );
  UTST_CHECK_CONT_EQ( gen_vec(6), vec_5 );
}

//------------------------------------------------------------------------
// TestLoopComma
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestLoopComma )
{
  #define TEST_LOOP_COMMA_LB0( count_ ) count_

  // Loop with zero iterations (should expand to nothing)

  STDX_PP_LOOP_C( 0, TEST_LOOP_COMMA_LB0 )

  // Loop with one iteration

  int vec_1[] = { STDX_PP_LOOP_C( 1, TEST_LOOP_COMMA_LB0 ) };
  std::vector<int> vec_ref_1 = gen_vec(1);
  for ( int i = 0; i < 1; i++ )
    UTST_CHECK_EQ( vec_1[i], vec_ref_1.at(i) );

  // Loop with three iterations

  int vec_2[] = { STDX_PP_LOOP_C( 3, TEST_LOOP_COMMA_LB0 ) };
  std::vector<int> vec_ref_2 = gen_vec(3);
  for ( int i = 0; i < 3; i++ )
    UTST_CHECK_EQ( vec_2[i], vec_ref_2.at(i) );

  // Loop with 32 iterations

  int vec_3[] = { STDX_PP_LOOP_C( 32, TEST_LOOP_COMMA_LB0 ) };
  std::vector<int> vec_ref_3 = gen_vec(32);
  for ( int i = 0; i < 32; i++ )
    UTST_CHECK_EQ( vec_3[i], vec_ref_3.at(i) );

  // Loop with three iterations and extra arguments

  #define TEST_LOOP_COMMA_LB1( count_, offset_ ) count_ + offset_

  int vec_4[] = { STDX_PP_LOOP_C( 3, TEST_LOOP_COMMA_LB1, 1 ) };
  std::vector<int> vec_ref_4 = gen_vec(3);
  for ( int i = 0; i < 3; i++ )
    UTST_CHECK_EQ( vec_4[i], vec_ref_4.at(i) + 1 );

  // Nested loops

  #define TEST_LOOP_COMMA_LB2_INNER( count_, outer_count_ ) \
    outer_count_*2 + count_

  #define TEST_LOOP_COMMA_LB2_OUTER( count_ ) \
    STDX_PP_LOOP_C_X1( 2, TEST_LOOP_COMMA_LB2_INNER, count_ )

  int vec_5[] = { STDX_PP_LOOP_C( 3, TEST_LOOP_COMMA_LB2_OUTER ) };
  std::vector<int> vec_ref_5 = gen_vec(6);
  for ( int i = 0; i < 6; i++ )
    UTST_CHECK_EQ( vec_5[i], vec_ref_5.at(i) );
}

//------------------------------------------------------------------------
// TestEnumParams
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestEnumParams )
{
  // Loop with zero iterations (should expand to nothing)

  STDX_PP_ENUM_PARAMS( 0, 0 )

  // Loop with one iteration

  int vec_1[] = { STDX_PP_ENUM_PARAMS( 1, 0x ) };
  std::vector<int> vec_ref_1 = gen_vec(1);
  for ( int i = 0; i < 1; i++ )
    UTST_CHECK_EQ( vec_1[i], vec_ref_1.at(i) );

  // Loop with three iterations

  int vec_2[] = { STDX_PP_ENUM_PARAMS( 3, 0x ) };
  std::vector<int> vec_ref_2 = gen_vec(3);
  for ( int i = 0; i < 3; i++ )
    UTST_CHECK_EQ( vec_2[i], vec_ref_2.at(i) );

  // Nested loops

  #define TEST_ENUM_PARAMS_LB0( count_ ) \
    STDX_PP_ENUM_PARAMS( 3, 0x )

  int vec_4[] = { STDX_PP_LOOP( 1, TEST_ENUM_PARAMS_LB0 ) };
  std::vector<int> vec_ref_4 = gen_vec(3);
  for ( int i = 0; i < 3; i++ )
    UTST_CHECK_EQ( vec_4[i], vec_ref_4.at(i) );
}

//------------------------------------------------------------------------
// TestListBasic
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestListBasic )
{
  // Create a list directly and test with at

  #define TEST_LIST_BASIC_0 (0,1,2)

  UTST_CHECK_EQ( STDX_PP_LIST_SIZE( TEST_LIST_BASIC_0 ), 3 );
  UTST_CHECK_EQ( STDX_PP_LIST_AT( TEST_LIST_BASIC_0, 0 ), 0 );
  UTST_CHECK_EQ( STDX_PP_LIST_AT( TEST_LIST_BASIC_0, 1 ), 1 );
  UTST_CHECK_EQ( STDX_PP_LIST_AT( TEST_LIST_BASIC_0, 2 ), 2 );
}

//------------------------------------------------------------------------
// TestListSize
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestListSize )
{
  // Check tricky zero item case

  UTST_CHECK_EQ( STDX_PP_LIST_SIZE( () ), 0 );

  // Check small numbers of list sizes

  UTST_CHECK_EQ( STDX_PP_LIST_SIZE(( a                   )), 1 );
  UTST_CHECK_EQ( STDX_PP_LIST_SIZE(( a, b                )), 2 );
  UTST_CHECK_EQ( STDX_PP_LIST_SIZE(( a, b, c             )), 3 );
  UTST_CHECK_EQ( STDX_PP_LIST_SIZE(( a, b, c, d          )), 4 );
  UTST_CHECK_EQ( STDX_PP_LIST_SIZE(( a, b, c, d, e       )), 5 );
  UTST_CHECK_EQ( STDX_PP_LIST_SIZE(( a, b, c, d, e, f    )), 6 );
  UTST_CHECK_EQ( STDX_PP_LIST_SIZE(( a, b, c, d, e, f, g )), 7 );

  // Check when list is itself a macro

  #define TEST_LIST_SIZE_0 ( )
  #define TEST_LIST_SIZE_1 ( a )
  #define TEST_LIST_SIZE_2 ( a, b )
  #define TEST_LIST_SIZE_3 ( a, b, c )
  #define TEST_LIST_SIZE_4 ( a, b, c, d )
  #define TEST_LIST_SIZE_5 ( a, b, c, d, e )
  #define TEST_LIST_SIZE_6 ( a, b, c, d, e, f )
  #define TEST_LIST_SIZE_7 ( a, b, c, d, e, f, g )

  UTST_CHECK_EQ( STDX_PP_LIST_SIZE( TEST_LIST_SIZE_0 ), 0 );
  UTST_CHECK_EQ( STDX_PP_LIST_SIZE( TEST_LIST_SIZE_1 ), 1 );
  UTST_CHECK_EQ( STDX_PP_LIST_SIZE( TEST_LIST_SIZE_2 ), 2 );
  UTST_CHECK_EQ( STDX_PP_LIST_SIZE( TEST_LIST_SIZE_3 ), 3 );
  UTST_CHECK_EQ( STDX_PP_LIST_SIZE( TEST_LIST_SIZE_4 ), 4 );
  UTST_CHECK_EQ( STDX_PP_LIST_SIZE( TEST_LIST_SIZE_5 ), 5 );
  UTST_CHECK_EQ( STDX_PP_LIST_SIZE( TEST_LIST_SIZE_6 ), 6 );
  UTST_CHECK_EQ( STDX_PP_LIST_SIZE( TEST_LIST_SIZE_7 ), 7 );

  // Check when two levels of expansions is required

  #define TEST_LIST_SIZE_7a TEST_LIST_SIZE_7
  UTST_CHECK_EQ( STDX_PP_LIST_SIZE( TEST_LIST_SIZE_7a ), 7 );

  // Check the max size of 32

  #define TEST_LIST_SIZE_32                                           \
    ( 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, \
      15, 14, 13, 12, 11, 10,  9,  8,  7,  6,  5,  4,  3,  2,  1,  0 )

  UTST_CHECK_EQ( STDX_PP_LIST_SIZE( TEST_LIST_SIZE_32 ), 32 );
}

//------------------------------------------------------------------------
// TestListPushFirstRest
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestListPushFirstRest )
{
  // Create a list directly and test with at

  #define TEST_LIST_PFR_0 (0,1,2)

  UTST_CHECK_EQ( STDX_PP_LIST_SIZE( TEST_LIST_PFR_0 ), 3 );
  UTST_CHECK_EQ( STDX_PP_LIST_AT( TEST_LIST_PFR_0, 0 ), 0 );
  UTST_CHECK_EQ( STDX_PP_LIST_AT( TEST_LIST_PFR_0, 1 ), 1 );
  UTST_CHECK_EQ( STDX_PP_LIST_AT( TEST_LIST_PFR_0, 2 ), 2 );

  // Create a list with push and test with at

  #define TEST_LIST_PFR_1a STDX_PP_LIST_EMPTY
  #define TEST_LIST_PFR_1b STDX_PP_LIST_PUSH( TEST_LIST_PFR_1a, 2 )
  #define TEST_LIST_PFR_1c STDX_PP_LIST_PUSH( TEST_LIST_PFR_1b, 1 )
  #define TEST_LIST_PFR_1  STDX_PP_LIST_PUSH( TEST_LIST_PFR_1c, 0 )

  UTST_CHECK_EQ( STDX_PP_LIST_SIZE( TEST_LIST_PFR_1 ), 3 );
  UTST_CHECK_EQ( STDX_PP_LIST_AT( TEST_LIST_PFR_1, 0 ), 0 );
  UTST_CHECK_EQ( STDX_PP_LIST_AT( TEST_LIST_PFR_1, 1 ), 1 );
  UTST_CHECK_EQ( STDX_PP_LIST_AT( TEST_LIST_PFR_1, 2 ), 2 );

  // Test first and rest

  #define TEST_LIST_PFR_0 (0,1,2)
  #define TEST_LIST_PFR_REST_0a \
    STDX_PP_LIST_REST( TEST_LIST_PFR_0 )

  UTST_CHECK_EQ( STDX_PP_LIST_SIZE( TEST_LIST_PFR_REST_0a ), 2 );
  UTST_CHECK_EQ( STDX_PP_LIST_FIRST( TEST_LIST_PFR_REST_0a), 1 );
  UTST_CHECK_EQ( STDX_PP_LIST_AT( TEST_LIST_PFR_REST_0a, 0 ), 1 );
  UTST_CHECK_EQ( STDX_PP_LIST_AT( TEST_LIST_PFR_REST_0a, 1 ), 2 );

  #define TEST_LIST_PFR_REST_0b \
    STDX_PP_LIST_REST( TEST_LIST_PFR_REST_0a )

  UTST_CHECK_EQ( STDX_PP_LIST_SIZE( TEST_LIST_PFR_REST_0b ), 1 );
  UTST_CHECK_EQ( STDX_PP_LIST_FIRST( TEST_LIST_PFR_REST_0b ), 2 );
  UTST_CHECK_EQ( STDX_PP_LIST_AT( TEST_LIST_PFR_REST_0b, 0 ), 2 );

  #define TEST_LIST_PFR_REST_0c \
    STDX_PP_LIST_REST( TEST_LIST_PFR_REST_0b )

  UTST_CHECK_EQ( STDX_PP_LIST_SIZE( TEST_LIST_PFR_REST_0c ), 0 );
  STDX_PP_LIST_FIRST( TEST_LIST_PFR_REST_0c ) // evals to nothing

  #define TEST_LIST_PFR_REST_0d \
    STDX_PP_LIST_REST( TEST_LIST_PFR_REST_0c )

  UTST_CHECK_EQ( STDX_PP_LIST_SIZE( TEST_LIST_PFR_REST_0d ), 0 );
}

//------------------------------------------------------------------------
// TestListAppend
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestListAppend )
{

  // Test list append with two elements each

  #define TEST_LIST_APPEND_0a (0,1)
  #define TEST_LIST_APPEND_0b (2,3)
  #define TEST_LIST_APPEND_0c \
    STDX_PP_LIST_APPEND( TEST_LIST_APPEND_0a, TEST_LIST_APPEND_0b )

  int vec_0[] = { STDX_PP_STRIP_PAREN( TEST_LIST_APPEND_0c ) };
  std::vector<int> vec_ref_0 = gen_vec(4);
  for ( int i = 0; i < 4; i++ )
    UTST_CHECK_EQ( vec_0[i], vec_ref_0.at(i) );

  // Test list append with empty first list

  #define TEST_LIST_APPEND_1a ()
  #define TEST_LIST_APPEND_1b (0,1)
  #define TEST_LIST_APPEND_1c \
    STDX_PP_LIST_APPEND( TEST_LIST_APPEND_1a, TEST_LIST_APPEND_1b )

  int vec_1[] = { STDX_PP_STRIP_PAREN( TEST_LIST_APPEND_1c ) };
  std::vector<int> vec_ref_1 = gen_vec(2);
  for ( int i = 0; i < 2; i++ )
    UTST_CHECK_EQ( vec_1[i], vec_ref_1.at(i) );

  // Test list append with empty second list

  #define TEST_LIST_APPEND_2a (0,1)
  #define TEST_LIST_APPEND_2b ()
  #define TEST_LIST_APPEND_2c \
    STDX_PP_LIST_APPEND( TEST_LIST_APPEND_2a, TEST_LIST_APPEND_2b )

  int vec_2[] = { STDX_PP_STRIP_PAREN( TEST_LIST_APPEND_2c ) };
  std::vector<int> vec_ref_2 = gen_vec(2);
  for ( int i = 0; i < 2; i++ )
    UTST_CHECK_EQ( vec_2[i], vec_ref_2.at(i) );
}

//------------------------------------------------------------------------
// TestListMap
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestListMap )
{
  // Map with zero iterations (should eval to nothing)

  STDX_PP_LIST_MAP( (), TEST_LIST_MAP_LB0 )

  // Map with one iteration

  std::vector<int> vec_0(1);
  #define TEST_LIST_MAP_LB0( count_, item_ ) \
    vec_0.at(count_) = count_ + item_;
  STDX_PP_LIST_MAP( (1), TEST_LIST_MAP_LB0 );
  UTST_CHECK_EQ( vec_0[0], 1 );

  // Map with three iterations

  std::vector<int> vec_1(3);
  #define TEST_LIST_MAP_LB1( count_, item_ ) \
    vec_1.at(count_) = count_ + item_;
  STDX_PP_LIST_MAP( (1,2,3), TEST_LIST_MAP_LB1 );

  std::vector<int> vec_ref_1 = gen_vec(3);
  for ( int i = 0; i < 3; i++ )
    UTST_CHECK_EQ( vec_1[i], vec_ref_1.at(i) + (i+1) );

  // Map with 32 iterations

  #define TEST_LIST_MAP_0                                             \
    (  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, \
      17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32 )

  std::vector<int> vec_2(32);
  #define TEST_LIST_MAP_LB2( count_, item_ ) \
    vec_2.at(count_) = count_ + item_;
  STDX_PP_LIST_MAP( TEST_LIST_MAP_0, TEST_LIST_MAP_LB2 );

  std::vector<int> vec_ref_2 = gen_vec(32);
  for ( int i = 0; i < 32; i++ )
    UTST_CHECK_EQ( vec_2[i], vec_ref_2.at(i) + (i+1) );

  // Loop with three iterations and extra arguments

  std::vector<int> vec_3(3);
  #define TEST_LIST_MAP_LB3( count_, item_, offset_ ) \
    vec_3.at(count_) = count_ + item_ + offset_;
  STDX_PP_LIST_MAP( (1,2,3), TEST_LIST_MAP_LB3, 1 );

  std::vector<int> vec_ref_3 = gen_vec(3);
  for ( int i = 0; i < 3; i++ )
    UTST_CHECK_EQ( vec_3[i], vec_ref_3.at(i) + (i+1) + 1 );

  // Nested loops

  std::vector<int> vec_4(6);

  #define TEST_LIST_MAP_LB4_INNER( count_, item_, outer_item_ )         \
    vec_4.at((outer_item_-1)*2 + (item_-1))                             \
      = (outer_item_-1)*2 + (item_-1);

  #define TEST_LIST_MAP_LB4_OUTER( count_, item_ ) \
    STDX_PP_LIST_MAP_X1( (1,2), TEST_LIST_MAP_LB4_INNER, item_ )

  STDX_PP_LIST_MAP( (1,2,3), TEST_LIST_MAP_LB4_OUTER );

  std::vector<int> vec_ref_4 = gen_vec(6);
  for ( int i = 0; i < 6; i++ )
    UTST_CHECK_EQ( vec_4[i], vec_ref_4.at(i) );
}

//------------------------------------------------------------------------
// TestListMapComma
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestListMapComma )
{
  #define TEST_LIST_MAP_COMMA_LB0( count_, item_ ) count_ + item_

  // Map with zero iterations (should eval to nothing)

  STDX_PP_LIST_MAP_C( (), TEST_LIST_MAP_COMMA_LB0 )

  // Map with one iteration

  int vec_0[] = { STDX_PP_LIST_MAP_C( (1), TEST_LIST_MAP_COMMA_LB0 ) };
  UTST_CHECK_EQ( vec_0[0], 1 );

  // Map with three iterations

  int vec_1[] = { STDX_PP_LIST_MAP_C( (1,2,3), TEST_LIST_MAP_COMMA_LB0 ) };
  std::vector<int> vec_ref_1 = gen_vec(3);
  for ( int i = 0; i < 3; i++ )
    UTST_CHECK_EQ( vec_1[i], vec_ref_1.at(i) + (i+1) );

  // Map with 32 iterations

  #define TEST_LIST_MAP_COMMA_0                                       \
    (  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, \
      17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32 )

  int vec_2[] = { STDX_PP_LIST_MAP_C( TEST_LIST_MAP_COMMA_0,
                                      TEST_LIST_MAP_COMMA_LB0 ) };

  std::vector<int> vec_ref_2 = gen_vec(32);
  for ( int i = 0; i < 32; i++ )
    UTST_CHECK_EQ( vec_2[i], vec_ref_2.at(i) + (i+1) );

  // Loop with three iterations and extra arguments

  #define TEST_LIST_MAP_COMMA_LB1( count_, item_, offset_ ) \
    count_ + item_ + offset_

  int vec_3[] = { STDX_PP_LIST_MAP_C( (1,2,3),
                                      TEST_LIST_MAP_COMMA_LB1, 1 ) };

  std::vector<int> vec_ref_3 = gen_vec(3);
  for ( int i = 0; i < 3; i++ )
    UTST_CHECK_EQ( vec_3[i], vec_ref_3.at(i) + (i+1) + 1 );

  // Nested loops

  #define TEST_LIST_MAP_COMMA_LB2_INNER( count_, item_, outer_item_ ) \
    (outer_item_-1)*2 + (item_-1)

  #define TEST_LIST_MAP_COMMA_LB2_OUTER( count_, item_ ) \
    STDX_PP_LIST_MAP_C_X1( (1,2), TEST_LIST_MAP_COMMA_LB2_INNER, item_ )

  int vec_4[] = { STDX_PP_LIST_MAP_C( (1,2,3),
                                      TEST_LIST_MAP_COMMA_LB2_OUTER ) };

  std::vector<int> vec_ref_4 = gen_vec(6);
  for ( int i = 0; i < 6; i++ )
    UTST_CHECK_EQ( vec_4[i], vec_ref_4.at(i) );
}

//------------------------------------------------------------------------
// TestStripParen
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestStripParen )
{
  STDX_PP_STRIP_PAREN( () ) // evals to nothing

  // Strip paren from list with one element

  int vec_0[] = { STDX_PP_STRIP_PAREN( (0) ) };
  std::vector<int> vec_ref_0 = gen_vec(1);
  for ( int i = 0; i < 1; i++ )
    UTST_CHECK_EQ( vec_0[i], vec_ref_0.at(i) );

  // Loop with three iterations

  int vec_1[] = { STDX_PP_STRIP_PAREN( (0,1,2) ) };
  std::vector<int> vec_ref_1 = gen_vec(3);
  for ( int i = 0; i < 3; i++ )
    UTST_CHECK_EQ( vec_1[i], vec_ref_1.at(i) );
}

//------------------------------------------------------------------------
// TestMath
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestMath )
{
  // Test add

  UTST_CHECK_EQ( STDX_PP_ADD(0,0),   0  );
  UTST_CHECK_EQ( STDX_PP_ADD(1,0),   1  );
  UTST_CHECK_EQ( STDX_PP_ADD(0,1),   1  );
  UTST_CHECK_EQ( STDX_PP_ADD(1,1),   2  );
  UTST_CHECK_EQ( STDX_PP_ADD(3,3),   6  );
  UTST_CHECK_EQ( STDX_PP_ADD(16,16), 32 );

  // Test increment

  UTST_CHECK_EQ( STDX_PP_INC(0),  1  );
  UTST_CHECK_EQ( STDX_PP_INC(1),  2  );
  UTST_CHECK_EQ( STDX_PP_INC(3),  4  );
  UTST_CHECK_EQ( STDX_PP_INC(31), 32 );

  // Test subtract

  UTST_CHECK_EQ( STDX_PP_SUB(0,0),   0  );
  UTST_CHECK_EQ( STDX_PP_SUB(1,0),   1  );
  UTST_CHECK_EQ( STDX_PP_SUB(3,1),   2  );
  UTST_CHECK_EQ( STDX_PP_SUB(1,1),   0  );
  UTST_CHECK_EQ( STDX_PP_SUB(6,3),   3  );
  UTST_CHECK_EQ( STDX_PP_SUB(32,16), 16 );

  // Test decrement

  UTST_CHECK_EQ( STDX_PP_DEC(1),  0  );
  UTST_CHECK_EQ( STDX_PP_DEC(2),  1  );
  UTST_CHECK_EQ( STDX_PP_DEC(4),  3  );
  UTST_CHECK_EQ( STDX_PP_DEC(32), 31 );

  // Test nested math

  #define TEST_MATH_1 1
  #define TEST_MATH_3 3
  #define TEST_MATH_5 5
  #define TEST_MATH_9 9

  int res_0 = (TEST_MATH_9 - TEST_MATH_5) + (TEST_MATH_3 - 1);

  #define TEST_MATH_RES_0 \
    STDX_PP_ADD( STDX_PP_SUB( TEST_MATH_9, TEST_MATH_5 ), \
                 STDX_PP_DEC( TEST_MATH_3 ) )

  UTST_CHECK_EQ( TEST_MATH_RES_0, res_0 );

  int res_1 = (TEST_MATH_9 + TEST_MATH_5) - (TEST_MATH_3 + 1);

  #define TEST_MATH_RES_1 \
    STDX_PP_SUB( STDX_PP_ADD( TEST_MATH_9, TEST_MATH_5 ), \
                 STDX_PP_INC( TEST_MATH_3 ) )

  UTST_CHECK_EQ( TEST_MATH_RES_1, res_1 );
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv );
}

