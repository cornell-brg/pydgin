//========================================================================
// stdx-InputRange.inl
//========================================================================

namespace stdx {

  //----------------------------------------------------------------------
  // mk_irange/mk_cirange
  //----------------------------------------------------------------------

  template < typename Cont >
  inline InputRange<typename Cont::iterator>
  mk_irange( Cont& c )
  {
    return InputRange<typename Cont::iterator>(c.begin(),c.end());
  }

  template < typename Cont >
  inline InputRange<typename Cont::const_iterator>
  mk_cirange( Cont& c )
  {
    return InputRange<typename Cont::const_iterator>(c.begin(),c.end());
  }

  //----------------------------------------------------------------------
  // Standard algorithms overloaded for use with input ranges
  //----------------------------------------------------------------------

  template < typename InItr, typename Func >
  inline Func for_each( InputRange<InItr> ir, Func f )
  {
    return std::for_each( ir.start, ir.end, f );
  }

  template < typename InItr, typename T >
  inline InItr find( InputRange<InItr> ir, const T& v )
  {
    return std::find( ir.start, ir.end, v );
  }

  template < typename InItr, typename Pred >
  inline InItr find_if( InputRange<InItr> ir, Pred p )
  {
    return std::find_if( ir.start, ir.end, p );
  }

  template < typename InItr, typename T >
  inline InItr remove( InputRange<InItr> ir, const T& v )
  {
    return std::remove( ir.start, ir.end, v );
  }

  template < typename InItr, typename Pred >
  inline InItr remove_if( InputRange<InItr> ir, Pred p )
  {
    return std::remove_if( ir.start, ir.end, p );
  }

  template < typename InItr, typename OutItr >
  inline OutItr copy( InputRange<InItr> ir, OutItr res )
  {
    return std::copy( ir.start, ir.end, res );
  }

  template < typename InItr, typename Cmp >
  inline void sort( InputRange<InItr> ir, Cmp cmp )
  {
    return std::sort( ir.start, ir.end, cmp );
  }

  template < typename InItr >
  inline void sort( InputRange<InItr> ir )
  {
    return std::sort( ir.start, ir.end );
  }

  template < typename InItr, typename Cmp >
  inline void stable_sort( InputRange<InItr> ir, Cmp cmp )
  {
    return std::stable_sort( ir.start, ir.end, cmp );
  }

  template < typename InItr1, typename InItr2, typename Func >
  inline Func for_each( InputRange<InItr1> ir, InItr2 iitr, Func op )
  {
    return std::for_each( ir.start, ir.end, iitr, op );
  }

  template < typename InItr, typename OutItr, typename Func >
  inline OutItr transform( InputRange<InItr> ir, OutItr oitr, Func op )
  {
    return std::transform( ir.start, ir.end, oitr, op );
  }

  template < typename InItr, typename InItr2,
             typename OutItr, typename Func >
  inline OutItr transform( InputRange<InItr> ir, InItr2 iitr,
                           OutItr oitr, Func op )
  {
    return std::transform( ir.start, ir.end, iitr, oitr, op );
  }

  template < typename InItr >
  inline InItr min_element( InputRange<InItr> ir )
  {
    return std::min_element( ir.start, ir.end );
  }

  template < typename InItr, typename Cmp >
  inline InItr unique( InputRange<InItr> ir, Cmp cmp )
  {
    return std::unique( ir.start, ir.end, cmp );
  }

  template < typename InItr >
  inline InItr unique( InputRange<InItr> ir )
  {
    return std::unique( ir.start, ir.end );
  }

  template < typename InItr, typename OutItr, typename Cmp >
  inline OutItr unique_copy( InputRange<InItr> ir, OutItr oitr, Cmp cmp )
  {
    return std::unique_copy( ir.start, ir.end, oitr, cmp );
  }

  template < typename InItr, typename OutItr >
  inline OutItr unique_copy( InputRange<InItr> ir, OutItr oitr )
  {
    return std::unique_copy( ir.start, ir.end, oitr );
  }

  template < typename InItr1, typename InItr2 >
  inline bool equal( InputRange<InItr1> ir, InItr2 itr )
  {
    return std::equal( ir.start, ir.end, itr );
  }

  template < typename InItr, typename Func >
  inline void generate( InputRange<InItr> ir, Func f )
  {
    std::generate( ir.start, ir.end, f );
  }

  template < typename InItr, typename T >
  inline void fill( InputRange<InItr> ir, const T& val )
  {
    std::fill( ir.start, ir.end, val );
  }

  template < typename InItr >
  inline void rotate( InputRange<InItr> ir, InItr mitr )
  {
    std::rotate( ir.start, mitr, ir.end );
  }

  template < typename InItr, typename OutItr >
  inline void rotate_copy( InputRange<InItr> ir, InItr mitr, OutItr oitr )
  {
    std::rotate_copy( ir.start, mitr, ir.end, oitr );
  }

  template < typename InItr >
  inline InItr max_element( InputRange<InItr> ir )
  {
    return std::max_element( ir.start, ir.end );
  }

  template < typename InItr, typename Pred >
  inline typename std::iterator_traits<InItr>::difference_type
  count_if( InputRange<InItr> ir, Pred p )
  {
    return std::count_if( ir.start, ir.end, p );
  }

  template < typename InItr, typename T >
  inline typename std::iterator_traits<InItr>::difference_type
  count( InputRange<InItr> ir, T v )
  {
    return std::count( ir.start, ir.end, v );
  }

  template < typename InItr, typename T >
  inline T accumulate( InputRange<InItr> ir, T v )
  {
    return std::accumulate( ir.start, ir.end, v );
  }

  //----------------------------------------------------------------------
  // copy_if
  //----------------------------------------------------------------------

  template <typename In, typename Out, typename Pred>
  Out copy_if( In first, In last, Out res, Pred p )
  {
    while (first != last) {
      if (p(*first)) *res++ = *first;
      ++first;
    }
    return res;
  }

  //----------------------------------------------------------------------
  // equal
  //----------------------------------------------------------------------

  template < typename InItr1, typename InItr2 >
  bool equal( InputRange<InItr1> ir1, InputRange<InItr2> ir2 )
  {
    while ( (ir1.start != ir1.end) && (ir2.start != ir2.end) )
      if ( *ir1.start++ != *ir2.start++ )
        return false;

    return ( (ir1.start == ir1.end) && (ir2.start == ir2.end) );
  }

  //----------------------------------------------------------------------
  // reduce_and
  //----------------------------------------------------------------------

  template < typename InItr, typename Func >
  bool reduce_and( InputRange<InItr> ir, Func f )
  {
    bool v = true;
    while ( ir.start != ir.end )
      v &= f(*ir.start++);
    return v;
  }

  //----------------------------------------------------------------------
  // reduce_or
  //----------------------------------------------------------------------

  template < typename InItr, typename Func >
  bool reduce_or( InputRange<InItr> ir, Func f )
  {
    bool v = false;
    while ( ir.start != ir.end )
      v |= f(*ir.start++);
    return v;
  }

}

