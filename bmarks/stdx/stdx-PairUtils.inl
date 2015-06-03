//========================================================================
// stdx-PairUtils.inl
//========================================================================

namespace stdx {

  //----------------------------------------------------------------------
  // mk_pair
  //----------------------------------------------------------------------

  template < typename T, typename U >
  std::pair<T,U> mk_pair( const T& value1, const U& value2 )
  {
    return std::pair<T,U>(value1,value2);
  }

  //----------------------------------------------------------------------
  // Insertion operator
  //----------------------------------------------------------------------

} namespace std {

  template < typename T, typename U >
  std::ostream& operator<<( std::ostream& os, const std::pair<T,U>& p )
  {
    return ( os << "(" << p.first << "," << p.second << ")" );
  }

} namespace stdx {

}

