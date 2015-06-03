//========================================================================
// stdx-ContainerUtils.inl
//========================================================================

#include "stdx-Exception.h"

namespace stdx {

  //----------------------------------------------------------------------
  // += operator for vector and list
  //----------------------------------------------------------------------

} namespace std {

  template < typename T, typename V >
  stdx::PushBackProxy< std::vector<T> >
  operator+=( std::vector<T>& container, V value )
  {
    container.push_back(value);
    return stdx::PushBackProxy< std::vector<T> >(container);
  }

  template < typename T, typename V >
  stdx::PushBackProxy< std::list<T> >
  operator+=( std::list<T>& container, V value )
  {
    container.push_back(value);
    return stdx::PushBackProxy< std::list<T> >(container);
  }

}
namespace stdx {

  //----------------------------------------------------------------------
  // , operator for PushBackProxy
  //----------------------------------------------------------------------
  // Note that we cannot overload the , operator for the container
  // classes directly otherwise the compiler would try to call our new
  // operator when we pass containers as parameters to functions:
  //
  //  std::vector<int> vec1;
  //  std::vector<int> vec2;
  //  foo( vec1, vec2 ); // would call , operator for vec2!

  template < typename T, typename V >
  PushBackProxy<T> operator,( PushBackProxy<T> container, V value )
  {
    container.push_back(value);
    return container;
  }

  //----------------------------------------------------------------------
  // mk_vec and mk_list
  //----------------------------------------------------------------------

  template < class T >
  std::vector<T> mk_vec()
  {
    return std::vector<T>();
  }

  template < class T >
  std::list<T> mk_list()
  {
    return std::list<T>();
  }

  #define STDX_MK_CONT_DEF_LB( count_, funcname_, cont_ )               \
    template < class T >                                                \
    cont_<T>                                                            \
    funcname_( STDX_PP_ENUM_PARAMS( STDX_PP_INC(count_), const T& v ) ) \
    {                                                                   \
      cont_<T> c_;                                                      \
      c_ += STDX_PP_ENUM_PARAMS( STDX_PP_INC(count_), v );              \
      return c_;                                                        \
    }

  STDX_PP_LOOP( 10, STDX_MK_CONT_DEF_LB, mk_vec,  std::vector );
  STDX_PP_LOOP( 10, STDX_MK_CONT_DEF_LB, mk_list, std::list   );

  //----------------------------------------------------------------------
  // mk_vec_seq and mk_list_seq
  //----------------------------------------------------------------------

  template < class T >
  std::vector<T> mk_vec_seq( const T& min_value, const T& max_value )
  {
    STDX_ASSERT( min_value <= max_value );

    std::vector<T> vec;
    T value( min_value );

    while ( !(value == max_value) )
      vec.push_back(value++);
    vec.push_back(value++);

    return vec;
  }

  template < class T >
  std::list<T> mk_list_seq( const T& min_value, const T& max_value )
  {
    STDX_ASSERT( min_value <= max_value );

    std::list<T> lst;
    T value( min_value );

    while ( !(value == max_value) )
      lst.push_back(value++);
    lst.push_back(value++);

    return lst;
  }

}

