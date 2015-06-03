//========================================================================
// utst::TestLog : Unit test output log
//========================================================================
// Please read the documenation in utst-uguide.txt for more details on
// the overall unit test framework.
//
// Unit tests write their results and other information to the test log.
// Normally, a user does not access the test log directly, but instead
// uses a test driver (such as the CommandLineTestDriver) to setup and
// configure the test log and the UTST_CHECK macros found in
// utst-Checks.h to write the results to the log.
//
// There are still some cases where a user might want to directly access
// the test log. For example, when writing a new test driver or when
// needing to directly insert debugging output to the log output stream.
// There is only one global test log which is accessed through the
// static singleton TestLog::instance() method.
//
// The verbosity of the log output is controlled by setting the log
// level to one of three values:
//
//  - minimal  : Output only failing checks
//  - moderate : Output failing checks and other log output
//  - verbose  : Output passing/failing checks and other log output
//
// The default log level is minimal. These log levels are static
// constants in the TestLog::LogLevel namespace. So to set the log level
// to be very verbose we can use:
//
//  utst::TestLog& log = utst::TestLog::instance();
//  log.set_log_level( utst::TestLog::LogLevel::verbose );
//
// A user might also want to directly set/get the log output stream.
// They can do so through the set_log_ostream() and the
// get_log_ostream() methods. The get_log_ostream() method is a little
// special since it takes as a parameter a log level. The given log
// level allows a user to specify when the objects which will be
// inserted into the ostream should actually be displayed. If we have
// something which should really only be displayed when the 'TestLog'
// log level is verbose we can use the following code.
//
//  utst::TestLog& log = utst::TestLog::instance();
//  std::ostream& os = log.get_log_ostream( utst::TestLog::LogLevel::verbose );
//  os << "This is only displayed when the TestLog log level is verbose";
//

#ifndef UTST_TEST_LOG_H
#define UTST_TEST_LOG_H

#include <string>
#include <iostream>

namespace utst {

  class TestLog {

   public:

    //--------------------------------------------------------------------
    // Singleton accessor
    //--------------------------------------------------------------------

    // This is the global test log. There is only one test log for
    // all tests and test suites.
    static TestLog& instance();

    //--------------------------------------------------------------------
    // Log level
    //--------------------------------------------------------------------

    // Enum for various log levels
    typedef int LogLevelEnum;
    struct LogLevel {
      static const LogLevelEnum minimal;
      static const LogLevelEnum moderate;
      static const LogLevelEnum verbose;
    };

    // Set the current log level for the test log
    void set_log_level( const LogLevelEnum& log_level );

    // Get the current log level for the test log
    LogLevelEnum get_log_level() const;

    //--------------------------------------------------------------------
    // Log stream
    //--------------------------------------------------------------------

    // Set current log output stream. The test log saves a pointer to
    // this stream so the caller is responsible for keeping the
    // output stream around for the lifetime of the test log.
    void set_log_ostream( std::ostream* log_ostream_ptr );

    // Get current log output stream. The given log level specifies
    // the minimum level at which the content inserted into the
    // returned stream will be displayed.
    std::ostream& get_log_ostream( const LogLevelEnum& log_level
                                                 = LogLevel::moderate );

    //--------------------------------------------------------------------
    // Log test suite begin/end
    //--------------------------------------------------------------------

    // Output log info to denote begining of test suite
    void log_test_suite_begin( const std::string& name );

    // Output log info to denote end of test suite
    void log_test_suite_end();

    //--------------------------------------------------------------------
    // Log test case begin/end
    //--------------------------------------------------------------------

    // Output log info to denote begining of test case
    void log_test_case_begin( const std::string& name );

    // Output log info to denote end of test case
    void log_test_case_end();

    //--------------------------------------------------------------------
    // Log notes and tests
    //--------------------------------------------------------------------

    // Log a note located on the given file/line. Only display the
    // note if the log level is moderate or verbose.
    void log_note( const std::string& file_name, int line_num,
                   const std::string& note );

    // Log a test located on the given file/line with a string
    // describing the test, the result indicating whether or not the
    // test passed or failed, and a message providing additional
    // information about the test.
    void log_test( const std::string& file_name, int line_num,
                   const std::string& description, bool result,
                   const std::string& msg = "" );

   private:

    TestLog();
    ~TestLog();

    TestLog::LogLevelEnum m_log_level;
    std::ostream*         m_log_ostream_ptr;
    std::ostream*         m_null_ostream_ptr;

  };

}

#endif /* UTST_TEST_LOG_H */

