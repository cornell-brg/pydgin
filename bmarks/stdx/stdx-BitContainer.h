//========================================================================
// stdx-BitContainer : Static and dynamic containers for bits
//========================================================================

#ifndef STDX_BIT_CONTAINER_H
#define STDX_BIT_CONTAINER_H

#include "stdx-Exception.h"
#include <limits>
#include <string>
#include <vector>

namespace stdx {

  //======================================================================
  // Basic bit types
  //======================================================================

  typedef bool Bit;

  // The BitWord type is part of the implementation - users should never
  // reference this type directly so we place it in the details
  // namespace. We have to place it here so that we can use an array of
  // BitWords as the bit storage in our BitArray class;

  namespace details {
    typedef unsigned long int BitWord;
  }

  //======================================================================
  // Exceptions
  //======================================================================

  namespace BitContainerExceptions
  {
    struct EInvalidBitIndex               : public stdx::Exception { };
    struct EInvalidWordIndex              : public stdx::Exception { };
    struct EInvalidUlongConversion        : public stdx::Exception { };
    struct EInvalidStringConversion       : public stdx::Exception { };
    struct EInvalidBitContainerConversion : public stdx::Exception { };
    struct EInvalidOperandSize            : public stdx::Exception { };
    struct EInvalidBitField               : public stdx::Exception { };
    struct EInvalidTruncation             : public stdx::Exception { };
    struct EInvalidExtension              : public stdx::Exception { };
  }

  //======================================================================
  // StaticBitField
  //======================================================================
  // A class which represents a bitfield specified at compile time. If
  // you know the field statically, using this class to name and access
  // your fields (as opposed to BitDynamicField) can result
  // significantly better code.

  template < int t_msb, int t_lsb >
  struct StaticBitField {

    // Accessors to the msb and lsb
    const static int msb = t_msb;
    const static int lsb = t_lsb;

    // A type for the length of the bit field
    const static int sz = (t_msb - t_lsb + 1);

  };

  //======================================================================
  // BitArray
  //======================================================================

  template < int Nb >
  class BitArray {

   public:

    //--------------------------------------------------------------------
    // Constructors
    //--------------------------------------------------------------------

    BitArray();
    BitArray( unsigned long val );
    BitArray( const std::string& str );

    //--------------------------------------------------------------------
    // Size member functions
    //--------------------------------------------------------------------

    int size() const;

    //--------------------------------------------------------------------
    // Reset/get/set bit member functions
    //--------------------------------------------------------------------

    void reset();
    void reset( int idx );
    void unchecked_reset( int idx );

    void set();
    void set( int idx );
    void set( int idx, Bit bit );
    void unchecked_set( int idx );

    Bit  get( int idx ) const;
    Bit  unchecked_get( int idx ) const;

    //--------------------------------------------------------------------
    // get/set bits member functions
    //--------------------------------------------------------------------

    template < int t_pos, int t_sz >
    BitArray<t_sz> get_bits() const;

    template < int t_sz >
    BitArray<t_sz> get_bits( int pos ) const;

    template < int t_pos, int t_sz >
    BitArray<Nb>& set_bits( const BitArray<t_sz>& bits );

    template < int t_sz >
    BitArray<Nb>& set_bits( int pos, const BitArray<t_sz>& bits );

    //--------------------------------------------------------------------
    // get/set field member functions
    //--------------------------------------------------------------------

    template < int t_msb, int t_lsb >
    BitArray<t_msb-t_lsb+1> get_field() const;

    template < typename Field >
    BitArray<Field::sz> get_field() const;

    template < int t_msb, int t_lsb >
    BitArray<Nb>& set_field( const BitArray<t_msb-t_lsb+1>& bits );

    template < typename Field >
    BitArray<Nb>& set_field( const BitArray<Field::sz>& bits );

    //--------------------------------------------------------------------
    // Conversions
    //--------------------------------------------------------------------

    void from_ulong( unsigned long val );
    void from_str( const std::string& str );

    unsigned long to_ulong() const;
    std::string   to_str()   const;

    //--------------------------------------------------------------------
    // Bit extension and truncation
    //--------------------------------------------------------------------

    template < int DestNb > BitArray<DestNb> to_zext()  const;
    template < int DestNb > BitArray<DestNb> to_sext()  const;
    template < int DestNb > BitArray<DestNb> to_trunc() const;

    //--------------------------------------------------------------------
    // Operators
    //--------------------------------------------------------------------

    BitArray<Nb>& operator&=( const BitArray<Nb>& rhs );
    BitArray<Nb>& operator|=( const BitArray<Nb>& rhs );
    BitArray<Nb>& operator^=( const BitArray<Nb>& rhs );
    BitArray<Nb>& operator<<=( int amt );
    BitArray<Nb>& operator>>=( int amt );

    BitArray<Nb>  operator~() const;
    BitArray<Nb>  operator&( const BitArray<Nb>& rhs ) const;
    BitArray<Nb>  operator|( const BitArray<Nb>& rhs ) const;
    BitArray<Nb>  operator^( const BitArray<Nb>& rhs ) const;
    BitArray<Nb>  operator<<( int amt ) const;
    BitArray<Nb>  operator>>( int amt ) const;

    bool          operator==( const BitArray<Nb>& rhs ) const;
    bool          operator!=( const BitArray<Nb>& rhs ) const;

   private:

    //--------------------------------------------------------------------
    // Friends
    //--------------------------------------------------------------------
    // All BitArrays are friends regardless of the number of bits.

    template < int Nb_ > friend class BitArray;

    //--------------------------------------------------------------------
    // Private data
    //--------------------------------------------------------------------

    static const int Nw
      = (   (Nb + std::numeric_limits<details::BitWord>::digits - 1)
          / std::numeric_limits<details::BitWord>::digits );

    details::BitWord m_words[Nw];

  };

  //----------------------------------------------------------------------
  // Other operators
  //----------------------------------------------------------------------

  template < int Nb >
  std::ostream& operator<<( std::ostream& os, const BitArray<Nb>& bits );

}

#include "stdx-BitContainer.inl"
#endif /* STDX_BIT_CONTAINER_H */

