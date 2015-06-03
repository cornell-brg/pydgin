//========================================================================
// utst::TestSuite : Collection of test cases
//========================================================================
// Please read the documentation in utst-uguide.txt for more information
// on how this class fits into the overall unit test framework.

#ifndef UTST_TEST_SUITE_H
#define UTST_TEST_SUITE_H

#include <string>
#include <vector>
#include <map>

namespace utst {

  // Forward declare classes
  class ITestCase;

  class TestSuite {

   public:

    //--------------------------------------------------------------------
    // Constructors/Destructors
    //--------------------------------------------------------------------

    // Default constructor
    TestSuite();

    // Default constructor
    TestSuite( const std::string& name );

    // Default destructor
    ~TestSuite();

    //--------------------------------------------------------------------
    // Test suite name
    //--------------------------------------------------------------------

    // Set the name of this test suite
    void set_name( const std::string& name );

    // Return the name of this test suite
    std::string get_name() const;

    //--------------------------------------------------------------------
    // Managing test cases
    //--------------------------------------------------------------------

    // Adds a new test case to the suite
    void add_test( const ITestCase& test_case );

    // Get the names of all the test cases in this suite
    std::vector<std::string> get_test_names() const;

    // Does the suite have a test with the given name
    bool has_test( const std::string& test_name ) const;

    // Run the test with the given name
    void run_test( const std::string& test_name ) const;

    // Run the tests with the given names
    void run_tests( const std::vector<std::string>& test_names ) const;

    // Run all the tests in this suite
    void run_all() const;

   private:

    std::string                      m_name;
    std::map<std::string,ITestCase*> m_name_map;
    std::vector<ITestCase*>          m_tests;

  };

}

#endif /* UTST_TEST_SUITE_H */

