//========================================================================
// stdx-BitContainer.inl
//========================================================================

#include "stdx-StaticAssert.h"
#include "stdx-DebugUtils.h"

//========================================================================
// Details
//========================================================================
// We create a bunch of helper functions in the details namespace for
// use by the actual bit container implementations found later in this
// inline source and in the standard .cc.

namespace stdx {
namespace details {

  //----------------------------------------------------------------------
  // BitWord and related constants
  //----------------------------------------------------------------------

  // We set the BitWord type in the header file. It is used for storing
  // bits. On a 32 bit machine this will probably be 32 bits while on a
  // 64 bit machine this will probably be 64 bits. All of the bit
  // containers use these typedefs and constants so it easy to change
  // how bits are stored.

  // Number of bits in a bit word
  static const int g_bit_word_sz = std::numeric_limits<BitWord>::digits;

  // Constant BitWords for 0 and 1
  static const BitWord g_bit_word_0 = static_cast<BitWord>(0);
  static const BitWord g_bit_word_1 = static_cast<BitWord>(1);

  //----------------------------------------------------------------------
  // ResetTopBits
  //----------------------------------------------------------------------
  // A separate struct which provides a static functions to reset the
  // top bits in the most significant word of an array of bit words. The
  // template parameter should be the number of bits in the most
  // significant word (ie the number of bits in the word which we pass
  // into the static function). We use this templated approach so that
  // we can specialize on the number of bits in the most significant
  // word and that way if there are no top bits then this function gets
  // completely optimized away. We have to use a templated struct
  // instead of a templated function because you can't specialize
  // templated functions. We are using specialization like a compile
  // time if statement.

  template < int MswNb >
  struct ResetTopBits {
    static void reset_top_bits( BitWord* word )
    {
      *word &= ~(~g_bit_word_0 << MswNb);
    }
  };

  template <>
  struct ResetTopBits<0> {
    static void reset_top_bits( BitWord* word )
    { }
  };

  //----------------------------------------------------------------------
  // word/bit indexing
  //----------------------------------------------------------------------

  inline int which_word( int idx )
  {
    return ( idx / g_bit_word_sz );
  }

  inline int which_bit( int idx )
  {
    return ( idx % g_bit_word_sz );
  }

  inline int mask_bit( int idx )
  {
    return ( g_bit_word_1 << (idx % g_bit_word_sz) );
  }

  //----------------------------------------------------------------------
  // bits/string conversion functions
  //----------------------------------------------------------------------
  // Note that these functions assume properly formatted bits
  // containers. So to convert bits to a string you need to make sure
  // that the high bits are zeroed out, and to convert a string to bits
  // you need to first reset the bits. We don't handle this here because
  // it's more efficient for the caller to do it.
  // Assumes that the high order bits are already reset. Also assumes
  // that the numer of bits is not more than the capacity of the bit
  // word container.

  void bits_to_str( const BitWord words[], int num_bits, std::string* str );
  void bits_from_str( BitWord words[], int num_bits,
                      const std::string& str );

  //----------------------------------------------------------------------
  // bits shifting functions
  //----------------------------------------------------------------------
  // Shift the bits stored in the given container of words. Note that
  // these functions don't actually care how many bits are valid in the
  // bit words - they just shift the words the given ammount. So for
  // left shifts you will need to reset the high bits again. Eventually
  // we might want to add templated versions of these so that we can
  // specialize when the amt is word aligned (we would need to use the
  // specialized struct trick like we did for ResetTopBits).

  void bits_left_shift( BitWord words[], int size, int amt );
  void bits_right_shift( BitWord words[], int size, int amt );

  //----------------------------------------------------------------------
  // get/set bits helper functions
  //----------------------------------------------------------------------
  // These functions are used to get or set bits from multiword bit
  // storage. Basically to get sz bits starting at pos we do:
  //
  //  bits_right_shifted_copy( words, size,
  //                           dest_words, dest_size, pos );
  //
  // And then of course we need to reset the high bits in the
  // destination storage. To set sz bits starting at pos we do:
  //
  //  bits_reset( words, pos, sz );
  //  bits_left_shifted_or( words, size, src_words, src_size, pos );
  //
  // Eventually we might want to add templated versions so that we can
  // specialize when the position is word aligned or when the
  // destination (source) bit words for shifted_assign (shifted_or) is
  // just one word long.

  void bits_right_shifted_copy( const BitWord words[], int size,
                                BitWord dest_words[],
                                int dest_size, int amt );

  void bits_reset( BitWord words[], int pos, int sz );

  void bits_left_shifted_or( BitWord words[], int size,
                             const BitWord src_words[],
                             int src_size, int amt );

  //----------------------------------------------------------------------
  // BitWordFuncs<Nw>
  //----------------------------------------------------------------------
  // Helper functions for manipulating an array of bit words. We place
  // all of these functions in a struct so we can specialize for the
  // single word case eliminating a great deal of overhead for small bit
  // arrays (which are very common). Some of these functions are
  // refactored above so that the same implementation can be used in the
  // dynamic bit container implementations.

  template < int Nw >
  struct BitWordFuncs {

    // Static word/bit index/mask functions

    static int which_word( int idx )
    {
      return details::which_word( idx );
    }

    static int which_bit( int idx )
    {
      return details::which_bit( idx );
    }

    static int mask_bit( int idx )
    {
      return details::mask_bit( idx );
    }

    // Operators : set/reset

    static void bits_set( BitWord words[] )
    {
      for ( int i = 0; i < Nw; i++ )
        words[i] = ~g_bit_word_0;
    }

    static void bits_reset( BitWord words[] )
    {
      for ( int i = 0; i < Nw; i++ )
        words[i] = g_bit_word_0;
    }

    static void bits_reset( BitWord words[], int pos, int sz )
    {
      details::bits_reset( words, pos, sz );
    }

    // Operators : and/or/xor/flip

    static void bits_and( BitWord words[], const BitWord rhs_words[] )
    {
      for ( int idx = 0; idx < Nw; idx++ )
        words[idx] &= rhs_words[idx];
    }

    static void bits_or( BitWord words[], const BitWord rhs_words[] )
    {
      for ( int idx = 0; idx < Nw; idx++ )
        words[idx] |= rhs_words[idx];
    }

    static void bits_xor( BitWord words[], const BitWord rhs_words[] )
    {
      for ( int idx = 0; idx < Nw; idx++ )
        words[idx] ^= rhs_words[idx];
    }

    static void bits_flip( BitWord words[] )
    {
      for ( int idx = 0; idx < Nw; idx++ )
        words[idx] = ~words[idx];
    }

    // Operators : left/right shift

    static void bits_left_shift( BitWord words[], int amt )
    {
      details::bits_left_shift( words, Nw, amt );
    }

    static void bits_right_shift( BitWord words[], int amt )
    {
      details::bits_right_shift( words, Nw, amt );
    }

    // Operators : equal

    static bool bits_equal( const BitWord words[],
                            const BitWord rhs_words[] )
    {
      for ( int idx = 0; idx < Nw; idx++ ) {
        if ( words[idx] != rhs_words[idx] )
          return false;
      }
      return true;
    }

    // Operators : assign

    static void bits_assign( BitWord words[], const BitWord rhs_words[],
                             int rhs_size )
    {
      int min_nw = (rhs_size < Nw) ? rhs_size : Nw;
      for ( int idx = 0; idx < min_nw; idx++ )
        words[idx] = rhs_words[idx];
    }

    // Operators : right_shifted_copy

    static void bits_right_shifted_copy( const BitWord words[],
                                         BitWord dest_words[],
                                         int dest_size, int amt )
    {
      details::bits_right_shifted_copy( words, Nw,
                                        dest_words, dest_size, amt );
    }

    // Operators : left_shifted_or

    static void bits_left_shifted_or( BitWord words[],
                                      const BitWord src_words[],
                                      int src_size, int amt )
    {
      details::bits_left_shifted_or( words, Nw,
                                     src_words, src_size, amt );
    }

  };

  //----------------------------------------------------------------------
  // BitWordFuncs<1>
  //----------------------------------------------------------------------
  // This specialization is the key to making small bit arrays blazingly
  // efficient. Essentially if all of the bits can fit in a single word,
  // then we optimize all of the multi-word operations into single word
  // bit operators. Although the compiler can optimize many of the
  // multi-word loops, the real key is optimizing the shifts so that
  // they are just simple bit shifts.

  template <>
  struct BitWordFuncs<1> {

    // Static word/bit index/mask functions

    static int which_word( int idx )
    {
      return 0;
    }

    static int which_bit( int idx )
    {
      return idx;
    }

    static int mask_bit( int idx )
    {
      return ( g_bit_word_1 << idx );
    }

    // Operators : set/reset

    static void bits_set( BitWord words[] )
    {
      words[0] = ~g_bit_word_0;
    }

    static void bits_reset( BitWord words[] )
    {
      words[0] = g_bit_word_0;
    }

    static void bits_reset( BitWord words[], int pos, int sz )
    {
      int mbits = g_bit_word_sz - pos - sz;
      words[0] &= ~((~g_bit_word_0 >> pos) << (pos + mbits) >> mbits);
    }

    // Operators : and/or/xor/flip

    static void bits_and( BitWord words[], const BitWord rhs_words[] )
    {
      words[0] &= rhs_words[0];
    }

    static void bits_or( BitWord words[], const BitWord rhs_words[] )
    {
      words[0] |= rhs_words[0];
    }

    static void bits_xor( BitWord words[], const BitWord rhs_words[] )
    {
      words[0] ^= rhs_words[0];
    }

    static void bits_flip( BitWord words[] )
    {
      words[0] = ~words[0];
    }

    // Operators : left/right shift

    static void bits_left_shift( BitWord words[], int amt )
    {
      words[0] <<= amt;
    }

    static void bits_right_shift( BitWord words[], int amt )
    {
      words[0] >>= amt;
    }

    // Operators : equal

    static bool bits_equal( const BitWord words[],
                            const BitWord rhs_words[] )
    {
      return (words[0] == rhs_words[0]);
    }

    // Operators : assign

    static void bits_assign( BitWord words[], const BitWord rhs_words[],
                             int rhs_size )
    {
      words[0] = rhs_words[0];
    }

    // Operators : right_shifted_copy

    static void bits_right_shifted_copy( const BitWord words[],
                                         BitWord dest_words[],
                                         int dest_size, int amt )
    {
      dest_words[0] = (words[0] >> amt);
    }

    // Operators : left_shifted_or

    static void bits_left_shifted_or( BitWord words[],
                                      const BitWord src_words[],
                                      int src_size, int amt )
    {
      words[0] |= (src_words[0] << amt);
    }

  };

  //----------------------------------------------------------------------
  // BitWordFuncs<2>
  //----------------------------------------------------------------------
  // This specialization is the key to making medium bit arrays
  // blazingly efficient. Essentially if all of the bits can fit in two
  // words, then we optimize all of the multi-word operations into two
  // word bit operators. Although the compiler can optimize many of the
  // multi-word loops, the real key is optimizing the shifts so that
  // they are just simple bit shifts.

  template <>
  struct BitWordFuncs<2> {

    // Static word/bit index/mask functions

    static int which_word( int idx )
    {
      return ( idx / g_bit_word_sz );
    }

    static int which_bit( int idx )
    {
      return ( idx % g_bit_word_sz );
    }

    static int mask_bit( int idx )
    {
      return ( g_bit_word_1 << (idx % g_bit_word_sz) );
    }

    // Operators : set/reset

    static void bits_set( BitWord words[] )
    {
      words[0] = ~g_bit_word_0;
      words[1] = ~g_bit_word_0;
    }

    static void bits_reset( BitWord words[] )
    {
      words[0] = g_bit_word_0;
      words[1] = g_bit_word_0;
    }

    static void bits_reset( BitWord words[], int pos, int sz )
    {
      int msb      = pos+sz-1;
      int lsb      = pos;
      int msb_word = msb / g_bit_word_sz;
      int lsb_word = lsb / g_bit_word_sz;

      // lbits = num of zeros on the least significant side of lsb word
      // mbits = num of zeros on the most significant side of msb word

      int lbits = lsb % g_bit_word_sz;
      int mbits = g_bit_word_sz - (msb % g_bit_word_sz) - 1;

      // Field stretches across both words

      if ( msb_word != lsb_word ) {
        words[0] &= ~((~g_bit_word_0 >> lbits) << lbits);
        words[1] &= ~((~g_bit_word_0 << mbits) >> mbits);
      }

      // Field is completely contained within one word

      else {
        words[msb_word]
          &= ~((~g_bit_word_0 >> lbits) << (lbits + mbits) >> mbits);
      }
    }

    // Operators : and/or/xor/flip

    static void bits_and( BitWord words[], const BitWord rhs_words[] )
    {
      words[0] &= rhs_words[0];
      words[1] &= rhs_words[1];
    }

    static void bits_or( BitWord words[], const BitWord rhs_words[] )
    {
      words[0] |= rhs_words[0];
      words[1] |= rhs_words[1];
    }

    static void bits_xor( BitWord words[], const BitWord rhs_words[] )
    {
      words[0] ^= rhs_words[0];
      words[1] ^= rhs_words[1];
    }

    static void bits_flip( BitWord words[] )
    {
      words[0] = ~words[0];
      words[1] = ~words[1];
    }

    // Operators : left/right shift

    static void bits_left_shift( BitWord words[], int amt )
    {
      if ( amt != 0 ) {
        if ( amt < g_bit_word_sz ) {
          words[1] = words[1] << amt;
          words[1] |= words[0] >> ( g_bit_word_sz - amt );
          words[0] = words[0] << amt;
        }
        else {
          words[1] = words[0] << ( amt - g_bit_word_sz );
          words[0] = g_bit_word_0;
        }
      }
    }

    static void bits_right_shift( BitWord words[], int amt )
    {
      if ( amt != 0 ) {
        if ( amt < g_bit_word_sz ) {
          words[0] = words[0] >> amt;
          words[0] |= words[1] << ( g_bit_word_sz - amt );
          words[1] = words[1] >> amt;
        }
        else {
          words[0] = words[1] >> ( amt - g_bit_word_sz );
          words[1] = g_bit_word_0;
        }
      }
    }

    // Operators : equal

    static bool bits_equal( const BitWord words[],
                            const BitWord rhs_words[] )
    {
      return ( (words[0] == rhs_words[0]) && (words[1] == rhs_words[1]) );
    }

    // Operators : assign

    static void bits_assign( BitWord words[], const BitWord rhs_words[],
                             int rhs_size )
    {
      words[0] = rhs_words[0];
      if ( rhs_size > 1 )
        words[1] = rhs_words[1];
    }

    // Operators : right_shifted_copy

    static void bits_right_shifted_copy( const BitWord words[],
                                         BitWord dest_words[],
                                         int dest_size, int amt )
    {
      if ( amt != 0 ) {
        if ( amt < g_bit_word_sz ) {
          dest_words[0] = words[0] >> amt;
          dest_words[0] |= words[1] << ( g_bit_word_sz - amt );
          if ( dest_size > 1 )
            dest_words[1] = words[1] >> amt;
        }
        else {
          dest_words[0] = words[1] >> ( amt - g_bit_word_sz );
          if ( dest_size > 1 )
            dest_words[1] = g_bit_word_0;
        }
      }
      else {
        dest_words[0] = words[0];
        if ( dest_size > 1 )
          dest_words[1] = words[1];
      }
    }

    // Operators : left_shifted_or

    static void bits_left_shifted_or( BitWord words[],
                                      const BitWord src_words[],
                                      int src_size, int amt )
    {
      if ( amt != 0 ) {
        if ( amt < g_bit_word_sz ) {
          if ( src_size > 1 )
            words[1] |= src_words[1] << amt;
          words[1] |= src_words[0] >> ( g_bit_word_sz - amt );
          words[0] |= src_words[0] << amt;
        }
        else
          words[1] |= src_words[0] << ( amt - g_bit_word_sz );
      }
      else {
        words[0] |= src_words[0];
        if ( src_size > 1 )
          words[1] |= src_words[1];
      }
    }

  };

  //----------------------------------------------------------------------
  // Throw Functions
  //----------------------------------------------------------------------
  // Putting the exception throws in separate functions helps gcc inline
  // code at the call site. This might be because my exception macros
  // create too much code.

  inline void bits_throw_invalid_bit_index( int idx, int num_bits )
  {
    STDX_THROW( stdx::BitContainerExceptions::EInvalidBitIndex,
                "Bit index (" << idx << ") must be positive "
                "and less than " << num_bits );
  }

  inline void bits_throw_invalid_bit_field( int pos, int sz,
                                            int num_bits )
  {
    STDX_THROW( stdx::BitContainerExceptions::EInvalidBitField,
                "Bit field (pos=" << pos << ",sz=" << sz << ") "
                "must be positive and less than " << num_bits );

  }

  inline void bits_throw_invalid_word_index( int idx, int num_bit_words )
  {
    STDX_THROW( stdx::BitContainerExceptions::EInvalidWordIndex,
                "Word index (" << idx << ") must be positive "
                "and less than " << num_bit_words );
  }

  inline void bits_throw_invalid_from_ulong( unsigned long val )
  {
    STDX_THROW( stdx::BitContainerExceptions::EInvalidUlongConversion,
                "High order bits non-zero (ulong = " << val << ")" );
  }

  inline void bits_throw_invalid_to_ulong( int num_bits )
  {
    STDX_THROW( stdx::BitContainerExceptions::EInvalidUlongConversion,
                "Bit container too long (" << num_bits << ") "
                "to convert to ulong" );
  }

  inline void bits_throw_invalid_container( int lhs_size, int rhs_size )
  {
    STDX_THROW( stdx::BitContainerExceptions::EInvalidBitContainerConversion,
                "Cannot convert given bit container with " << rhs_size
                  << " bits to container with " << lhs_size << " bits." );
  }

  inline void bits_throw_invalid_operand_size( int lhs_size,
                                               int rhs_size )
  {
    STDX_THROW( stdx::BitContainerExceptions::EInvalidOperandSize,
                "Right hand operand has " << rhs_size << " bits "
                "but left hand operand has " << lhs_size << " bits" );
  }

  inline void bits_throw_invalid_trunc( int Nb, int num_bits )
  {
    STDX_THROW( stdx::BitContainerExceptions::EInvalidTruncation,
                "Cannot truncate " << Nb << " bits to "
                  << num_bits << " bits" );
  }

  inline void bits_throw_invalid_ext( int Nb, int num_bits )
  {
    STDX_THROW( stdx::BitContainerExceptions::EInvalidExtension,
                "Cannot extend " << Nb << " bits to "
                  << num_bits << " bits" );
  }

}}

//========================================================================
// BitArray
//========================================================================

namespace stdx {

  //----------------------------------------------------------------------
  // BitArray : Constructors
  //----------------------------------------------------------------------

  template < int Nb >
  inline BitArray<Nb>::BitArray()
  {
    typedef details::BitWordFuncs<Nw> BWF;
    BWF::bits_reset( m_words );
  }

  template < int Nb >
  inline BitArray<Nb>::BitArray( unsigned long val )
  {
    from_ulong(val);
  }

  template < int Nb >
  inline BitArray<Nb>::BitArray( const std::string& str )
  {
    from_str(str);
  }

  //----------------------------------------------------------------------
  // BitArray : Size member functions
  //----------------------------------------------------------------------

  template < int Nb >
  inline int BitArray<Nb>::size() const
  {
    return Nb;
  }

  //----------------------------------------------------------------------
  // BitArray : Reset member functions
  //----------------------------------------------------------------------

  template < int Nb >
  inline void BitArray<Nb>::reset()
  {
    typedef details::BitWordFuncs<Nw> BWF;
    BWF::bits_reset( m_words );
  }

  template < int Nb >
  inline void BitArray<Nb>::reset( int idx )
  {
    if ( (idx < 0) || (idx >= Nb) )
      details::bits_throw_invalid_bit_index(idx,Nb);
    unchecked_reset(idx);
  }

  template < int Nb >
  inline void BitArray<Nb>::unchecked_reset( int idx )
  {
    typedef details::BitWordFuncs<Nw> BWF;
    m_words[BWF::which_word(idx)] &= ~BWF::mask_bit(idx);
  }

  //----------------------------------------------------------------------
  // BitArray : Set member functions
  //----------------------------------------------------------------------

  template < int Nb >
  inline void BitArray<Nb>::set()
  {
    typedef details::BitWordFuncs< Nw > BWF;
    typedef details::ResetTopBits< Nb % details::g_bit_word_sz > RTP;
    BWF::bits_set( m_words );
    RTP::reset_top_bits( &m_words[Nw-1] );
  }

  template < int Nb >
  inline void BitArray<Nb>::set( int idx )
  {
    if ( (idx < 0) || (idx >= Nb) )
      details::bits_throw_invalid_bit_index(idx,Nb);
    unchecked_set(idx);
  }

  template < int Nb >
  inline void BitArray<Nb>::set( int idx, Bit bit )
  {
    if ( (idx < 0) || (idx >= Nb) )
      details::bits_throw_invalid_bit_index(idx,Nb);
    ( bit == 1 ) ? unchecked_set(idx) : unchecked_reset(idx);
  }

  template < int Nb >
  inline void BitArray<Nb>::unchecked_set( int idx )
  {
    typedef details::BitWordFuncs<Nw> BWF;
    m_words[BWF::which_word(idx)] |= BWF::mask_bit(idx);
  }

  //----------------------------------------------------------------------
  // BitArray : Get member functions
  //----------------------------------------------------------------------

  template < int Nb >
  inline Bit BitArray<Nb>::get( int idx ) const
  {
    if ( (idx < 0) || (idx >= Nb) )
      details::bits_throw_invalid_bit_index(idx,Nb);
    return unchecked_get(idx);
  }

  template < int Nb >
  inline Bit BitArray<Nb>::unchecked_get( int idx ) const
  {
    typedef details::BitWordFuncs<Nw> BWF;
    details::BitWord word
      = m_words[BWF::which_word(idx)] >> BWF::which_bit(idx);
    return static_cast<Bit>(word & details::g_bit_word_1);
  }

  //----------------------------------------------------------------------
  // BitArray : get bits member functions
  //----------------------------------------------------------------------
  // Maybe later we can provide a templated version of
  // bits_right_shifted_copy, bits_reset_bits, and bits_left_shifted_or
  // so that we can use specializations when the msb and lsb are in the
  // same word and/or when the position is word aligned. For example,
  // the functions could take two template arguments: (t_pos %
  // bit_word_sz) and also (t_pos/bit_word_sz) -
  // ((t_pos+t_sz-1)/bit_word_sz). We can then specialize on them like
  // this:
  //
  //  - bits_func<0,1>() : aligned field, msb,lsb in same word
  //  - bits_func<0,N>() : aligned field, more than 1 word
  //  - bits_func<N,1>() : unaligned field, msb,lsb in same word
  //  - bits_func<N,M>() : unaligned field, more than 1 word

  template < int Nb >
  template < int t_pos, int t_sz >
  inline BitArray<t_sz> BitArray<Nb>::get_bits() const
  {
    typedef details::BitWordFuncs<Nw> BWF;

    STDX_STATIC_ASSERT( t_pos >= 0 );
    STDX_STATIC_ASSERT( t_sz > 0 );
    STDX_STATIC_ASSERT( Nb > t_pos );
    STDX_STATIC_ASSERT( Nb > (t_pos+t_sz-1) );

    BitArray<t_sz> bits;
    BWF::bits_right_shifted_copy( m_words, bits.m_words,
                                  BitArray<t_sz>::Nw, t_pos );

    details::BitWord bits_msw_idx = BitArray<t_sz>::Nw-1;
    typedef details::ResetTopBits< t_sz % details::g_bit_word_sz > RTPd;
    RTPd::reset_top_bits( &bits.m_words[bits_msw_idx] );
    return bits;
  }

  template < int Nb >
  template < int t_sz >
  inline BitArray<t_sz> BitArray<Nb>::get_bits( int pos ) const
  {
    typedef details::BitWordFuncs<Nw> BWF;

    STDX_STATIC_ASSERT( t_sz > 0 );
    if ( (pos < 0) || ((pos + t_sz - 1) >= Nb) )
      details::bits_throw_invalid_bit_field(pos,t_sz,Nb);

    BitArray<t_sz> bits;
    BWF::bits_right_shifted_copy( m_words, bits.m_words,
                                  BitArray<t_sz>::Nw, pos );

    details::BitWord bits_msw_idx = BitArray<t_sz>::Nw-1;
    typedef details::ResetTopBits< t_sz % details::g_bit_word_sz > RTPd;
    RTPd::reset_top_bits( &bits.m_words[bits_msw_idx] );
    return bits;
  }

  //----------------------------------------------------------------------
  // BitArray : set bits member functions
  //----------------------------------------------------------------------

  template < int Nb >
  template < int t_pos, int t_sz >
  inline BitArray<Nb>&
  BitArray<Nb>::set_bits( const BitArray<t_sz>& bits )
  {
    typedef details::BitWordFuncs<Nw> BWF;

    STDX_STATIC_ASSERT( t_pos >= 0 );
    STDX_STATIC_ASSERT( t_sz > 0 );
    STDX_STATIC_ASSERT( Nb > t_pos );
    STDX_STATIC_ASSERT( Nb > (t_pos+t_sz-1) );

    BWF::bits_reset( m_words, t_pos, t_sz );
    BWF::bits_left_shifted_or( m_words, bits.m_words,
                               BitArray<t_sz>::Nw, t_pos );
    return *this;
  }

  template < int Nb >
  template < int t_sz >
  inline BitArray<Nb>&
  BitArray<Nb>::set_bits( int pos, const BitArray<t_sz>& bits )
  {
    typedef details::BitWordFuncs<Nw> BWF;

    STDX_STATIC_ASSERT( t_sz > 0 );
    if ( (pos < 0) || ((pos + t_sz - 1) >= Nb) )
      details::bits_throw_invalid_bit_field(pos,t_sz,Nb);

    BWF::bits_reset( m_words, pos, t_sz );
    BWF::bits_left_shifted_or( m_words, bits.m_words,
                               BitArray<t_sz>::Nw, pos );
    return *this;
  }

  //----------------------------------------------------------------------
  // BitArray : get field member functions
  //----------------------------------------------------------------------

  template < int Nb >
  template < int t_msb, int t_lsb >
  BitArray<t_msb-t_lsb+1> BitArray<Nb>::get_field() const
  {
    return get_bits<t_lsb,t_msb-t_lsb+1>();
  }

  template < int Nb >
  template < typename Field >
  BitArray<Field::sz> BitArray<Nb>::get_field() const
  {
    return get_field<Field::msb,Field::lsb>();
  }

  //----------------------------------------------------------------------
  // BitArray : set field member functions
  //----------------------------------------------------------------------

  template < int Nb >
  template < int t_msb, int t_lsb >
  BitArray<Nb>& BitArray<Nb>::set_field(
    const BitArray<t_msb-t_lsb+1>& bits )
  {
    return set_bits<t_lsb,t_msb-t_lsb+1>(bits);
  }

  template < int Nb >
  template < typename Field >
  BitArray<Nb>& BitArray<Nb>::set_field(
    const BitArray<Field::sz>& bits )
  {
    return set_field<Field::msb,Field::lsb>(bits);
  }

  //----------------------------------------------------------------------
  // BitArray : Ulong Conversions
  //----------------------------------------------------------------------

  template < int Nb >
  inline void BitArray<Nb>::from_ulong( unsigned long val )
  {
    typedef details::BitWordFuncs<Nw> BWF;
    BWF::bits_reset( m_words );

    // Make sure there are not too many bits in the ulong
    int ulong_num_bits = std::numeric_limits<unsigned long>::digits;
    if ( Nb < ulong_num_bits ) {
      int extra_bits = ulong_num_bits - Nb;
      if ( (val & (~(0ul) << extra_bits)) != 0ul )
        details::bits_throw_invalid_from_ulong(val);
    }

    m_words[0] = val;
  }

  template < int Nb >
  inline unsigned long BitArray<Nb>::to_ulong() const
  {
    // Make sure there are not too many bits for a ulong
    int ulong_num_bits = std::numeric_limits<unsigned long>::digits;
    if ( Nb > ulong_num_bits )
      details::bits_throw_invalid_to_ulong(Nb);

    return m_words[0];
  }

  //----------------------------------------------------------------------
  // BitArray : String Conversions
  //----------------------------------------------------------------------

  template < int Nb >
  inline void BitArray<Nb>::from_str( const std::string& str )
  {
    typedef details::BitWordFuncs<Nw> BWF;
    BWF::bits_reset( m_words );
    details::bits_from_str( m_words, Nb, str );
  }

  template < int Nb >
  inline std::string BitArray<Nb>::to_str() const
  {
    std::string str;
    details::bits_to_str( m_words, Nb, &str );
    return str;
  }

  //----------------------------------------------------------------------
  // BitArray : Bit extension and truncation
  //----------------------------------------------------------------------

  template < int Nb >
  template < int DestNb >
  inline BitArray<DestNb> BitArray<Nb>::to_zext() const
  {
    STDX_STATIC_ASSERT( DestNb >= Nb );
    BitArray<DestNb> bits;
    typedef details::BitWordFuncs< BitArray<DestNb>::Nw > BWFd;
    BWFd::bits_assign( bits.m_words, m_words, Nw );
    return bits;
  }

  template < int Nb >
  template < int DestNb >
  inline BitArray<DestNb> BitArray<Nb>::to_sext() const
  {
    typedef details::BitWordFuncs<Nw> BWF;
    STDX_STATIC_ASSERT( DestNb >= Nb );
    BitArray<DestNb> bits;
    typedef details::BitWordFuncs< BitArray<DestNb>::Nw > BWFd;

    Bit sign_bit = this->unchecked_get(Nb-1);
    if ( sign_bit == 1 ) {
      bits.set();
      BWFd::bits_assign( bits.m_words, m_words, Nw );
      bits.m_words[BWFd::which_word(Nb)]
        |= (~details::g_bit_word_0 << BWF::which_bit(Nb));

      int bits_msw_idx = BitArray<DestNb>::Nw-1;
      typedef details::ResetTopBits< DestNb % details::g_bit_word_sz > RTBd;
      RTBd::reset_top_bits( &bits.m_words[bits_msw_idx] );
    }
    else
      BWFd::bits_assign( bits.m_words, m_words, Nw );

    return bits;
  }

  template < int Nb >
  template < int DestNb >
  inline BitArray<DestNb> BitArray<Nb>::to_trunc() const
  {
    STDX_STATIC_ASSERT( DestNb <= Nb );
    BitArray<DestNb> bits;
    typedef details::BitWordFuncs< BitArray<DestNb>::Nw > BWFd;
    BWFd::bits_assign( bits.m_words, m_words, Nw );

    int bits_msw_idx = BitArray<DestNb>::Nw-1;
    typedef details::ResetTopBits< DestNb % details::g_bit_word_sz > RTBd;
    RTBd::reset_top_bits( &bits.m_words[bits_msw_idx] );

    return bits;
  }

  //----------------------------------------------------------------------
  // BitArray : Operators
  //----------------------------------------------------------------------

  template < int Nb >
  inline BitArray<Nb>& BitArray<Nb>::operator&=( const BitArray<Nb>& rhs )
  {
    typedef details::BitWordFuncs<Nw> BWF;
    BWF::bits_and( m_words, rhs.m_words );
    return *this;
  }

  template < int Nb >
  inline BitArray<Nb>& BitArray<Nb>::operator|=( const BitArray<Nb>& rhs )
  {
    typedef details::BitWordFuncs<Nw> BWF;
    BWF::bits_or( m_words, rhs.m_words );
    return *this;
  }

  template < int Nb >
  inline BitArray<Nb>& BitArray<Nb>::operator^=( const BitArray<Nb>& rhs )
  {
    typedef details::BitWordFuncs<Nw> BWF;
    BWF::bits_xor( m_words, rhs.m_words );
    return *this;
  }

  template < int Nb >
  inline BitArray<Nb>& BitArray<Nb>::operator<<=( int amt )
  {
    typedef details::BitWordFuncs< Nw > BWF;
    typedef details::ResetTopBits< Nb % details::g_bit_word_sz > RTP;

    if ( amt < Nb ) {
      BWF::bits_left_shift( m_words, amt );
      RTP::reset_top_bits( &m_words[Nw-1] );
    }
    else
      BWF::bits_reset( m_words );

    return *this;
  }

  template < int Nb >
  inline BitArray<Nb>& BitArray<Nb>::operator>>=( int amt )
  {
    typedef details::BitWordFuncs<Nw> BWF;

    if ( amt < Nb )
      BWF::bits_right_shift( m_words, amt );
    else
      BWF::bits_reset( m_words );

    return *this;
  }

  template < int Nb >
  inline BitArray<Nb> BitArray<Nb>::operator~() const
  {
    typedef details::BitWordFuncs< Nw > BWF;
    typedef details::ResetTopBits< Nb % details::g_bit_word_sz > RTP;

    BitArray<Nb> bits(*this);
    BWF::bits_flip( bits.m_words );
    RTP::reset_top_bits( &bits.m_words[Nw-1] );
    return bits;
  }

  template < int Nb >
  inline BitArray<Nb> BitArray<Nb>::operator&( const BitArray<Nb>& rhs ) const
  {
    BitArray<Nb> bits(*this);
    bits &= rhs;
    return bits;
  }

  template < int Nb >
  inline BitArray<Nb> BitArray<Nb>::operator|( const BitArray<Nb>& rhs ) const
  {
    BitArray<Nb> bits(*this);
    bits |= rhs;
    return bits;
  }

  template < int Nb >
  inline BitArray<Nb> BitArray<Nb>::operator^( const BitArray<Nb>& rhs ) const
  {
    BitArray<Nb> bits(*this);
    bits ^= rhs;
    return bits;
  }

  template < int Nb >
  inline BitArray<Nb> BitArray<Nb>::operator<<( int amt ) const
  {
    BitArray<Nb> bits(*this);
    bits <<= amt;
    return bits;
  }

  template < int Nb >
  inline BitArray<Nb> BitArray<Nb>::operator>>( int amt ) const
  {
    BitArray<Nb> bits(*this);
    bits >>= amt;
    return bits;
  }

  template < int Nb >
  inline bool BitArray<Nb>::operator==( const BitArray<Nb>& rhs ) const
  {
    typedef details::BitWordFuncs<Nw> BWF;
    return BWF::bits_equal( m_words, rhs.m_words );
  }

  template < int Nb >
  inline bool BitArray<Nb>::operator!=( const BitArray<Nb>& rhs ) const
  {
    typedef details::BitWordFuncs<Nw> BWF;
    return !BWF::bits_equal( m_words, rhs.m_words );
  }

  //----------------------------------------------------------------------
  // BitArray : Insertion operator
  //----------------------------------------------------------------------

  template < int Nb >
  inline std::ostream& operator<<( std::ostream& os,
                                   const BitArray<Nb>& bits )
  {
    os << bits.to_str();
    return os;
  }

}

