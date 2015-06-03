//========================================================================
// stdx-PairUtils : Utilities for working with STL pairs
//========================================================================

#ifndef STDX_PAIR_UTILS_H
#define STDX_PAIR_UTILS_H

#include <iostream>
#include <map>

namespace stdx {

  //----------------------------------------------------------------------
  // mk_pair
  //----------------------------------------------------------------------
  // When we want to create temporary pairs we can use this syntax:
  //
  //  std::pair<int,int>(1,1)
  //
  // Although this syntax doesn't seem too bad, notice that we have to
  // include the types of the pair items in the constructor. When the
  // pair stores more complicated types this can get pretty ugly.
  // Instead we can use the templated mk_pair helper function. The types
  // of the pair items will be inferred. The mk_pair function is similar
  // to the std::make_pair function except that it uses the mk_ prefix
  // which is common throughput the stdx subproject.
  //
  //  std::mk_pair(1,1)
  //

  template < typename T, typename U >
  std::pair<T,U> mk_pair( const T& value1, const U& value2 );

  //----------------------------------------------------------------------
  // Insertion operator
  //----------------------------------------------------------------------

} namespace std {

  template < typename T, typename U >
  std::ostream& operator<<( std::ostream& os, const std::pair<T,U>& p );

} namespace stdx {

}

#include "stdx-PairUtils.inl"
#endif /* STDX_PAIR_UTILS_H */

