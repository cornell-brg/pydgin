//========================================================================
// stdx-ReflectionUtils.inl
//========================================================================

#include <string>
#include <typeinfo>
#include <cstdlib>

#ifdef STDX_HAVE_ABI_CXA_DEMANGLE
#include <cxxabi.h>
#endif

namespace stdx {

  //----------------------------------------------------------------------
  // Function name demangling
  //----------------------------------------------------------------------

namespace details {

  inline std::string extract_funct_name( const std::string& str )
  {
    std::string temp_str = str.substr( 0, str.find('(') );
    return temp_str.substr( temp_str.rfind(' ') + 1 );
  }

}

  //----------------------------------------------------------------------
  // is_a operator
  //----------------------------------------------------------------------

  template < typename T, typename C >
  bool is_a( const C& obj )
  {
    const T* ptr = dynamic_cast<const T*>(&obj);
    return (ptr != 0);
  }

  //----------------------------------------------------------------------
  // demangle_type
  //----------------------------------------------------------------------

  template < typename T >
  std::string demangle_type()
  {
    #ifdef STDX_HAVE_ABI_CXA_DEMANGLE
      int err;
      char* output = abi::__cxa_demangle( typeid(T).name(), 0, 0, &err );
    #else
      char* output = 0;
    #endif

    // If demangling fails then just return the mangled name
    if ( output == 0 )
      return typeid(T).name();

    // Otherwise return the demangled name as a string
    else {
      std::string ret_str(output);
      free(output);
      return ret_str;
    }
  }

  template < typename T >
  std::string demangle_type( const T& obj )
  {
    #ifdef STDX_HAVE_ABI_CXA_DEMANGLE
      int err;
      char* output = abi::__cxa_demangle( typeid(obj).name(), 0, 0, &err );
    #else
      char* output = 0;
    #endif

    // If demangling fails then just return the mangled name
    if ( output == 0 )
      return typeid(obj).name();

    // Otherwise return the demangled name as a string
    else {
      std::string ret_str(output);
      free(output);
      return ret_str;
    }
  }

}

