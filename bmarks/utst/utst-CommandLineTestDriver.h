//========================================================================
// utst::CommandLineTestDriver : Use command line to manage unit tests
//========================================================================
// Please read the documentation in utst-uguide.txt for more information
// on how this class fits into the overall unit test framework.
//
// A test driver manages setting up the test log and running the desired
// tests. Currently the only test driver is allows dvelopers to control
// the unit testing process through the command line. To use the driver,
// a developer first defines the test cases and adds them to a test
// suite. Then a pointer to the suite is added to the driver, and the
// driver is passed the command line arguments for processing.
//
// The test driver accepts the following command line usage:
//
//  % utst-exe [options] [suite ...] [case ...]
//
// With the following command line options:
//
//  --log-level <level> : Set level of detail for output
//  --list-tests        : List all test suites and cases
//  --help              : Show usage information
//
// Use the --list-tests flag to see a list of all the possible test
// suites and test cases. A user can select which tests to run by simply
// listing the names of the desired test suites and test cases on the
// command line. The default is to run all tests suites. Possible log
// levels are listed below:
//
//  - minimal  : Output failing checks only
//  - moderate : Output failing checks and other log output
//  - verbose  : Output passing/failing checks and other log output
//

#ifndef UTST_COMMAND_LINE_TEST_DRIVER_H
#define UTST_COMMAND_LINE_TEST_DRIVER_H

#include <vector>

namespace utst {

  // Forward declare classes
  class TestSuite;

  class CommandLineTestDriver {

   public:

    //--------------------------------------------------------------------
    // Constructors/Destructors
    //--------------------------------------------------------------------

    // Default constructor
    CommandLineTestDriver();

    // Default destructor
    ~CommandLineTestDriver();

    //--------------------------------------------------------------------
    // Adding test suites
    //--------------------------------------------------------------------

    // Add a pointer to a test suite for this driver to manage. The
    // caller is responsible for making sure the pointer is valid for
    // the lifetime of the driver.
    void add_suite( TestSuite* test_suite_ptr );

    //--------------------------------------------------------------------
    // Running test cases
    //--------------------------------------------------------------------

    // Run all the test suites based on the given command line arguments
    void run( int argc, char* argv[] ) const;

   private:

    std::vector<TestSuite*> m_suites;

  };

}

#endif /* UTST_COMMAND_LINE_TEST_DRIVER_H */

