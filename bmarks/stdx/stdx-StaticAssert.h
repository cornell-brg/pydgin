//========================================================================
// stdx-StaticAssert : Static (compile-time) assertions
//========================================================================
// With maore advanced metaprogramming, we often want to check some
// assertions at compile time instead of at run-time. The following
// macro simplifies this process. For example, to check if one template
// argument is less than or equal to a second argument we could use
// this:
//
//  template < int t_num1, int t_num2 >
//  class ExampleClass {
//    STDX_STATIC_ASSERT( t_num1 <= t_num2 );
//   
//    // Rest of class declaration
//  };
//
// If we try and compile a program which instantiates this template as 
// ExampleClass<3,2> we will get an error message like this:
//
//  test.cc: In instantiation of 'TestClass<2, 3>':
//  test.cc:28:   instantiated from here
//  test.cc:14: error: invalid application of 'sizeof' to
//                        incomplete type 'stdx::StaticAssert<false>' 
//
// The reference to stdx::StaticAssert<false> quickly tells us that
// there was a static assertion failure on line 14 of the file test.cc.
// This implementation was inspired from the boost StaticAssert library.

#ifndef STDX_STATIC_ASSERT_H
#define STDX_STATIC_ASSERT_H

//------------------------------------------------------------------------
// STDX_STATIC_ASSERT
//------------------------------------------------------------------------

#define STDX_STATIC_ASSERT( expr_ ) \
  STDX_STATIC_ASSERT_( expr_ )

#include "stdx-StaticAssert.inl"
#endif /* STDX_STATIC_ASSERT_H */

