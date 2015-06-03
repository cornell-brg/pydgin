//========================================================================
// utst-CommandLineTestDriver.cc
//========================================================================

#include "utst-CommandLineTestDriver.h"
#include "utst-TestSuite.h"
#include "utst-TestLog.h"
#include <iostream>
#include <string>
#include <cstdlib>

namespace {

  //----------------------------------------------------------------------
  // SelectedTests
  //----------------------------------------------------------------------

  struct SelectedTests {

    SelectedTests( const utst::TestSuite* suite_ptr )
    {
      m_suite_ptr       = suite_ptr;
      m_entire_suite_en = false;
    }

    const utst::TestSuite*   m_suite_ptr;
    std::vector<std::string> m_test_names;
    bool                     m_entire_suite_en;

  };

  //----------------------------------------------------------------------
  // Display usage and exit
  //----------------------------------------------------------------------

  void display_usage_and_exit( const std::string& name )
  {
    std::cout <<
    "\n Usage: " << name << " [options] [suite ...] [case ...]\n"
    "\n"
    "  --log-level <level> : Set level of detail for output\n"
    "  --list-tests        : List all test suites and cases\n"
    "  --help              : Output this message\n"
    "\n"
    " This program runs unit tests for " << name << ". Use the\n"
    " --list-tests flag to see a list of all the possible test suites and\n"
    " test cases. A user can select which tests to run by simply listing\n"
    " the names of the desired test suites and test cases on the command\n"
    " line. The default is to run all tests suites.\n"
    "\n"
    " Possible log levels are listed below:\n"
    "  minimal  : Output failing checks only\n"
    "  moderate : Output failing checks and other log output\n"
    "  verbose  : Output passing/failing checks and other log output\n"
    "\n";
    exit(1);
  }

}

namespace utst {

  //----------------------------------------------------------------------
  // Constructors/Destructors
  //----------------------------------------------------------------------

  CommandLineTestDriver::CommandLineTestDriver()
  { }

  CommandLineTestDriver::~CommandLineTestDriver()
  { }

  //----------------------------------------------------------------------
  // Adding test suites
  //----------------------------------------------------------------------

  void CommandLineTestDriver::add_suite( TestSuite* test_suite_ptr )
  {
    m_suites.push_back( test_suite_ptr );
  }

  //----------------------------------------------------------------------
  // Running test cases
  //----------------------------------------------------------------------

  void CommandLineTestDriver::run( int argc, char* argv[] ) const
  {
    using namespace std;

    // Get and display unit test name from the name of executable

    string exe_name(argv[0]);
    string::size_type start_pos = exe_name.rfind('/');
    string::size_type end_pos   = exe_name.rfind("-utst");
    string base_name = exe_name.substr( start_pos+1, string::npos );
    string utst_name = exe_name.substr( start_pos+1, end_pos-start_pos-1 );

    // Initialize data structure to track which tests are selected

    bool                  any_selections = false;
    vector<SelectedTests> selected_tests;

    for ( int i = 0; i < static_cast<int>(m_suites.size()); i++ )
      selected_tests.push_back( SelectedTests(m_suites.at(i)) );

    // Parse command line arguments

    for ( int arg_idx = 1; arg_idx < argc; arg_idx++ ) {
      string arg_str = string(argv[arg_idx]);

      // --log-level

      if ( (arg_str == "--log-level") && (arg_idx+1 < argc) ) {

        string log_level_str = argv[++arg_idx];
        if ( log_level_str == "minimal" )
          TestLog::instance().set_log_level( TestLog::LogLevel::minimal );
        else if ( log_level_str == "moderate" ) {
          TestLog::instance().set_log_level( TestLog::LogLevel::moderate );
        }
        else if ( log_level_str == "verbose" ) {
          TestLog::instance().set_log_level( TestLog::LogLevel::verbose );
        }
        else {
          std::cerr << "\n Command Line Error: Unrecognized log level \""
                    << log_level_str << "\"" << endl;
          display_usage_and_exit(base_name);
        }
      }

      // List tests option

      else if ( arg_str == "--list-tests" ) {
        for ( int i = 0; i < static_cast<int>(m_suites.size()); i++ ) {
          vector<string> test_names = m_suites.at(i)->get_test_names();
          if ( !test_names.empty() ) {
            cout << "\n Test suite : "
                 << m_suites.at(i)->get_name() << endl;

            int test_names_sz = static_cast<int>(test_names.size());
            for ( int j = 0; j < test_names_sz; j++ ) {
              cout << "  + Test case : " << test_names.at(j) << endl;
            }

          }
        }
        cout << "\n";
        return;
      }

      // Help option

      else if ( arg_str == "--help")
        display_usage_and_exit(base_name);

      // Test suite or test case

      else {

        // Although this is not a very efficient way to do this search,
        // the number of test suites will probably be very small.

        any_selections = true;
        bool   found = false;
        vector<SelectedTests>::iterator itr = selected_tests.begin();
        while ( !found && (itr != selected_tests.end()) ) {
          if ( itr->m_suite_ptr->get_name() == arg_str ) {
            itr->m_entire_suite_en = true;
            found = true;
          }
          else if ( itr->m_suite_ptr->has_test( arg_str ) ) {
            itr->m_test_names.push_back( arg_str );
            found = true;
          }
          itr++;
        }

        // Display an error if the given command line argument is
        // neither a test suite name nor a test case name.

        if ( !found ) {
          std::cerr << "\n Command Line Error: \"" << arg_str << "\" "
                    << "is not a test suite or test case" << endl;
          display_usage_and_exit(base_name);
        }

      }

    }

    // Output a header specifying what unit tests we are running

    cout << "\n Unit Tests : " << utst_name << endl;

    // If no tests were selected then run all tests in all suites

    if ( !any_selections ) {
      for ( int i = 0; i < static_cast<int>(m_suites.size()); i++ )
        m_suites.at(i)->run_all();
    }

    // Otherwise just run the selected tests

    else {
      int selected_tests_sz = static_cast<int>(selected_tests.size());
      for ( int i = 0; i < selected_tests_sz; i++ ) {
        const TestSuite* suite_ptr = selected_tests.at(i).m_suite_ptr;
        if ( selected_tests.at(i).m_entire_suite_en )
          suite_ptr->run_all();
        else
          suite_ptr->run_tests( selected_tests.at(i).m_test_names );
      }
    }

    // Final blank line

    TestLog::LogLevelEnum log_level
      = TestLog::instance().get_log_level();

    if ( log_level == TestLog::LogLevel::minimal )
      cout << endl;
  }

}

