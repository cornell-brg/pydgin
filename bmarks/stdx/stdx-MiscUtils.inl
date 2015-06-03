//========================================================================
// stdx-MiscUtils.inl
//========================================================================
// We make the bit fields inline because often the msb and lsb are
// compile time constants so it is very likely that the compiler can
// optimize much of this away.

#include "stdx-Exception.h"

namespace stdx {

  //----------------------------------------------------------------------
  // nl
  //----------------------------------------------------------------------

  template <typename Ch, typename Tr>
  std::basic_ostream<Ch,Tr>& nl( std::basic_ostream<Ch,Tr>& os )
  {
    return os.put(os.widen('\n'));
  }

  //----------------------------------------------------------------------
  // verify_bit_field
  //----------------------------------------------------------------------

  inline void verify_bit_field( int msb, int lsb )
  {
    STDX_ASSERT( (msb < 32) && (msb >= 0) );
    STDX_ASSERT( (lsb < 32) && (lsb >= 0) );
    STDX_ASSERT( msb >= lsb );
  }

  //----------------------------------------------------------------------
  // extract_bit_field_fast
  //----------------------------------------------------------------------

  inline uint32_t extract_bit_field_fast( uint32_t bits,
                                          int msb, int lsb )
  {
    return (bits & ~(~1u << msb)) >> lsb;
  }

  //----------------------------------------------------------------------
  // extract_bit_field
  //----------------------------------------------------------------------

  inline uint32_t extract_bit_field( uint32_t bits, int msb, int lsb )
  {
    verify_bit_field( msb, lsb );
    return extract_bit_field_fast( bits, msb, lsb );
  }

}

