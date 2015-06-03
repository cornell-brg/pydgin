//========================================================================
// stdx-Exception : Exception base class and helper macros
//========================================================================

#include "stdx-ReflectionUtils.h"
#include <sstream>
#include <string>

namespace stdx {
namespace details {

  //----------------------------------------------------------------------
  // mk_exception
  //----------------------------------------------------------------------
  // This helper function formats the file name, line number, class
  // name, function name, and error message into a nice looking string.
  // In then instantiates an exception object of type E and sets the
  // message via the set_msg method before returning the exception
  // object. This function simplifies our exception macros below.

  template < typename E >
  E mk_exception( const std::string& file_name, int line_num,
                  const std::string& class_name,
                  const std::string& func_name,
                  const std::string& msg )
  {
    std::ostringstream ost;
    ost << " " << stdx::demangle_type<E>() << "\n";
    ost << "   File  : " << file_name << ":" << line_num << "\n";
    if ( !class_name.empty() )
      ost << "   Class : " << class_name << "\n";
    ost << "   Func  : " << func_name << "\n";
    ost << "   Msg   : " << msg << std::endl;
    E exception;
    exception.set_msg( ost.str() );
    return exception;
  }

}
}

//------------------------------------------------------------------------
// STDX_THROW
//------------------------------------------------------------------------

#define STDX_THROW_( excep_, msg_ )                                     \
{                                                                       \
  std::ostringstream ost;                                               \
  ost << msg_;                                                          \
  throw stdx::details::mk_exception<excep_>                             \
    ( __FILE__, __LINE__, "", STDX_FUNCTION_NAME, ost.str() );          \
}

//------------------------------------------------------------------------
// STDX_M_THROW
//------------------------------------------------------------------------

#define STDX_M_THROW_( excep_, msg_ )                                   \
{                                                                       \
  std::ostringstream ost;                                               \
  ost << msg_;                                                          \
  throw stdx::details::mk_exception<excep_>                             \
    ( __FILE__, __LINE__, stdx::demangle_type(*this),                   \
      STDX_FUNCTION_NAME, ost.str() );                                  \
}

//------------------------------------------------------------------------
// STDX_ASSERT
//------------------------------------------------------------------------

#define STDX_ASSERT_( assertion_ )                                      \
  if ( !(assertion_) ) {                                                \
    STDX_THROW_( stdx::EAssert,                                         \
      "Assertion (" << #assertion_ << ") failed" ); }

//------------------------------------------------------------------------
// STDX_M_ASSERT
//------------------------------------------------------------------------

#define STDX_M_ASSERT_( assertion_ )                                    \
  if ( !(assertion_) ) {                                                \
    STDX_M_THROW_( stdx::EAssert,                                       \
      "Assertion (" << #assertion_ << ") failed" ); }

//------------------------------------------------------------------------
// STDX_PERFCRIT_ASSERT
//------------------------------------------------------------------------

#ifdef STDX_PERFCRIT_ASSERT_OFF
#define STDX_PERFCRIT_ASSERT_( assertion_ )
#else
#define STDX_PERFCRIT_ASSERT_( assertion_ ) \
  STDX_ASSERT_( assertion_ )
#endif

//------------------------------------------------------------------------
// STDX_PERFCRIT_M_ASSERT
//------------------------------------------------------------------------

#ifdef STDX_PERFCRIT_ASSERT_OFF
#define STDX_PERFCRIT_M_ASSERT_( assertion_ )
#else
#define STDX_PERFCRIT_M_ASSERT_( assertion_ ) \
  STDX_M_ASSERT_( assertion_ )
#endif

