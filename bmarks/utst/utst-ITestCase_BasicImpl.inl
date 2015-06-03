//========================================================================
// utst-ITestCase_BasicImpl.inl
//========================================================================

#include "utst-TestLog.h"
#include "utst-Checks.h"
#include <iostream>
#include <cassert>

//------------------------------------------------------------------------
// Hack to help with stdx integration
//------------------------------------------------------------------------
// Ideally we want our utst library to display useful debugging
// information about unexpected exceptions which are thrown from within
// a test case. Normally what we would do is simply catch std::exception
// and then use the virtual what() method to display a message about the
// exception. Unfortunately, the std::exception class uses a throw()
// specifier on its destructor which means that _any_ class which
// inherits from std::exception must explicitly define a destructor
// (almost always empty) just so that it can narrow the throw
// specification. So we have to do something like this:
//
//  struct MyException : public std::exception {
//    virtual ~MyException() throw() { }
//  };
//
// This might not seem like such a big deal, but it leads to pretty
// annoying syntax if we have a list of exceptions for a given class.
// It's also pretty unnecessary - destructors should never throw
// exceptions anyways and I doubt the compiler is enabled to do any
// radical optimization based on having throw() defined on the
// std::exception destructor.
//
// So as a workaround, we anticipate all of our user defined exceptions
// inheriting from stdx::IException which will not include the throw()
// specifier. We will also have a helper implementation class which
// inherits from stdx::IException called stdx::Exception that stores a
// string with the debug message. Thus we can just use this syntax:
//
//  struct MyException : public stdx::Exception { }
//
// We cannot, however, make utst depend on stdx - but we need to have
// stdx::IException defined so that we can catch it in this test case.
// So instead what we do (and here is the hack), we define IException
// here in this file - and we use preprocessor conditions so that we
// don't define it twice. Then we will put the same definition (with the
// same preprocessor conditions) eventually in our stdx exception code.
// Maybe eventually I will come up with a better way to do this.
//
// Maybe we can use some kind of handler registration approach. So
// users could register a handler for stdx exceptions. We might be
// able to use this kind of idiom:
//
//  void exception_handler()
//  {
//    try { throw; }
//    catch ( stdx::IException& e ) {
//      // do something?
//    }
//  }
//
// The try { throw; } pattern means that you can really only call this
// function from within a catch (...) block and it is essentially a way
// to see if the caught exception is of a certain type. Maybe the
// exception handler should take a stream and its job is essentially
// to write some output to the stream. Seems like we would want to
// register these handlers with the test driver not each test case. So
// maybe unhandled exceptions should stop the whole unit test as opposed
// to just stopping that specific test case? Not sure I like that. Test
// cases could maybe have a pointer to the test suite which in turn
// knows the exception handlers to use.
//
// TODO:
//  - Develop cleaner way to handle stdx exceptions in utst framework
//

#ifndef STDX_IEXCEPTION_DEFINED
#define STDX_IEXCEPTION_DEFINED
namespace stdx {
  class IException {
   public:
    virtual ~IException() { }
    virtual const char* what() const = 0;
  };
}
#endif

namespace utst {

  //----------------------------------------------------------------------
  // Constructors/Destructors
  //----------------------------------------------------------------------

  template < typename T >
  ITestCase_BasicImpl<T>::ITestCase_BasicImpl()
  {
    m_name = "UNNAMED";
  }

  template < typename T >
  ITestCase_BasicImpl<T>::~ITestCase_BasicImpl()
  { }

  //----------------------------------------------------------------------
  // Test case name
  //----------------------------------------------------------------------

  template < typename T >
  void ITestCase_BasicImpl<T>::set_name( const std::string& name )
  {
    m_name = name;
  }

  template < typename T >
  std::string ITestCase_BasicImpl<T>::get_name() const
  {
    return m_name;
  }

  //----------------------------------------------------------------------
  // Other public member functions
  //----------------------------------------------------------------------

  template < typename T >
  ITestCase* ITestCase_BasicImpl<T>::clone() const
  {
    return new T(dynamic_cast<const T&>(*this));
  }

  template < typename T >
  void ITestCase_BasicImpl<T>::run()
  {
    utst::TestLog& log = utst::TestLog::instance();
    log.log_test_case_begin(m_name);

    try {

      the_test();

    }
    catch ( utst::details::EFatalFailure& e ) { }
    catch ( std::exception& e ) {
      log.log_test( "", 0, "Caught unexpected std::exception", false );
      log.get_log_ostream( TestLog::LogLevel::minimal ) << e.what();
      log.get_log_ostream( TestLog::LogLevel::minimal ) << std::endl;
    }
    catch ( stdx::IException& e ) {
      log.log_test( "", 0, "Caught unexpected stdx::IException", false );
      log.get_log_ostream( TestLog::LogLevel::minimal ) << e.what();
      log.get_log_ostream( TestLog::LogLevel::minimal ) << std::endl;
    }
    catch ( ... ) {
      log.log_test( "", 0, "Caught unexpected exception", false );
    }

    log.log_test_case_end();
  }

}

//------------------------------------------------------------------------
// UTST_TEST_CASE
//------------------------------------------------------------------------

#define UTST_TEST_CASE_( name_ )                                        \
  struct name_ : public utst::ITestCase_BasicImpl<name_>                \
  {                                                                     \
    name_() { set_name( #name_ ); }                                     \
    void the_test();                                                    \
  };                                                                    \
  void name_::the_test()

