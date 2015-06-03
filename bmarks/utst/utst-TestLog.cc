//========================================================================
// utst-TestLog.cc
//========================================================================

#include "utst-TestLog.h"

//------------------------------------------------------------------------
// Null Output Stream
//------------------------------------------------------------------------
// This helper output stream basically just throws away anything which
// is inserted into it. It allows us to return a valid stream as the
// log stream even when the log level is such that nothing should be
// actaully logged. Note that we dynamically allocate this object so
// that we can put the declaration and definition in the .cc and avoid
// polluting the utst namespace.

namespace {

  class NullStreambuf : public std::streambuf {

   public:

    typedef std::streambuf::char_type   char_type;
    typedef std::streambuf::traits_type traits_type;
    typedef traits_type::int_type       int_type;
    typedef traits_type::off_type       off_type;
    typedef traits_type::pos_type       pos_type;

    NullStreambuf()
    { }

    ~NullStreambuf()
    { }

    virtual std::streamsize xsputn( const char* c, std::streamsize n )
    {
      return n;
    }

    virtual int_type overflow( int_type c = traits_type::eof() )
    {
      return traits_type::not_eof(c);
    }

  };

  class NullOstream : public std::ostream {

   public:
    NullOstream() : std::ostream( &m_buf ) { }

   private:
    NullStreambuf m_buf;

  };

}

//------------------------------------------------------------------------
// Test Log
//------------------------------------------------------------------------
// I spent some time trying to avoid a global singleton test log by
// instantiating a log and passing a pointer into the test cases, but
// the problem is that then this log needs to also be passed into any
// helper functions which call test macros. It just seemed to
// complicate things so for now we stick to a global singleton log.

const utst::TestLog::LogLevelEnum utst::TestLog::LogLevel::minimal  = 0;
const utst::TestLog::LogLevelEnum utst::TestLog::LogLevel::moderate = 1;
const utst::TestLog::LogLevelEnum utst::TestLog::LogLevel::verbose  = 2;

namespace utst {

  //----------------------------------------------------------------------
  // Constructors/Destructors
  //----------------------------------------------------------------------

  TestLog::TestLog()
  {
    m_log_level        = TestLog::LogLevel::minimal;
    m_log_ostream_ptr  = &std::cout;
    m_null_ostream_ptr = new NullOstream;
  }

  TestLog::~TestLog()
  {
    delete m_null_ostream_ptr;
  }

  //----------------------------------------------------------------------
  // Singleton accessor
  //----------------------------------------------------------------------

  TestLog& TestLog::instance()
  {
    static TestLog s_instance;
    return s_instance;
  }

  //----------------------------------------------------------------------
  // Log level
  //----------------------------------------------------------------------

  void TestLog::set_log_level( const TestLog::LogLevelEnum& log_level )
  {
    m_log_level = log_level;
  }

  TestLog::LogLevelEnum TestLog::get_log_level() const
  {
    return m_log_level;
  }

  //----------------------------------------------------------------------
  // Log stream
  //----------------------------------------------------------------------

  void TestLog::set_log_ostream( std::ostream* log_ostream_ptr )
  {
    m_log_ostream_ptr = log_ostream_ptr;
  }

  std::ostream&
  TestLog::get_log_ostream( const TestLog::LogLevelEnum& log_level )
  {
    if ( m_log_level >= log_level )
      return *m_log_ostream_ptr;
    else
      return *m_null_ostream_ptr;
  }

  //----------------------------------------------------------------------
  // Log test suite begin/end
  //----------------------------------------------------------------------

  void TestLog::log_test_suite_begin( const std::string& name )
  {
    *m_log_ostream_ptr << " Running test suite : " << name << "\n";
    if ( m_log_level != TestLog::LogLevel::minimal )
      *m_log_ostream_ptr << "\n";
  }

  void TestLog::log_test_suite_end()
  { }

  //----------------------------------------------------------------------
  // Log test case begin/end
  //----------------------------------------------------------------------

  void TestLog::log_test_case_begin( const std::string& name )
  {
    *m_log_ostream_ptr << "  + Running test case : " << name << "\n";
  }

  void TestLog::log_test_case_end()
  {
    if ( m_log_level != TestLog::LogLevel::minimal )
      *m_log_ostream_ptr << "\n";
  }

  //----------------------------------------------------------------------
  // Log note
  //----------------------------------------------------------------------

  void TestLog::log_note( const std::string& file_name, int line_num,
                          const std::string& note )
  {
    if ( m_log_level != TestLog::LogLevel::minimal )
      *m_log_ostream_ptr << "     [ -note- ] Line " << line_num
                         << " : " << note << std::endl;
  }

  //----------------------------------------------------------------------
  // Log test
  //----------------------------------------------------------------------

  void TestLog::log_test( const std::string& file_name, int line_num,
                          const std::string& description, bool result,
                          const std::string& msg )
  {
    if ( result && (m_log_level != TestLog::LogLevel::verbose) )
      return;

    *m_log_ostream_ptr
      << "     " << ((result) ? "[ passed ]" : "[ FAILED ]") << " ";

    if ( !file_name.empty() && (line_num > 0) )
      *m_log_ostream_ptr << "Line " << line_num << " : ";

    *m_log_ostream_ptr << description;

    if ( !msg.empty() )
      *m_log_ostream_ptr << " [ " << msg << " ]";

    *m_log_ostream_ptr << std::endl;
  }

}

