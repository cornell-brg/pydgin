//========================================================================
// Unit Tests for the Unit Test Framework
//========================================================================

#include "utst.h"
#include <vector>

//------------------------------------------------------------------------
// Test check basics
//------------------------------------------------------------------------

UTST_TEST_CASE( TestCheckBasics )
{
  UTST_CHECK( 1 + 1 == 2 );
  UTST_CHECK_EQ  ( 1 + 1, 2 );
  UTST_CHECK_NEQ ( 1 + 2, 2 );
}

//------------------------------------------------------------------------
// Test check floating-point
//------------------------------------------------------------------------

UTST_TEST_CASE( TestCheckFloatingPoint )
{
  UTST_CHECK_EQ  ( 0.5 + 0.5, 1.0  );
  UTST_CHECK_EQ  ( 0.1 + 0.1, 0.2  );
  UTST_CHECK_EQ  ( 0.3 + 0.3, 0.6  );
  UTST_CHECK_NEQ ( 0.5 + 0.5, 1.10 );
  UTST_CHECK_NEQ ( 0.1 + 0.1, 0.25 );
  UTST_CHECK_NEQ ( 0.3 + 0.3, 0.66 );

  UTST_CHECK_EQ  ( 0.5f + 0.5f, 1.0f  );
  UTST_CHECK_EQ  ( 0.1f + 0.1f, 0.2f  );
  UTST_CHECK_EQ  ( 0.3f + 0.3f, 0.6f  );
  UTST_CHECK_NEQ ( 0.5f + 0.5f, 1.10f );
  UTST_CHECK_NEQ ( 0.1f + 0.1f, 0.25f );
  UTST_CHECK_NEQ ( 0.3f + 0.3f, 0.66f );

  UTST_CHECK_EQ  ( 10000.5 + 10000.5, 20001.0  );
  UTST_CHECK_EQ  ( 10000.1 + 10000.1, 20000.2  );
  UTST_CHECK_EQ  ( 10000.3 + 10000.3, 20000.6  );
  UTST_CHECK_NEQ ( 10000.5 + 10000.5, 20002.10 );
  UTST_CHECK_NEQ ( 10000.1 + 10000.1, 20002.25 );
  UTST_CHECK_NEQ ( 10000.3 + 10000.3, 20002.66 );

  UTST_CHECK_EQ  ( 10000.5f + 10000.5f, 20001.0f  );
  UTST_CHECK_EQ  ( 10000.1f + 10000.1f, 20000.2f  );
  UTST_CHECK_EQ  ( 10000.3f + 10000.3f, 20000.6f  );
  UTST_CHECK_NEQ ( 10000.5f + 10000.5f, 20002.10f );
  UTST_CHECK_NEQ ( 10000.1f + 10000.1f, 20002.25f );
  UTST_CHECK_NEQ ( 10000.3f + 10000.3f, 20002.66f );
}

//------------------------------------------------------------------------
// Test check throw
//------------------------------------------------------------------------

UTST_TEST_CASE( TestCheckThrow )
{
  int foo = 0;
  UTST_CHECK_THROW( int, throw foo );
}

//------------------------------------------------------------------------
// Test check containers equal
//------------------------------------------------------------------------

int int_array0[3] = { 1, 2, 3 };
int int_array1[3] = { 1, 2, 3 };

float float_array0[3] = { 1.0, 2.5, 3.3 };
float float_array1[3] = { 1.0, 2.5, 3.3 };

UTST_TEST_CASE( TestCheckArrayEq )
{
  UTST_CHECK_ARRAY_EQ( int_array0,   int_array1,   2 );
  UTST_CHECK_ARRAY_EQ( int_array0,   int_array1,   3 );
  UTST_CHECK_ARRAY_EQ( float_array0, float_array1, 2 );
  UTST_CHECK_ARRAY_EQ( float_array0, float_array1, 3 );
}

//------------------------------------------------------------------------
// Test check containers equal
//------------------------------------------------------------------------

template < typename T >
std::vector<T> mk_vec( T elm0, T elm1, T elm2 )
{
  std::vector<T> vec;
  vec.push_back(elm0);
  vec.push_back(elm1);
  vec.push_back(elm2);
  return vec;
}

UTST_TEST_CASE( TestCheckContEq )
{
  std::vector<int> int_vec0 = mk_vec(1,2,3);
  std::vector<int> int_vec1 = mk_vec(1,2,3);

  UTST_CHECK_CONT_EQ( int_vec0, int_vec1 );
  UTST_CHECK_CONT_EQ( int_vec0, mk_vec(1,2,3) );

  int_vec0.push_back(4);
  int_vec1.push_back(4);

  UTST_CHECK_CONT_EQ( int_vec0, int_vec1 );

  std::vector<float> float_vec0 = mk_vec(1.0f,2.5f,3.3f);
  std::vector<float> float_vec1 = mk_vec(1.0f,2.5f,3.3f);

  UTST_CHECK_CONT_EQ( float_vec0, float_vec1 );
  UTST_CHECK_CONT_EQ( float_vec0, mk_vec(1.0,2.5,3.3) );

  float_vec0.push_back(4.1);
  float_vec1.push_back(4.1);

  UTST_CHECK_CONT_EQ( float_vec0, float_vec1 );
}

//------------------------------------------------------------------------
// Test log macros
//------------------------------------------------------------------------

UTST_TEST_CASE( TestLogMacros )
{
  int foo = 32;
  UTST_LOG_VAR( foo );
  UTST_LOG_MSG( "Done testing log macros" );
}

//------------------------------------------------------------------------
// Test parameterized test case class
//------------------------------------------------------------------------

class TestParameterizedTestCase
  : public utst::ITestCase_BasicImpl<TestParameterizedTestCase>
{

 public:

  TestParameterizedTestCase( int op1, int op2, int result )
    : m_op1(op1), m_op2(op2), m_result(result)
  {
    std::ostringstream ost;
    ost << "TestParameterizedTestCase_" << m_op1 << "_"
        << m_op2 << "_" << m_result;
    set_name( ost.str() );
  }

  void the_test()
  {
    UTST_CHECK( m_op1 + m_op2 == m_result );
    UTST_CHECK_EQ( m_op1 + m_op2, m_result );
  }

 private:
  int m_op1, m_op2, m_result;

};

//------------------------------------------------------------------------
// Test auto registered test case explicitly
//------------------------------------------------------------------------

class TestAutoReg1 : public utst::ITestCase_BasicImpl<TestAutoReg1> {

 public:

  TestAutoReg1()
  {
    set_name( "TestAutoReg1" );
  }

  void the_test()
  {
    UTST_CHECK( 1 + 1 == 2 );
    UTST_CHECK_EQ(  1 + 1, 2 );
    UTST_CHECK_NEQ( 1 + 2, 2 );
  }

};

utst::AutoRegister ar( &utst::g_default_suite(), TestAutoReg1() );

//------------------------------------------------------------------------
// Test auto registered test case with macro
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestAutoReg2 )
{
  UTST_CHECK( 1 + 1 == 2 );
  UTST_CHECK_EQ(  1 + 1, 2 );
  UTST_CHECK_NEQ( 1 + 2, 2 );
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::g_default_suite().add_test( TestCheckBasics() );
  utst::g_default_suite().add_test( TestCheckFloatingPoint() );
  utst::g_default_suite().add_test( TestCheckThrow() );
  utst::g_default_suite().add_test( TestCheckArrayEq() );
  utst::g_default_suite().add_test( TestCheckContEq() );
  utst::g_default_suite().add_test( TestLogMacros() );
  utst::g_default_suite().add_test( TestParameterizedTestCase(1,1,2) );
  utst::g_default_suite().add_test( TestParameterizedTestCase(2,2,4) );

  utst::auto_command_line_driver( argc, argv );
}

