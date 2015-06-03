//========================================================================
// stdx-ReflectionUtils : Functions for program reflection
//========================================================================
// Reflection refers to the ability of a program at run-time to observe
// and possibly modify its own structure and behavior. Although C++ does
// not have much built-in support for reflection we can use a
// combination of preprocessor macros, RTTI, and non-standard compiler
// extensions to provide some limited reflection capabilities. This
// header includes some utilities to test and print the types of objects
// and functions at run-time.
//
// An is_a function is provided which allows a user to test if an object
// is of a certain type. For example, this will check is an object is of
// type Derived:
//
//  if ( stdx::is_a<Derived>(obj) )
//    // do something specific to the Derived type
//
// Using runtime type information in this way is usually discouraged.
// Users should use templates and/or virtual functions to implement
// polymorphism. The is_a function can still be useful though in some
// cases.
//
// This header also provides a function to convert the type of an object
// into a string. This can be very useful for debugging. For example,
// the following will print out the type of the given container:
//
//  typedef std::vector<int> IntVector;
//  IntVector vec;
//  std::cout << stdx::demangle_type<IntVector>() << std::endl;
//  std::cout << stdx::demangle_type(vec) << std::endl;
//
// Finally, this header provides macros which expand into the name of
// the containing function. Again this can be useful for debugging. For
// example, the following will print "void foo(int)" to the standard
// output.
//
//  void foo( int arg )
//  {
//    stdx::cout << STDX_FUNCTION_NAME << std::cout;
//  }
//
// Eventually, we might want to add a backtrace() function which uses
// the GNU backtrace() and backtrace_symbols() extensions to return a
// string representing the current call stack. This would be particulary
// useful for debugging where an exception was thrown (ie. we could use
// backtrace() in the constructor for an exception).

#ifndef STDX_REFLECTION_UTILS_H
#define STDX_REFLECTION_UTILS_H

#include "stdx-config.h"
#include <string>

namespace stdx {

  //----------------------------------------------------------------------
  // is_a operator
  //----------------------------------------------------------------------
  // The operator returns true if the type of the given object reference
  // is derived from class T. This function ignores const so the
  // constness of C or T does not matter.

  template < typename T, typename C >
  bool is_a( const C& obj );

  //----------------------------------------------------------------------
  // demangle_type
  //----------------------------------------------------------------------
  // These functions will demangle a type if given a template parameter
  // or a reference to an object. Currently these functions require the
  // gcc abi::__cxa_demangle() extension. If this function is not
  // available then we just return the output from  typeid(obj).name()

  template < typename T >
  std::string demangle_type();

  template < typename T >
  std::string demangle_type( const T& obj );

  //----------------------------------------------------------------------
  // Function name demangling
  //----------------------------------------------------------------------
  // Use the macro STDX_FUNCTION_NAME to get a string representing the
  // current function name with the appropriate namespace, class name,
  // return type, and argument types. The STDX_SHORT_FUNCTION_NAME macro
  // removes the return type and the argument types. Currently these
  // macros require the gcc __PRETTY_FUNCTION__ extension. If this
  // extension is not available then we just use the more standard
  // __func__ magic variable.

  #ifdef STDX_HAVE_GNU_PRETTY_FUNCTION
    #define STDX_FUNCTION_NAME __PRETTY_FUNCTION__
    #define STDX_SHORT_FUNCTION_NAME \
      stdx::details::extract_funct_name( __PRETTY_FUNCTION__ )
  #else
    #define STDX_FUNCTION_NAME __func__
    #define STDX_SHORT_FUNCTION_NAME __func__
  #endif

}

#include "stdx-ReflectionUtils.inl"
#endif /* STDX_REFLECTION_UTILS_H */

