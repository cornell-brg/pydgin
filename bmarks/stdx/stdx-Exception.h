//========================================================================
// stdx-Exception : Exception base class and helper macros
//========================================================================
// This file includes the stdx::Exception base class which has extra
// support for creating more informative error messages. If users derive
// their specific exceptions from this base class and then use the
// provided preprocessor macros, their exception error messages will
// include information about the file name, line number, class name, and
// function name where the exception was thrown.
//
// This file also provides two subclasses of stdx::Exception and
// additional preprocessor macros which are useful for checking
// assertions. Unlike the builtin in assert() function which terminates
// on failure, stdx assertions throw an exception which allow us to
// handle exceptions and assertions the same way.
//
// The available helper macros are listed below:
//
//  - STDX_THROW( excep, msg )             : Throw excep 
//  - STDX_M_THROW( excep, msg )           : ... in member function
//  - STDX_ASSERT( excep, msg )            : Assertion
//  - STDX_M_ASSERT( excep, msg )          : ... in member function
//  - STDX_PERFCRIT_ASSERT( excep, msg )   : Perf critical assertion
//  - STDX_PERFCRIT_M_ASSERT( excep, msg ) : ... in member function
//
// The M variants can be used in member functions and then they will
// include information on the type of the class which threw the
// exception.
//
// We usually always want to check our assertions, but sometimes an
// assertion is in a performance critical piece of code. Of course to
// avoid premature optimization we start by just using a standard
// STDX_ASSERT even in these cases. But if after profiling we find that
// the assertion check is too much overhead, we can replace STDX_ASSERT
// with STDX_PREFCRIT_ASSERT. Then we can disable these assertions by
// defining the STDX_PERFCRIT_ASSERT_OFF preprocessor macro.
//
// The exception messages are directly inserted into a stringstream so
// you can use the insertion operator in your message like this:
//
//  if ( errror )
//    STDX_THROW( EInvalidNumber, "Not a valid number : " << num );
//
// Notice that the policy is for exception classes to begin with an
// uppercase E. A quick and dirty way to throw an exception without
// creating a new exception type is to just throw the stdx:Exception
// class like this:
//
//  if ( error )
//    STDX_THROW( stdx::Exception, "Error message" );
//
// Eventually, we might want to add backtrace support in the exception
// constructor so that we can get information on how we reached the
// point where the exception was thrown. We could potentially leverage
// the GNU backtrace() and backtrace_symbols() extensions for this.
//
// We also provide a helper function named stdx::set_terminate() that is
// similar to the standard std::set_terminate() except with a different
// default exception handler. Our new default exception handler will
// actually call the what() member function for std::exception and
// stdx::IException classes. So all you need to do is use the following
// at the beginning of your main function and you will get verbose
// output when an exception is thrown and not caught.
//
//  stdx::set_terminate();
//
// Note that we do not subclass the std::exception base class because
// then every single exception would need to define an empty destructor
// just so that we can use an empty throw specification. This is pretty
// tedious and its not that important anways since destructors
// fundamentally don't throw exceptions. The tradeoff is that now we
// need to catch both std::exception and stdx::Exception - but writing
// catch blocks (that should catch all exceptions) seems to be much less
// common than defining exceptions.
//
// TODO:
//  - Develop cleaner way to handle stdx exceptions in utst framework
//  - Add way to register exception handlers for use by set_terminate
//

#ifndef STDX_EXCEPTION_H
#define STDX_EXCEPTION_H

#include "stdx-ReflectionUtils.h"
#include <sstream>
#include <string>

namespace stdx {

  //----------------------------------------------------------------------
  // IException
  //----------------------------------------------------------------------
  // This is the base class for all of our exceptions. Notice that we do
  // not inheret from std::exception because that would require us to
  // include a default constructor for every exception subclass (we need
  // to explicitly specify the throw() specifier). The preprocessor
  // conditions are a hack to allow the unit test framework to catch
  // IExceptions and display the appropriate debug message without
  // making utst depend on stdx.

  #ifndef STDX_IEXCEPTION_DEFINED
  #define STDX_IEXCEPTION_DEFINED

  class IException {
   public:
    virtual ~IException() { }
    virtual const char* what() const = 0;
  };

  #endif /* STDX_IEXCEPTION_DEFINED */

  //----------------------------------------------------------------------
  // Exception
  //----------------------------------------------------------------------
  // This exception base class includes a string to hold an error
  // message. We do not pass this message in as a constructor argument
  // because it would mean that every subclass of exception would need
  // to definie a similar constructor. Instead we set the message
  // through a member function. The macros provided below take care of
  // using this member function to set the error message accordingly.

  class Exception : public IException {

   public:

    // Set the error message

    void set_msg( const std::string& msg )
    {
      m_msg = msg;
    }

    // Default deconstructor

    virtual ~Exception() { }

    // Return the error message

    virtual const char* what() const
    {
      return m_msg.c_str();
    }

   private:
    std::string m_msg;

  };

  //----------------------------------------------------------------------
  // EAssert
  //----------------------------------------------------------------------
  // A design assertion. This class is meant to be used with the various
  // STDX_ASSERT macros so that we can include an error message and
  // information about where the exception was thrown.

  struct EAssert : public Exception { };

  //----------------------------------------------------------------------
  // terminate
  //----------------------------------------------------------------------
  // Our new exception handler that calls the what() member function for
  // std::exception and stdx::IException so that your program prints out
  // nice verbose information for uncaught exceptions. We make this
  // publically visible incase someone wants to call explicitly, say
  // after creating their own custom terminate() function. Note that due
  // to implementation details, it is invalid to call terminate except
  // from within a catch block or within an exception handler that will
  // be set with set_terminate().

  void terminate();

  //----------------------------------------------------------------------
  // set_terminate
  // ----------------------------------------------------------------------
  // A helper function similar to the standard std::set_terminate()
  // except with a different default exception handler, namely
  // stdx::terminate().

  void set_terminate( std::terminate_handler handler = stdx::terminate );

}

//------------------------------------------------------------------------
// STDX_THROW
//------------------------------------------------------------------------
// Throw the given exception (excep_) with the given message (msg_). The
// message is inserted into a stringstream so you can use << in the
// message if desired.

#define STDX_THROW( excep_, msg_ ) \
  STDX_THROW_( excep_, msg_ )

//------------------------------------------------------------------------
// STDX_M_THROW
//------------------------------------------------------------------------
// Throw the given exception (excep_) with the given message (msg_). The
// type of (*this) is also added to the error message. This gives more
// information than just STDX_THROW since it will list the concrete
// class not just the base class. The message is inserted into a
// stringstream so you can use << in the message if desired.

#define STDX_M_THROW( excep_, msg_ ) \
  STDX_M_THROW_( excep_, msg_ )

//------------------------------------------------------------------------
// STDX_ASSERT
//------------------------------------------------------------------------
// Check the given assertion and if it is false throw a stdx::EAssert
// exception with the given message (msg_). The message is inserted into
// a stringstream so you can use << in the message if desired.

#define STDX_ASSERT( assertion_ ) \
  STDX_ASSERT_( assertion_ )

//------------------------------------------------------------------------
// STDX_M_ASSERT
//------------------------------------------------------------------------
// Check the given assertion and if it is false throw a stdx::EAssert
// exception with the given message (msg_). The type of (*this) is also
// added to the error message. This gives more information than just
// STDX_ASSERTa since it will list the concrete class not just the base
// class. The message is inserted into a stringstream so you can use <<
// in the message if desired.

#define STDX_M_ASSERT( assertion_ ) \
  STDX_M_ASSERT_( assertion_ )

//------------------------------------------------------------------------
// STDX_PERFCRIT_ASSERT
//------------------------------------------------------------------------
// Check the given assertion and if it is false throw a stdx::EAssert
// exception with the given message (msg_). The message is inserted into
// a stringstream so you can use << in the message if desired. Defining
// STDX_PERFCRIT_ASSERT_OFF will make this macro turn into nothing.

#define STDX_PERFCRIT_ASSERT( assertion_ ) \
  STDX_PERFCRIT_ASSERT_( assertion_ )

//------------------------------------------------------------------------
// STDX_PERFCRIT_M_ASSERT
//------------------------------------------------------------------------
// Check the given assertion and if it is false throw a stdx::EAssert
// exception with the given message (msg_). The type of (*this) is also
// added to the error message. This gives more information than just
// STDX_PERCRIT_ASSERT since it will list the concrete class not just
// the base class. The message is inserted into a stringstream so you
// can use << in the message if desired. Defining
// STDX_PERFCRIT_ASSERT_OFF will make this macro turn into nothing.

#define STDX_PERFCRIT_M_ASSERT( assertion_ ) \
  STDX_PERFCRIT_M_ASSERT_( assertion_ ) 

#include "stdx-Exception.inl"
#endif /* STDX_EXCEPTION_H */

