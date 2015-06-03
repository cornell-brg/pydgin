//========================================================================
// stdx-InputRange : Input ranges for STL containers
//========================================================================
// Usually we want to use an STL algorithm on a whole container, but to
// do so requires some tedious syntax:
//
//  for_each( vec.begin(), vec.end(), mem_fun(&Foo::method) );
//
// Specifying the container name twice is verbose and error prone. Input
// ranges offer a convenient syntax which makes the common case much
// more succinct. An input range is basically just a pair of iterators
// which delimit a range in a container. So we can first create an input
// range which delimits the entire container and then pass it into an
// overloaded version of the desired algorithm which just "unpacks" the
// range. Here's the previous example using an input range:
//
//  stdx::InputRange<vector<int>::iterator> irange(vec.begin(),vec.end());
//  stdx::for_each( irange, mem_fun(&Foo::method) );
//
// Obviously this seems even more verbose than the original syntax, but
// a mk_irange helper function is provided in this header which prevents
// us from having to explicitly create the input range (and thus
// explicitly specify the iterator type):
//
//  stdx::for_each( stdx::mk_irange(vec), mem_fun(&Foo::method) );
//
// We also provide the mk_cirange helper function which creates an input
// range that contains constant iterators. The overloaded version of
// for_each is defined in this header and just looks like this:
//
//  template < typename InItr, typename Func >
//  inline Func for_each( InputRange<InItr> ir, Func f )
//  {
//    return std::for_each( ir.start, ir.end, f );
//  }
//
// This should add no overhead as long as it is inlined. The idea for
// input ranges comes from Stroustrup's "The C++ Programming Language:
// 3rd Edition" Section 18.3.1.

#ifndef STDX_INPUT_RANGE_H
#define STDX_INPUT_RANGE_H

#include <algorithm>
#include <numeric>

namespace stdx {

  //----------------------------------------------------------------------
  // InputRange
  //----------------------------------------------------------------------
  // This is the actual input range object which holds two iterators
  // delimiting a range in an container. Most of the time a user will
  // just use the mk_irange/mk_cirange helper functions instead of
  // explicitly instantiating an InputRange.

  template < typename Itr >
  class InputRange {
   public:

    InputRange() { }
    InputRange( Itr start_, Itr end_ )
      : start(start_), end(end_)
    { };

    Itr start;
    Itr end;
  };

  //----------------------------------------------------------------------
  // mk_irange/mk_cirange
  //----------------------------------------------------------------------
  // These helper functions make it much simpler to create and use input
  // ranges. The mk_cirange version creates an input range that uses
  // constant iterators.

  template < typename Cont >
  InputRange<typename Cont::iterator> mk_irange( Cont& c );

  template < typename Cont >
  InputRange<typename Cont::const_iterator> mk_cirange( Cont& c );

  //----------------------------------------------------------------------
  // Standard algorithms overloaded for use with input ranges
  //----------------------------------------------------------------------

  template < typename InItr, typename Func >
  Func for_each( InputRange<InItr> ir, Func f );

  template < typename InItr, typename T >
  InItr find( InputRange<InItr> ir, const T& v );

  template < typename InItr, typename Pred >
  InItr find_if( InputRange<InItr> ir, Pred p );

  template < typename InItr, typename T >
  InItr remove( InputRange<InItr> ir, const T& v );

  template < typename InItr, typename Pred >
  InItr remove_if( InputRange<InItr> ir, Pred p );

  template < typename InItr, typename OutItr >
  OutItr copy( InputRange<InItr> ir, OutItr res );

  template < typename InItr, typename Cmp >
  void sort( InputRange<InItr> ir, Cmp cmp );

  template < typename InItr >
  void sort( InputRange<InItr> ir );

  template < typename InItr, typename Cmp >
  void stable_sort( InputRange<InItr> ir, Cmp cmp );

  template < typename InItr1, typename InItr2, typename Func >
  Func for_each( InputRange<InItr1> ir, InItr2 iitr, Func op );

  template < typename InItr, typename OutItr, typename Func >
  OutItr transform( InputRange<InItr> ir, OutItr oitr, Func op );

  template < typename InItr, typename InItr2,
             typename OutItr, typename Func >
  OutItr transform( InputRange<InItr> ir, InItr2 iitr,
                    OutItr oitr, Func op );

  template < typename InItr >
  InItr min_element( InputRange<InItr> ir );

  template < typename InItr, typename Cmp >
  InItr unique( InputRange<InItr> ir, Cmp cmp );

  template < typename InItr >
  InItr unique( InputRange<InItr> ir );

  template < typename InItr, typename OutItr, typename Cmp >
  OutItr unique_copy( InputRange<InItr> ir, OutItr oitr, Cmp cmp );

  template < typename InItr, typename OutItr >
  OutItr unique_copy( InputRange<InItr> ir, OutItr oitr );

  template < typename InItr1, typename InItr2 >
  bool equal( InputRange<InItr1> ir, InItr2 itr );

  template < typename InItr, typename Func >
  void generate( InputRange<InItr> ir, Func f );

  template < typename InItr, typename T >
  void fill( InputRange<InItr> ir, const T& val );

  template < typename InItr >
  void rotate( InputRange<InItr> ir, InItr mitr );

  template < typename InItr, typename OutItr >
  void rotate_copy( InputRange<InItr> ir, InItr mitr, OutItr oitr );

  template < typename InItr >
  InItr max_element( InputRange<InItr> ir );

  template < typename InItr, typename Pred >
  typename std::iterator_traits<InItr>::difference_type
  count_if( InputRange<InItr> ir, Pred p );

  template < typename InItr, typename T >
  typename std::iterator_traits<InItr>::difference_type
  count( InputRange<InItr> ir, T v );

  template < typename InItr, typename T >
  T accumulate( InputRange<InItr> ir, T v );

  //----------------------------------------------------------------------
  // copy_if
  //----------------------------------------------------------------------
  // This is a copy_if algorithm taken from Stroustrup's "The C++
  // Programming Language: 3rd Edition" Section 18.6.1. For some reason
  // it was not included in the actual standard template library.

  template <typename In, typename Out, typename Pred>
  Out copy_if( In first, In last, Out res, Pred p );

  //----------------------------------------------------------------------
  // equal
  //----------------------------------------------------------------------
  // The standard equal algorithm assumes that both ranges are the same
  // size. This version of the algorithm does not make this assumption
  // and returns false if the two input ranges are not the same size.

  template < typename InItr1, typename InItr2 >
  bool equal( InputRange<InItr1> ir1, InputRange<InItr2> ir2 );

  //----------------------------------------------------------------------
  // reduce_and/or
  //----------------------------------------------------------------------
  // These functions implement a boolean reduction over the given input
  // range. The given function object (which must return a boolean) is
  // applied to each element in the input range and the results are
  // combined together using either a logical and or a logical or. So
  // for example, if we have a vector of objects which each have a
  // is_valid method we can easily see if any object is valid or if all
  // objects are valid:
  //
  //  all_valid = reduce_and( mk_irange(vec), mem_fun(&Foo::is_valid) );
  //  any_valid = reduce_or( mk_irange(vec), mem_fun(&Foo::is_valid) );
  //

  template < typename InItr, typename Func >
  bool reduce_and( InputRange<InItr> ir, Func f );

  template < typename InItr, typename Func >
  bool reduce_or( InputRange<InItr> ir, Func f );

}

#include "stdx-InputRange.inl"
#endif /* STDX_INPUT_RANGE_H */

