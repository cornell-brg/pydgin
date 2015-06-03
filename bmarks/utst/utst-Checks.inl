//========================================================================
// utst-Checks.inl
//========================================================================
// Refactoring the check macros into functions as much as possible
// should improve compile times as opposed to having each macro expand
// to lots of code. A single test case might use tens of check macros so
// we need to be careful how much code this expands to.

#include "utst-TestLog.h"
#include <string>
#include <sstream>
#include <iostream>
#include <cmath>
#include <functional>

namespace utst {
namespace details {

  //----------------------------------------------------------------------
  // ComparisonFunctor
  //----------------------------------------------------------------------

  template < typename T >
  struct ComparisonFunctor
  {
    bool operator()( const T& value0, const T& value1 ) {
      return ( value0 == value1 );
    }
  };

  //----------------------------------------------------------------------
  // ComparisonFunctor floating point specializations
  //----------------------------------------------------------------------
  // Originally I used the implementation from Knuth via the C++ FAQ
  //
  //  http://www.parashift.com/c++-faq-lite/newbie.html#faq-29.17
  //
  // but this seemed to return false for some numbers which were really
  // close enough in my mind. Part of this is because the Knuth approach
  // doesn't do the first check to see if the parameters are within a
  // reasonable absolute error. Overall, I am happier with the approach
  // described in the begining of the following white paper:
  //
  //  http://www.cygnus-software.com/papers/comparingfloats/comparingfloats.htm
  //

  template < typename T >
  bool fp_close( T num0, T num1 )
  {
    T max_abs_error = static_cast<T>(0.00001);
    T max_rel_error = static_cast<T>(0.00001);

    T abs_error = std::abs( num0 - num1 );
    if ( abs_error <= max_abs_error )
      return true;

    T rel_error;
    if ( std::abs(num1) > std::abs(num0) )
      rel_error = std::abs((num0 - num1) / num1);
    else
      rel_error = std::abs((num0 - num1) / num0);

    return ( rel_error <= max_rel_error );
  }

  template <>
  struct ComparisonFunctor<float>
  {
    bool operator()( const float& value0, const float& value1 ) {
      return fp_close<float>( value0, value1 );
    }
  };

  template <>
  struct ComparisonFunctor<double>
  {
    bool operator()( const double& value0, const double& value1 ) {
      return fp_close<double>( value0, value1 );
    }
  };

  //----------------------------------------------------------------------
  // check_eq
  //----------------------------------------------------------------------
  // We use the above specializations of the ComparisonFunctor to use
  // different equality tests based on the expression types.

  template < typename Expr1, typename Expr2 >
  void check_eq( const std::string& file_name, int line_num,
                 const Expr1& expression0, const Expr2& expression1,
                 const char* expression0_str,
                 const char* expression1_str )
  {
    utst::TestLog& log = utst::TestLog::instance();

    ComparisonFunctor<Expr1> comp_func;
    bool result = comp_func( expression0, expression1 );

    std::ostringstream descr;
    descr << expression0_str << " == " << expression1_str;

    std::ostringstream msg;
    msg << expression0 << (result ? " == " : " != ") << expression1;

    log.log_test( file_name, line_num, descr.str(), result, msg.str() );
  }

  //----------------------------------------------------------------------
  // check_neq
  //----------------------------------------------------------------------
  // We use the above specializations of the ComparisonFunctor to use
  // different equality tests based on the expression types.

  template < typename Expr1, typename Expr2 >
  void check_neq( const std::string& file_name, int line_num,
                  const Expr1& expression0, const Expr2& expression1,
                  const char* expression0_str,
                  const char* expression1_str )
  {
    utst::TestLog& log = utst::TestLog::instance();

    ComparisonFunctor<Expr1> comp_func;
    bool result = !comp_func( expression0, expression1 );

    std::ostringstream descr;
    descr << expression0_str << " != " << expression1_str;

    std::ostringstream msg;
    msg << expression0 << (result ? " != " : " == ") << expression1;

    log.log_test( file_name, line_num, descr.str(), result, msg.str() );
  }

  //----------------------------------------------------------------------
  // check_array_eq
  //----------------------------------------------------------------------

  template < typename Elm0, typename Elm1 >
  void check_array_eq( const std::string& file_name, int line_num,
                       const Elm0* array0, const Elm1* array1, int size,
                       const char* array0_str,
                       const char* array1_str )
  {
    utst::TestLog& log = utst::TestLog::instance();

    // Check each element in each array

    bool equal = true;
    for ( int i = 0; i < size; i++ ) {
      ComparisonFunctor<Elm0> comp_func;
      if ( !( comp_func( array0[i], array1[i] ) ) ) {
        equal = false;

        std::ostringstream descr;
        descr << array0_str << "[" << i << "]" << " == "
              << array1_str << "[" << i << "]";

        std::ostringstream msg;
        msg << array0[i] << " != " << array1[i];

        log.log_test( file_name, line_num, descr.str(), false, msg.str() );
      }
    }

    // Are they equal?

    if ( equal ) {
      std::ostringstream descr;
      descr << array0_str << " == " << array1_str;
      log.log_test( file_name, line_num, descr.str(), true );
    }

  }

  //----------------------------------------------------------------------
  // check_cont_eq
  //----------------------------------------------------------------------

  template < typename Cont0, typename Cont1 >
  void check_cont_eq( const std::string& file_name, int line_num,
                      const Cont0& container0, const Cont1& container1,
                      const char* container0_str,
                      const char* container1_str )
  {
    utst::TestLog& log = utst::TestLog::instance();

    // Check containers are of the same size

    if ( container0.size() != container1.size() ) {

      std::ostringstream descr;
      descr << container0_str << " and "
            << container1_str << " same size?";

      std::ostringstream msg;
      msg << container0.size() << " != " << container1.size();

      log.log_test( file_name, line_num, descr.str(), false, msg.str() );
      return;
    }

    // Check each element in each container

    typename Cont0::const_iterator itr1 = container0.begin();
    typename Cont1::const_iterator itr2 = container1.begin();

    bool equal = true;
    int  index = 0;
    while ((itr1 != container0.end()) && (itr2 != container1.end())) {

      ComparisonFunctor<typename Cont0::value_type> comp_func;
      if ( !( comp_func( *itr1, *itr2 ) ) ) {
        equal = false;

        std::ostringstream descr;
        descr << container0_str << "[" << index << "]" << " == "
              << container1_str << "[" << index << "]";

        std::ostringstream msg;
        msg << *itr1 << " != " << *itr2;

        log.log_test( file_name, line_num, descr.str(), false, msg.str() );
      }

      itr1++; itr2++; index++;
    }

    // Are they equal?

    if ( equal ) {
      std::ostringstream descr;
      descr << container0_str << " == " << container1_str;
      log.log_test( file_name, line_num, descr.str(), true );
    }

  }

  //----------------------------------------------------------------------
  // ECheckFailed
  //----------------------------------------------------------------------

  struct EFatalFailure : std::exception {
    ~EFatalFailure() throw() { };
  };

}}

//------------------------------------------------------------------------
// UTST_CHECK
//------------------------------------------------------------------------

#define UTST_CHECK_( expression_ )                                      \
  utst::TestLog::instance().log_test( __FILE__, __LINE__,               \
    #expression_, expression_ );

//------------------------------------------------------------------------
// UTST_CHECK_EQ
//------------------------------------------------------------------------

#define UTST_CHECK_EQ_( expression0_, expression1_ )                    \
  utst::details::check_eq( __FILE__, __LINE__,                          \
    expression0_, expression1_, #expression0_, #expression1_ );

//------------------------------------------------------------------------
// UTST_CHECK_NEQ
//------------------------------------------------------------------------

#define UTST_CHECK_NEQ_( expression0_, expression1_ )                   \
  utst::details::check_neq( __FILE__, __LINE__,                         \
    expression0_, expression1_, #expression0_, #expression1_ );

//------------------------------------------------------------------------
// UTST_CHECK_THROW
//------------------------------------------------------------------------

#define UTST_CHECK_THROW_( exception_, expression_ )                    \
{                                                                       \
  bool caught_ = false;                                                 \
  try { expression_; }                                                  \
  catch ( exception_& e_ ) { caught_ = true; }                          \
  std::ostringstream ost_;                                              \
  ost_ << "( " << #expression_ << " ) throw " << #exception_ << "?";    \
  utst::TestLog::instance().log_test( __FILE__, __LINE__,               \
                                      ost_.str(), caught_ );            \
}

//------------------------------------------------------------------------
// UTST_CHECK_ARRAY_EQ
//------------------------------------------------------------------------

#define UTST_CHECK_ARRAY_EQ_( array0_, array1_, size_ )                 \
  utst::details::check_array_eq( __FILE__, __LINE__,                    \
    array0_, array1_, size_, #array0_, #array1_ );

//------------------------------------------------------------------------
// UTST_CHECK_CONT_EQ
//------------------------------------------------------------------------

#define UTST_CHECK_CONT_EQ_( container0_, container1_ )                 \
  utst::details::check_cont_eq( __FILE__, __LINE__,                     \
    container0_, container1_, #container0_, #container1_ );

//------------------------------------------------------------------------
// UTST_CHECK_FAILED
//------------------------------------------------------------------------

#define UTST_CHECK_FAILED_( message_ )                                  \
{                                                                       \
  std::ostringstream ost;                                               \
  ost << message_;                                                      \
  utst::TestLog::instance().log_test( __FILE__, __LINE__,               \
                                      ost.str(), false );               \
  throw utst::details::EFatalFailure();                                 \
}

//------------------------------------------------------------------------
// UTST_LOG_MSG
//------------------------------------------------------------------------

#define UTST_LOG_MSG_( message_ )                                       \
{                                                                       \
  std::ostringstream ost;                                               \
  ost << message_;                                                      \
  utst::TestLog::instance().log_note( __FILE__, __LINE__, ost.str() );  \
}

//------------------------------------------------------------------------
// UTST_LOG_VAR
//------------------------------------------------------------------------

#define UTST_LOG_VAR_( variable_ )                                      \
{                                                                       \
  std::ostringstream ost;                                               \
  ost << #variable_ << " = " << variable_;                              \
  utst::TestLog::instance().log_note( __FILE__, __LINE__, ost.str() );  \
}

