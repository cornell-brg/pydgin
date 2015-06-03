//========================================================================
// stdx-StringUtils : String utility functions
//========================================================================
// This file contains functions and classes for creating and
// manipulating STL strings.

#ifndef STDX_STRING_UTILS_H
#define STDX_STRING_UTILS_H

#include "stdx-Exception.h"
#include "stdx-Enum.h"
#include "stdx-PreprocessorUtils.h"
#include <string>

namespace stdx {

  //----------------------------------------------------------------------
  // to_str
  //----------------------------------------------------------------------
  // To convert an object to a string we usually need to use a
  // ostringstream like this:
  //
  //  ostringstream ost;
  //  ost << foo;
  //  std::string foo_str = ost.c_str();
  //
  // The to_str template functions do this conversion for any type. The
  // function requires the insertion operator to be overloaded for the
  // supplied template type.
  //
  //  std::string foo_str = to_str(foo);
  //
  // There are many to_str functions, each taking a different number of
  // input arguments (which can all be of different types). All of the
  // arguments are concatenated into one long string. For example,
  // assume we are naming an array of objects and we want each name to
  // be something like "obj[i][j]" where i and j are two ints. Here is
  // the standard way using ostringstreams:
  //
  //  ostringstream ost;
  //  ost << "obj[" << i << "][" << j << "]";
  //  obj.set_name( ost.c_str() );
  //
  // Here is the way using the single argument version of to_str:
  //
  //  obj.set_name( "obj[" + to_str(i) + "][" + to_str(j) + "]" );
  //
  // And here is how we can do it using the multiple argument to_str:
  //
  //  obj.set_name( to_str("obj[",i,"][",j,"]") );
  //
  // We use the STDX_PP code generation macros in
  // stdx-PreprocessorUtils.h to generate 10 version of this function
  // with each function taking a different number of arguments.

  #define STDX_TO_STR_DECL_LB1( count_ ) \
    const T ## count_ & v ## count_

  #define STDX_TO_STR_DECL_LB0( count_ )                                \
    template < STDX_PP_ENUM_PARAMS( STDX_PP_INC(count_), typename T ) > \
    std::string to_str( STDX_PP_LOOP_C( STDX_PP_INC(count_),            \
                                        STDX_TO_STR_DECL_LB1 ) );

  STDX_PP_LOOP( 10, STDX_TO_STR_DECL_LB0 );

  //----------------------------------------------------------------------
  // from_str
  //----------------------------------------------------------------------
  // To create an object from a string we usually need to use an
  // istringstream like this:
  //
  //  Foo foo;
  //  istringstream ist(foo_str);
  //  ist >> foo;
  //  assert( !ist.fail() );
  //
  // The from_str template function is a little wrapper which does this
  // conversion for any type. The function requires the extraction
  // operator to be overloaded for the target type, and the target type
  // also needs a default constructor.
  //
  //  Foo foo = from_str<Foo>(foo_str);
  //
  // Notice that we must supply the conversion type as a template
  // argument so the function knows how to do the conversion. The
  // function will throw an EInvalidFromString exception in two cases:
  // (a) if after the extraction the stream is in an invalid state or
  // (b) there is non-white space left in the string after extraction.

  struct EInvalidFromString : public stdx::Exception { };

  template < typename T >
  T from_str( const std::string& str );

  //----------------------------------------------------------------------
  // Prefix/Suffix
  //----------------------------------------------------------------------
  // These functions can test for a given prefix/suffix and they can
  // remove that prefix/suffix.

  // Return true if str has the given prefix
  bool has_prefix( const std::string& str, const std::string& prefix );

  // Return true if str has the given suffix
  bool has_suffix( const std::string& str, const std::string& suffix );

  // Remove the prefix from str, return str unchanged if no prefix
  std::string remove_prefix( const std::string& str,
                             const std::string& prefix );

  // Remove the suffix from str, return str unchanged if no suffix
  std::string remove_suffix( const std::string& str,
                             const std::string& suffix );

  //----------------------------------------------------------------------
  // Trim Leading/Trailing
  //----------------------------------------------------------------------
  // These functions trim characters from either the beginning, the end,
  // or both sides of a string. The characters to trim are given as a
  // string and the default is to trim whitespace.

  // Trim any of the characters in the chars string from front of str
  std::string trim_leading( const std::string& str,
                            const std::string& chars = " \t\n" );

  // Trim any of the characters in the chars string from end of str
  std::string trim_trailing( const std::string& str,
                             const std::string& chars = " \t\n" );

  // Trim any of the characters in leading_chars string from front of
  // str and any characters in trailing_chars string from end of str
  std::string trim( const std::string& str,
                    const std::string& leading_chars = " \t\n",
                    const std::string& trailing_chars = " \t\n" );

  //----------------------------------------------------------------------
  // to_upper/to_lower
  //----------------------------------------------------------------------

  // Converts a string to all lower case
  std::string to_lower( const std::string& str );

  // Converts a string to all upper case
  std::string to_upper( const std::string& str );

  //----------------------------------------------------------------------
  // split
  //----------------------------------------------------------------------
  // These functions will split a string into substrings based on the
  // given delimiter characters. There are two versions: one writes the
  // substrings to an output iterator while the other simply returns a
  // new vector with the substrings.

  template < typename Itr >
  void split_to_oitr( Itr out_itr, const std::string& str,
                      const std::string& delimiter_chars = " \t\n" );

  std::vector<std::string>
  split( const std::string& str,
         const std::string& delimiter_chars = " \t\n" );

}

#include "stdx-StringUtils.inl"
#endif /* STDX_STRING_UTILS_H */

