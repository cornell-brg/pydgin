//========================================================================
// utst-AutoUtils.h : Utilities for auto registration features
//========================================================================
// This file contains macros, classes, and functions for automatically
// registering test cases with a few global test suites. Using these
// auto registration features avoids some common errors (eg. defining a
// test case but forgetting to add it to a test suite) and simplifies
// the required boiler plate for writing unit tests. Please read the
// documentation in utst-uguide.txt for more information on how this
// class fits into the overall unit test framework.

#ifndef UTST_AUTO_UTILS_H
#define UTST_AUTO_UTILS_H

#include "utst-TestSuite.h"

namespace utst {

  //----------------------------------------------------------------------
  // Global test suites
  //----------------------------------------------------------------------
  // We use free functions which return a reference to a local static
  // variable Instead of true global variables to avoid any issues with
  // static initialization order. Currently there are three global test
  // suites which developers can use with the auto registration
  // features:
  //
  //  - g_default_suite()  : For default functional unit tests
  //  - g_longrun_suite()  : For long running functional unit tests
  //  - g_perf_suite()     : For performance regression tests
  //

  TestSuite& g_default_suite();
  TestSuite& g_longrun_suite();
  TestSuite& g_perf_suite();

  //----------------------------------------------------------------------
  // AutoRegister
  //----------------------------------------------------------------------
  // This is a helper class whose constructor is mainly just used as a
  // way to run some code at static initialization time. The constructor
  // simply adds the given test case to the given suite.

  struct AutoRegister
  {
    AutoRegister( TestSuite* suite, const ITestCase& test_case );
  };

  //----------------------------------------------------------------------
  // Auto command line driver function
  //----------------------------------------------------------------------
  // This helper function instantiates a CommandLineTestDriver, adds the
  // three global test suites, and runs the unit tests. If you are using
  // the auto registration features then this function is all you need
  // to add to your main function.

  void auto_command_line_driver( int argc, char* argv[] );

}

//------------------------------------------------------------------------
// UTST_AUTO_TEST_CASE
//------------------------------------------------------------------------
// This macro is similar to UTST_TEST_CASE in that it creates a new test
// case, but additionally it auto registers the new test case with the
// default global test suite.

#define UTST_AUTO_TEST_CASE( name_ ) \
  UTST_AUTO_TEST_CASE_( name_ )

//------------------------------------------------------------------------
// UTST_AUTO_EXTRA_TEST_CASE
//------------------------------------------------------------------------
// This macro is similar to UTST_TEST_CASE in that it creates a new test
// case, but additionally it auto registers the new test case with the
// global test suite given as the first parameter. The test suite
// parameter should be either longrun or perf. For example, this creates
// a new test case and automatically adds it to the longrun test suite.
//
//  UTST_AUTO_EXTRA_TEST_CASE( longrun, TestAddition )
//  {
//    UTST_CHECK( 1 + 1 == 2 );
//    UTST_CHECK_EQ( 1, 1 );
//  }
//

#define UTST_AUTO_EXTRA_TEST_CASE( suite_, name_ ) \
  UTST_AUTO_EXTRA_TEST_CASE_( suite_, name_ )

#include "utst-AutoUtils.inl"
#endif /* UTST_AUTO_UTILS_H */

