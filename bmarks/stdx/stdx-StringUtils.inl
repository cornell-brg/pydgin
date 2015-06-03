//========================================================================
// stdx-StringUtils.inl
//========================================================================

#include "stdx-ReflectionUtils.h"
#include <sstream>

namespace stdx {

  //----------------------------------------------------------------------
  // to_str
  //----------------------------------------------------------------------

  #define STDX_TO_STR_DEF_LB1( count_ ) \
    v ## count_ <<

  #define STDX_TO_STR_DEF_LB0( count_ )                                 \
    template < STDX_PP_ENUM_PARAMS( STDX_PP_INC(count_), typename T ) > \
    std::string to_str( STDX_PP_LOOP_C( STDX_PP_INC(count_),            \
                                        STDX_TO_STR_DECL_LB1 ) )        \
    {                                                                   \
      std::ostringstream ost;                                           \
      ost << STDX_PP_LOOP_X1( STDX_PP_INC(count_),                      \
                              STDX_TO_STR_DEF_LB1 ) "";                 \
      return ost.str();                                                 \
    }

  STDX_PP_LOOP( 10, STDX_TO_STR_DEF_LB0 );

  //----------------------------------------------------------------------
  // from_str
  //----------------------------------------------------------------------

  template < typename T >
  T from_str( const std::string& str )
  {
    T ret_val;
    std::istringstream ist(str);
    ist >> ret_val;

    // Make sure the extraction did not cause an error

    if ( ist.fail() )
      STDX_THROW( stdx::EInvalidFromString, \
       "Cannot convert \"" << str << "\" into a " << demangle_type<T>() );

    // Make sure there is nothing else at the end of the string

    char c;
    ist >> c;
    if ( ist )
      STDX_THROW( stdx::EInvalidFromString, \
       "Cannot convert \"" << str << "\" into a " << demangle_type<T>() );

    return ret_val;
  }

  //----------------------------------------------------------------------
  // split into output iterator
  //----------------------------------------------------------------------

  template < typename Itr >
  void split_to_oitr( Itr oitr, const std::string& str,
                      const std::string& delimiter_chars )
  {
    using namespace std;

    string::size_type pos1 = 0;
    while ( pos1 < str.length() ) {

      // Eat leading delimiters
      pos1 = str.find_first_not_of(delimiter_chars,pos1);

      // String ended with delimiters
      if ( pos1 == std::string::npos )
        break;

      // Find the end of the token
      string::size_type pos2 = str.find_first_of(delimiter_chars,pos1);

      // Write token to output iterator
      if ( pos2 == string::npos ) {
        (*oitr++) = str.substr(pos1);
        break;
      }
      else
        (*oitr++) = str.substr(pos1,pos2-pos1);

      // Set up for next loop
      pos1 = pos2 + 1;

    }

  }

}

