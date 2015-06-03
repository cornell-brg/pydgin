//========================================================================
// utst-Checks.h : Macros for simple checks in unit tests
//========================================================================
// This file includes the UTST_CHECK macros which check for various
// conditions in a unit test. Details on each check are below. Please
// read the documentation in utst-uguide.txt for how these macros fit
// into the overall unit test framework.

#ifndef UTST_CHECKS_H
#define UTST_CHECKS_H

//------------------------------------------------------------------------
// UTST_CHECK
//------------------------------------------------------------------------
// Check whether or not the given boolean expression is true.

#define UTST_CHECK( expression_ ) \
  UTST_CHECK_( expression_ )

//------------------------------------------------------------------------
// UTST_CHECK_EQ
//------------------------------------------------------------------------
// Check whether or not the given expresssions are equal. When possible
// it is better to use UTST_CHECK_EQ( a, b ) as opposed to using
// UTST_CHECK( a == b ). If a UTST_CHECK_EQ test fails, the framework can
// display the value of both sides of the equality check which can aid in
// debugging. This is not possible in a UTST_TEST test. Of course this
// means a and b must have insertion operators defined for them. If they
// don't then you are better off just using a UTST_CHECK test. Floats and
// doubles are checked with an absolute precision of 0.00001 and a
// relativel rprecision of 0.00001. If you need more or less precision
// you will have to do the check explicitly with UTST_CHECK.

#define UTST_CHECK_EQ( expression0_, expression1_ ) \
  UTST_CHECK_EQ_( expression0_, expression1_ )

//------------------------------------------------------------------------
// UTST_CHECK_NEQ
//------------------------------------------------------------------------
// Check whether or not the given expresssions are not equal. When
// possible it is better to use UTST_CHECK_NEQ( a, b ) as opposed to
// using UTST_TEST( a != b ). If a UTST_CHECK_NEQ test fails, the
// framework can display the value of both sides of the equality check
// which can aid in debugging. This is not possible in a UTST_TEST test.
// Of course this means a and b must have insertion operators defined for
// them. If they don't then you are better off just using a UTST_TEST
// test. Floats and doubles are checked with an absolute precision of
// 0.00001 and a relativel rprecision of 0.00001. If you need more or
// less precision you will have to do the check explicitly with
// UTST_CHECK.

#define UTST_CHECK_NEQ( expression0_, expression1_ ) \
  UTST_CHECK_NEQ_( expression0_, expression1_ )

//------------------------------------------------------------------------
// UTST_CHECK_THROW
//------------------------------------------------------------------------
// Check if the given expresssion throws the given exception. The test
// case will try and catch the exception and if it can then execution
// continues in the test case. There is no need for an explicit
// UTST_CHECK_NOT_THROW test since if any exception is thrown in a test
// case and is not caught it causes that test to fail gracefully.

#define UTST_CHECK_THROW( exception_, expression_ ) \
  UTST_CHECK_THROW_( exception_, expression_ )

//------------------------------------------------------------------------
// UTST_CHECK_ARRAY_EQ
//------------------------------------------------------------------------
// Check whether or not the given arrays are equal. To be equal all
// corresponding elements must be equal. Check assumes that arrays are no
// longer than size. Elements must have insertion operators defined.
// Containers of floats and doubles are checked with a precision of
// 0.000001. If you need more precision you will have to do the check
// explicitly with UTST_CHECK.

#define UTST_CHECK_ARRAY_EQ( array0_, array1_, size_ )  \
  UTST_CHECK_ARRAY_EQ_( array0_, array1_, size_ )

//------------------------------------------------------------------------
// UTST_CHECK_CONT_EQ
//------------------------------------------------------------------------
// Check whether or not the given STL containers are equal. To be equal
// they must have the same number of elements and the corresponding
// elements must be equal. Each container should have at least begin(),
// end(), and size() member functions, a value_type typedef, and the
// elements must have insertion operators defined. Containers of floats
// and doubles are checked with a precision of 0.000001. If you need
// more precision you will have to do the check explicitly with
// UTST_CHECK.

#define UTST_CHECK_CONT_EQ( container0_, container1_ ) \
  UTST_CHECK_CONT_EQ_( container0_, container1_ )

//------------------------------------------------------------------------
// UTST_CHECK_FAILED
//------------------------------------------------------------------------
// Write the given message and force this test case to fail. This can be
// useful when writing custom checks. Note that the given message is fed
// directly into a stringstream so a user is free to insert strings as
// well as other datatypes. Here is an example:
//
//  UTST_TEST_CASE( SimpleTestCase )
//  {
//    int sum = 1 + 1;
//    if ( sum != 2 )
//      UTST_CHECK_FAILED( "sum != 2 (equals " << sum << " instead)" );
//  }
//
// Essentially this macro throws an ECheckFailed exception which should
// be caught by the test case harness.

namespace utst {
  struct ECheckFailed : std::exception {
    ~ECheckFailed() throw() { };
  };
}

#define UTST_CHECK_FAILED( message_ ) \
  UTST_CHECK_FAILED_( message_ )

//------------------------------------------------------------------------
// UTST_LOG_MSG
//------------------------------------------------------------------------
// Write the given message to the log's message stream. The given
// message is fed directly into a stringstream so a user is free to
// insert strings as well as other datatypes. This is only displayed if
// the log level is moderate or verbose.

#define UTST_LOG_MSG( message_ ) \
  UTST_LOG_MSG_( message_ )

//------------------------------------------------------------------------
// UTST_LOG_VAR
//------------------------------------------------------------------------
// Write the given variable plus the variable's name to the log's
// message stream. This is only displayed if the log level is moderate
// or verbose.

#define UTST_LOG_VAR( message_ ) \
  UTST_LOG_VAR_( message_ )

#include "utst-Checks.inl"
#endif /* UTST_CHECKS_H */

