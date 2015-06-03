//========================================================================
// utst-TestSuite.cc
//========================================================================

#include "utst-TestSuite.h"
#include "utst-TestLog.h"
#include "utst-ITestCase.h"
#include <cassert>

namespace utst {

  //----------------------------------------------------------------------
  // Constructors/Destructors
  //----------------------------------------------------------------------

  TestSuite::TestSuite()
  {
    m_name = "UNNAMED";
  }

  TestSuite::TestSuite( const std::string& name )
  {
    m_name = name;
  }

  TestSuite::~TestSuite()
  {
    for ( int i = 0; i < static_cast<int>(m_tests.size()); i++ )
      delete m_tests.at(i);
  }

  //----------------------------------------------------------------------
  // Test suite name
  //----------------------------------------------------------------------

  void TestSuite::set_name( const std::string& name )
  {
    m_name = name;
  }

  std::string TestSuite::get_name() const
  {
    return m_name;
  }

  //----------------------------------------------------------------------
  // add_test
  //----------------------------------------------------------------------

  void TestSuite::add_test( const ITestCase& test )
  {
    m_tests.push_back( test.clone() );
    m_name_map[test.get_name()] = m_tests.back();
  }

  //----------------------------------------------------------------------
  // get_test_names
  //----------------------------------------------------------------------

  std::vector<std::string> TestSuite::get_test_names() const
  {
    std::vector<std::string> vec;
    for ( int i = 0; i < static_cast<int>(m_tests.size()); i++ )
      vec.push_back( m_tests.at(i)->get_name() );
    return vec;
  }

  //----------------------------------------------------------------------
  // has_test
  //----------------------------------------------------------------------

  bool TestSuite::has_test( const std::string& test_name ) const
  {
    return ( m_name_map.find( test_name ) != m_name_map.end() );
  }

  //----------------------------------------------------------------------
  // run_test
  //----------------------------------------------------------------------

  void TestSuite::run_test( const std::string& test_name ) const
  {
    TestLog::instance().log_test_suite_begin(m_name);

    // Lookup test name in the name map and assert its presence
    std::map<std::string,ITestCase*>::const_iterator itr;
    itr = m_name_map.find( test_name );
    assert( itr != m_name_map.end() );

    // Run the test case
    itr->second->run();

    TestLog::instance().log_test_suite_end();
  }

  //----------------------------------------------------------------------
  // run_tests
  //----------------------------------------------------------------------

  void TestSuite::run_tests( const std::vector<std::string>& test_names ) const
  {
    if ( test_names.empty() )
      return;

    TestLog::instance().log_test_suite_begin(m_name);

    int test_names_sz = static_cast<int>(test_names.size());
    for ( int idx = 0; idx < test_names_sz; idx++ ) {

      // Lookup test name in the name map and assert its presence
      std::map<std::string,ITestCase*>::const_iterator itr;
      itr = m_name_map.find( test_names.at(idx) );
      assert( itr != m_name_map.end() );

      // Run the test case
      itr->second->run();

    }

    TestLog::instance().log_test_suite_end();
  }

  //----------------------------------------------------------------------
  // run_all
  //----------------------------------------------------------------------

  void TestSuite::run_all() const
  {
    if ( m_tests.empty() )
      return;

    TestLog::instance().log_test_suite_begin(m_name);

    for ( int i = 0; i < static_cast<int>(m_tests.size()); i++ )
      m_tests.at(i)->run();

    TestLog::instance().log_test_suite_end();
  }

}

