//========================================================================
// stdx-ContainerUtils : Utilities for working with containers
//========================================================================
// This header provides functions and classes for initializing and
// formatting containers. Currently we focus on the STL vector and list
// containers although it should be straightforward to extend these
// techniques if necessary.

//------------------------------------------------------------------------
// Container Initialization
//------------------------------------------------------------------------
// The default way to initialize a container is to either set the size
// and directly access the elements (with a vector) or use the push_back
// method (with a vector or alist). Here are some examples of these
// approaches:
//
//  std::vector<int> vec(3);
//  vec.at(0) = 0;
//  vec.at(1) = 1;
//  vec.at(2) = 2;
//
//  std::vector<int> vec;
//  vec.push_back(0);
//  vec.push_back(1);
//  vec.push_back(2);
//
//  std::list<int> lst;
//  lst.push_back(0);
//  lst.push_back(1);
//  lst.push_back(2);
//
// This can become quite tedious when we want to create large containers
// or when we want to create small containers to pass as temporary
// objects. This header provides two new approaches to container
// initialization. The first overloads the += and , operators to enable
// the following syntax:
//
//  std::vector<int> vec;
//  vec += 0, 1, 2;
//
// This is typesafe and you will get an compile time error if you try
// and initialize the container with the wrong type. These operators use
// the push_back method. The second approach defines a set of functions
// which each take as input a different number of arguments and returns
// a newely created container enabling the following syntax:
//
//  std::vector<int> vec = stdx::mk_vec( 0, 1, 2 );
//
// You can combine these two approaches to elegantly initialize two
// dimensional vectors.
//
//  std::vector< std::vector<int> > vec;
//  vec += stdx::mk_vec( 0, 1, 2 ),
//         stdx::mk_vec( 2, 0, 1 ),
//         stdx::mk_vec( 1, 2, 0 );
//
// Note that because the return type of the mk functions is determined
// by the type of the initial elements, there is an issue with trying to
// initialize a container of strings like this:
//
//  std::vector<std::string> vec = stdx::mk_vec( "A", "B", "C" );
//
// The type of the three string literals is const char* so the mk_vec
// function will create a vector of const char* elements. This cannot be
// converted into a vector of strings so we will get a compile time
// errror. Instead we must explicitly specify the return type like this:
//
//  std::vector<std::string> vec
//    = stdx::mk_vec<std::string>( "A", "B", "C" );
//
// Finally, this header provides an easy way to initialize a vector or a
// list with a increasing sequence of values. For example, you can use
// the following will fill a vector and a list with the integers between
// 0 and 99:
//
//  std::vector<int> vec = mk_vec_seq(0,99);
//  std::list<int>   lst = mk_list_seq(0,99);
//

#ifndef STDX_CONTAINER_UTILS_H
#define STDX_CONTAINER_UTILS_H

#include "stdx-PreprocessorUtils.h"
#include <vector>
#include <list>

namespace stdx {

  //----------------------------------------------------------------------
  // PushBackProxy
  //----------------------------------------------------------------------
  // The PushBackProxy is used to overload the += and , operators for
  // containers which provide the push_back method. It is purely a proxy
  // which helps make sure the the correct operator gets called. It
  // should probably not be uesd directly but we need to include it here
  // because it needs to be in the same namespace as the overloaded
  // comma operator. See the comments for the += and , operators for
  // more information.

  template < typename T >
  class PushBackProxy {

   public:
    PushBackProxy( T& container )
     : m_container( container ) { }

    template < typename V >
    inline void push_back( const V& value )
    {
      m_container.push_back(value);
    }

   private:
    T& m_container;

  };

  //----------------------------------------------------------------------
  // operator += for containers
  //----------------------------------------------------------------------
  // We overload the += operator for containers so that it first pushes
  // the given element into the container and then returns a proxy
  // object. This allows us to use the following syntax:
  //
  //  std::vector<int> vec;
  //  vec += 0;
  //  vec += 1;
  //  vec += 2;
  //
  // The += operator by itself is not that useful, but combining it with
  // the , operator creates quite a nice syntax. See the , operator
  // description for more details. Overloaded operators need to be in
  // the same namespace as the type we are overloading for. Since the
  // STL containers are in the std namespace we need to also put the
  // overloaded += operator in the std namespace.

} namespace std {

   template < typename T, typename V >
   stdx::PushBackProxy< std::vector<T> >
   operator+=( std::vector<T>& container, V value );

   template < typename T, typename V >
   stdx::PushBackProxy< std::list<T> >
   operator+=( std::list<T>& container, V value );

} namespace stdx {

  //----------------------------------------------------------------------
  // operator , for containers
  //----------------------------------------------------------------------
  // Since the += operator returns a proxy object, if we overload the ,
  // operator for these proxy objects then we can continue to push new
  // elements into the container using this very nice syntax:
  //
  //  std::vector<int> vec;
  //  vec += 0, 1, 2;
  //

  template < typename T, typename V >
  PushBackProxy<T> operator,( PushBackProxy<T> container, V value );

  //----------------------------------------------------------------------
  // mk_vec and mk_list
  //----------------------------------------------------------------------
  // Although the += and , syntax is nice for filling large containers,
  // sometimes we just want to create a small container "in-place". For
  // example, we might want to pass a small temporary vector into a
  // function or initialize a small vector with just a few elements. The
  // templated mk_vec and mk_list functions allow us to do this. We use
  // the code generation preprocessor macros to generate several
  // different functions each taking a different number of arguments.
  // Here is an exmaple of using these functions:
  //
  //  std::vector<int> vec = mk_vec( 0, 1, 2 );
  //  std::list<int>   lst = mk_list( 0, 1, 2 );
  //

  template < typename T > std::vector<T> mk_vec();
  template < typename T > std::list<T>   mk_list();

  #define STDX_MK_CONT_DECL_LB( count_, funcname_, cont_ )              \
    template < typename T >                                             \
    cont_<T>                                                            \
    funcname_( STDX_PP_ENUM_PARAMS( STDX_PP_INC(count_), const T& v ) );

  STDX_PP_LOOP( 10, STDX_MK_CONT_DECL_LB, mk_vec,  std::vector );
  STDX_PP_LOOP( 10, STDX_MK_CONT_DECL_LB, mk_list, std::list   );

  //----------------------------------------------------------------------
  // mk_vec_seq and mk_list_seq
  //----------------------------------------------------------------------
  // These functions create vectors or lists with a sequence of values.
  // The templated argument needs a copy constructor, an equality
  // operator, and an incrementor (++) operator. For example, here is
  // how we can fill a vector with the integers between 0 and 99:
  //
  //  std::vector<int> vec = mk_vec_seq(0,99);
  //

  template < class T >
  std::vector<T> mk_vec_seq( const T& min_value, const T& max_value );

  template < class T >
  std::list<T> mk_list_seq( const T& min_value, const T& max_value );

}

#include "stdx-ContainerUtils.inl"
#endif /* STDX_CONTAINER_UTILS_H */

