//========================================================================
// stdx-StringUtils.cc
//========================================================================

#include "stdx-StringUtils.h"

namespace stdx {

  //----------------------------------------------------------------------
  // to_lower
  //----------------------------------------------------------------------

  std::string to_lower( const std::string& str )
  {
    std::string ret_str;
    for ( unsigned int i = 0; i < str.length(); i++ ) {
      ret_str += std::tolower(str[i]);
    }
    return ret_str;
  }

  //----------------------------------------------------------------------
  // to_upper
  //----------------------------------------------------------------------

  std::string to_upper( const std::string& str )
  {
    std::string ret_str;
    for ( unsigned int i = 0; i < str.length(); i++ ) {
      ret_str += std::toupper(str[i]);
    }
    return ret_str;
  }

  //----------------------------------------------------------------------
  // has_prefix
  //----------------------------------------------------------------------

  bool has_prefix( const std::string& str, const std::string& prefix )
  {
    return (    ( str.length() >= prefix.length() )
             && ( str.substr(0,prefix.length()) == prefix ) );
  }

  //----------------------------------------------------------------------
  // has_suffix
  //----------------------------------------------------------------------

  bool has_suffix( const std::string& str, const std::string& suffix )
  {
    int pos = str.length() - suffix.length();
    return (    ( str.length() >= suffix.length() )
             && ( str.substr(pos,suffix.length()) == suffix ) );
  }

  //----------------------------------------------------------------------
  // remove_prefix
  //----------------------------------------------------------------------

  std::string remove_prefix( const std::string& str,
                             const std::string& prefix )
  {
    if ( has_prefix(str,prefix) ) {
      if ( str.length() == prefix.length() )
        return std::string("");
      else
        return str.substr( prefix.length() );
    }
    return str;
  }

  //----------------------------------------------------------------------
  // remove_suffix
  //----------------------------------------------------------------------

  std::string remove_suffix( const std::string& str,
                             const std::string& suffix )
  {
    if ( has_suffix(str,suffix) ) {
      if ( str.length() == suffix.length() )
        return std::string("");
      else
        return str.substr( 0, str.length()-suffix.length() );
    }
    return str;
  }

  //----------------------------------------------------------------------
  // trim_leading
  //----------------------------------------------------------------------

  std::string trim_leading( const std::string& str,
                            const std::string& chars )
  {
    if ( str.empty() )
      return std::string("");

    if ( chars.empty() )
      return str;

    std::string::size_type pos = str.find_first_not_of(chars);
    if ( pos == std::string::npos )
      return std::string("");

    return str.substr(pos);
  }

  //----------------------------------------------------------------------
  // trim_trailing
  //----------------------------------------------------------------------

  std::string trim_trailing( const std::string& str,
                             const std::string& chars )
  {
    if ( str.empty() )
      return std::string("");

    if ( chars.empty() )
      return str;

    std::string::size_type pos = str.find_last_not_of(chars);
    if ( pos == std::string::npos )
      return std::string("");

    return str.substr(0,pos+1);
  }

  //----------------------------------------------------------------------
  // trim
  //----------------------------------------------------------------------

  std::string trim( const std::string& str,
                    const std::string& leading_chars,
                    const std::string& trailing_chars )
  {
    if ( str.empty() )
      return std::string("");

    std::string::size_type pos1 = 0;
    if ( !leading_chars.empty() )
      pos1 = str.find_first_not_of(leading_chars);

    std::string::size_type pos2 = str.length()-1;
    if ( !trailing_chars.empty() )
      pos2 = str.find_last_not_of(trailing_chars);

    if (    ( (pos1 == std::string::npos) && (pos2 == std::string::npos) )
         || ( pos1 > pos2) )
    {
      return std::string("");
    }

    return str.substr(pos1,pos2-pos1+1);
  }

  //----------------------------------------------------------------------
  // split and return vector of substrings
  //----------------------------------------------------------------------

  std::vector<std::string>
  split( const std::string& str, const std::string& delimiter_chars )
  {
    std::vector<std::string> vec;
    split_to_oitr( std::back_inserter(vec), str, delimiter_chars );
    return vec;
  }

}

