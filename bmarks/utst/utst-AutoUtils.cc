//========================================================================
// utst-AutoUtils.cc
//========================================================================

#include "utst-AutoUtils.h"
#include "utst-ITestCase.h"
#include "utst-CommandLineTestDriver.h"

namespace utst {

  //----------------------------------------------------------------------
  // Global test suites
  //----------------------------------------------------------------------

  TestSuite& g_default_suite()
  {
    static TestSuite g_default_suite("default");
    return g_default_suite;
  }

  TestSuite& g_longrun_suite()
  {
    static TestSuite g_longrun_suite("longrun");
    return g_longrun_suite;
  }

  TestSuite& g_perf_suite()
  {
    static TestSuite g_perf_suite("perf");
    return g_perf_suite;
  }

  //----------------------------------------------------------------------
  // AutoRegister
  //----------------------------------------------------------------------
  // This is a helper class whose constructor is mainly just used as a
  // way to run some code at static initialization time.

  AutoRegister::AutoRegister( TestSuite* suite,
                              const ITestCase& test_case )
  {
    suite->add_test( test_case );
  }

  //----------------------------------------------------------------------
  // auto_command_line_driver
  //----------------------------------------------------------------------

  void auto_command_line_driver( int argc, char* argv[] )
  {
    utst::CommandLineTestDriver driver;
    driver.add_suite( &utst::g_default_suite() );
    driver.add_suite( &utst::g_longrun_suite() );
    driver.add_suite( &utst::g_perf_suite()    );
    driver.run( argc, argv );
  }

}

