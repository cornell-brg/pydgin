//========================================================================
// stdx-DebugUtils : Preprocessor macros for debugging
//========================================================================
// A couple simple macros that make "printf" style debugging easier.
// These macros are defined to be empty if STDX_DEBUG_OFF is defined.
// There are three macros:
//
//  - STDX_DEBUG_CHK         : Output checkpoint
//  - STDX_DEBUG_VAR( expr ) : Display the expression and its value
//  - STDX_DEBUG_MSG( msg )  : Display the given message
//
// Each macro will display the file name, the line number, and the
// function where the macro was called before possibly displaying the
// message on a single line. Note that the msg passsed to STDX_DEBUG_MSG
// is directly inserted into a stringstream so you can use the insertion
// operator in the message like this:
//
//  STDX_DEBUG_MSG( "unexpected value (" << value << ")" );
//
// The following example shows how we might trace some buggy behavior in
// a function:
//
//  void foo( int bar )
//  {
//    STDX_DEBUG_MSG( "Entering foo() ..." );
//    STDX_DEBUG_VAR( bar );
//
//    if ( bar != 0 ) {
//      STDX_DEBUG_CHK;
//      foo1();
//    }
//    else {
//      STDX_DEBUG_CHK;
//      foo2();
//    }
//
//    STDX_DEBUG_MSG( "Leaving foo() ..." );
//  }
//
// And this might result in the following output:
//
//  DEBUG: ../stdx/stdx-test.cc:168 : foo : Entering foo() ...
//  DEBUG: ../stdx/stdx-test.cc:169 : foo : bar = 1
//  DEBUG: ../stdx/stdx-test.cc:172 : foo : Checkpoint
//  DEBUG: ../stdx/stdx-test.cc:180 : foo : Leaving foo() ...
//

#ifndef STDX_DEBUG_MACROS_H
#define STDX_DEBUG_MACROS_H

//------------------------------------------------------------------------
// STDX_DEBUG_CHK
//------------------------------------------------------------------------
// Display a checkpoint which can be useful for tracing control flow.
// The resulting output will be:
//
//  DEBUG: somefile.cc:56 : func() : Checkpoint
//

#define STDX_DEBUG_CHK \
  STDX_DEBUG_CHK_

//------------------------------------------------------------------------
// STDX_DEBUG_VAR( var )
//------------------------------------------------------------------------
// Display the name of the given variable (or expression) and its value.
// The resulting output will be:
//
//  DEBUG: somefile.cc:56 : func() : varname = somevalue
//

#define STDX_DEBUG_VAR( expr_ ) \
  STDX_DEBUG_VAR_( expr_ )

//------------------------------------------------------------------------
// STDX_DEBUG_MSG( msg )
//------------------------------------------------------------------------
// Display the given message. The message is inserted into an output
// stream, so you can use the << operator if need. The resulting output
// will be:
//
//  DEBUG: somefile.cc:56 : func() : msg
//

#define STDX_DEBUG_MSG( msg_ ) \
  STDX_DEBUG_MSG_( msg_ )

#include "stdx-DebugUtils.inl"
#endif /* STDX_DEBUG_UTILS */

