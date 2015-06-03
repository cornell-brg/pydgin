//========================================================================
// stdx-BitContainer Unit Tests
//========================================================================

#include "stdx-BitContainer.h"
#include "utst.h"
#include <inttypes.h>

//========================================================================
// BitArray
//========================================================================

//------------------------------------------------------------------------
// Simple Examples
//------------------------------------------------------------------------
// These are two simple examples which we use just to make sure that our
// bit containers result in the same performance as doing the bit
// manipulation manually.

uint64_t foobar_uint_48( uint64_t bits )
{
  uint32_t bitsA = (bits & 0x0000000f);
  uint64_t bitsB = (bits & 0xffff0000) >> 16;
  uint64_t bitsC = (bitsB << 32) | (bitsB << 4) | bitsA;
  return bitsC;
}

stdx::BitArray<48> foobar_barray_48( stdx::BitArray<64> bits )
{
  stdx::BitArray<4>  bitsA = bits.get_bits<  0,  4 >();
  stdx::BitArray<16> bitsB = bits.get_bits< 16, 16 >();
  stdx::BitArray<48> bitsC;

  bitsC.set_bits<  0,  4 >( bitsA );
  bitsC.set_bits<  4, 16 >( bitsB );
  bitsC.set_bits< 32, 16 >( bitsB );

  return bitsC;
}

uint32_t foobar_uint_24( uint32_t bits )
{
  uint32_t bitsA = (bits & 0x0000000f);
  uint32_t bitsB = (bits & 0xffff0000) >> 16;
  uint32_t bitsC = (bitsA << 20) | (bitsB << 4) | bitsA;
  return bitsC;
}

stdx::BitArray<24> foobar_barray_24( stdx::BitArray<32> bits )
{
  typedef stdx::StaticBitField<  3,  0 > a;
  typedef stdx::StaticBitField< 31, 16 > b;

  stdx::BitArray<a::sz> bitsA = bits.get_field<a>();
  stdx::BitArray<b::sz> bitsB = bits.get_field<b>();
  stdx::BitArray<24> bitsC;

  typedef stdx::StaticBitField<  3,  0 > x;
  typedef stdx::StaticBitField< 19,  4 > y;
  typedef stdx::StaticBitField< 23, 20 > z;

  bitsC.set_field<x>( bitsA );
  bitsC.set_field<y>( bitsB );
  bitsC.set_field<z>( bitsA );

  return bitsC;
}

//------------------------------------------------------------------------
// TestBitArray4bBasic
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestBitArray4bBasic )
{
  stdx::BitArray<4> bits(0x3);
  UTST_CHECK_EQ( bits.to_ulong(), 0x3u );
  UTST_CHECK_EQ( bits.size(),     4    );
  UTST_CHECK_EQ( bits.get(0),     1    );
  UTST_CHECK_EQ( bits.get(1),     1    );
  UTST_CHECK_EQ( bits.get(2),     0    );
  UTST_CHECK_EQ( bits.get(3),     0    );

  bits.set(0);   UTST_CHECK_EQ( bits.to_ulong(), 0x3u );
  bits.reset(0); UTST_CHECK_EQ( bits.to_ulong(), 0x2u );
  bits.set(0,1); UTST_CHECK_EQ( bits.to_ulong(), 0x3u );
  bits.set(0,0); UTST_CHECK_EQ( bits.to_ulong(), 0x2u );
  bits.reset();  UTST_CHECK_EQ( bits.to_ulong(), 0x0u );
  bits.set();    UTST_CHECK_EQ( bits.to_ulong(), 0xfu );

  bits = 0x3;
  stdx::BitArray<4> bitsA = bits;
  stdx::BitArray<4> bitsB(0x3);
  stdx::BitArray<4> bitsC(0x1);

  UTST_CHECK_EQ  ( bits, bitsA );
  UTST_CHECK_EQ  ( bits, bitsB );
  UTST_CHECK_NEQ ( bits, bitsC );
}

//------------------------------------------------------------------------
// TestBitArray4bOperators
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestBitArray4bOperators )
{
  stdx::BitArray<4> bitsA("0b1010");
  stdx::BitArray<4> bitsB("0b0110");
  stdx::BitArray<4> bits;

  // Unary operators

  UTST_CHECK_EQ( ~bitsA, stdx::BitArray<4>("0b0101") );

  // Inplace operators

  bits = bitsA;
  UTST_CHECK_EQ( bits &= bitsB, stdx::BitArray<4>("0b0010") );

  bits = bitsA;
  UTST_CHECK_EQ( bits |= bitsB, stdx::BitArray<4>("0b1110") );

  bits = bitsA;
  UTST_CHECK_EQ( bits ^= bitsB, stdx::BitArray<4>("0b1100") );

  bits = bitsA;
  UTST_CHECK_EQ( bits <<= 2,    stdx::BitArray<4>("0b1000") );

  bits = bitsA;
  UTST_CHECK_EQ( bits >>= 2,    stdx::BitArray<4>("0b0010") );

  // Binary operators

  UTST_CHECK_EQ( bitsA & bitsB, stdx::BitArray<4>("0b0010") );
  UTST_CHECK_EQ( bitsA | bitsB, stdx::BitArray<4>("0b1110") );
  UTST_CHECK_EQ( bitsA ^ bitsB, stdx::BitArray<4>("0b1100") );
  UTST_CHECK_EQ( bitsA << 2,    stdx::BitArray<4>("0b1000") );
  UTST_CHECK_EQ( bitsA >> 2,    stdx::BitArray<4>("0b0010") );
}

//------------------------------------------------------------------------
// TestBitArray4bExtTrunc
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestBitArray4bExtTrunc )
{
  using namespace stdx;
  BitArray<4> bitsA("0b1010");
  BitArray<4> bitsB("0b0110");

  UTST_CHECK_EQ( bitsA.to_zext<8>(),  BitArray<8>("0x0a")          );
  UTST_CHECK_EQ( bitsA.to_zext<32>(), BitArray<32>("0x0000000a")   );
  UTST_CHECK_EQ( bitsA.to_zext<37>(), BitArray<37>("0x000000000a") );

  UTST_CHECK_EQ( bitsB.to_zext<8>(),  BitArray<8>("0x06")          );
  UTST_CHECK_EQ( bitsB.to_zext<32>(), BitArray<32>("0x00000006")   );
  UTST_CHECK_EQ( bitsB.to_zext<37>(), BitArray<37>("0x0000000006") );

  UTST_CHECK_EQ( bitsA.to_sext<8>(),  BitArray<8>("0xfa")          );
  UTST_CHECK_EQ( bitsA.to_sext<32>(), BitArray<32>("0xfffffffa")   );
  UTST_CHECK_EQ( bitsA.to_sext<37>(), BitArray<37>("0x1ffffffffa") );

  UTST_CHECK_EQ( bitsB.to_sext<8>(),  BitArray<8>("0x06")          );
  UTST_CHECK_EQ( bitsB.to_sext<32>(), BitArray<32>("0x00000006")   );
  UTST_CHECK_EQ( bitsB.to_sext<37>(), BitArray<37>("0x0000000006") );

  UTST_CHECK_EQ( bitsA.to_trunc<2>(), BitArray<2>("0b10")          );
  UTST_CHECK_EQ( bitsB.to_trunc<2>(), BitArray<2>("0b10")          );
}

//------------------------------------------------------------------------
// TestBitArray4bGetSetBits
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestBitArray4bGetSetBits )
{
  using namespace stdx;
  stdx::BitArray<4> bits("0b1010");

  typedef BitArray<1> B1;
  typedef BitArray<2> B2;
  typedef BitArray<3> B3;
  typedef BitArray<4> B4;

  // get_bits (static length)

  UTST_CHECK_EQ( (bits.get_bits<0,1>()), B1("0b0")    );
  UTST_CHECK_EQ( (bits.get_bits<1,1>()), B1("0b1")    );
  UTST_CHECK_EQ( (bits.get_bits<2,1>()), B1("0b0")    );
  UTST_CHECK_EQ( (bits.get_bits<3,1>()), B1("0b1")    );

  UTST_CHECK_EQ( (bits.get_bits<0,2>()), B2("0b10")   );
  UTST_CHECK_EQ( (bits.get_bits<1,2>()), B2("0b01")   );
  UTST_CHECK_EQ( (bits.get_bits<2,2>()), B2("0b10")   );

  UTST_CHECK_EQ( (bits.get_bits<0,3>()), B3("0b010")  );
  UTST_CHECK_EQ( (bits.get_bits<1,3>()), B3("0b101")  );

  UTST_CHECK_EQ( (bits.get_bits<0,4>()), B4("0b1010") );

  // get_bits (dynamic length)

  UTST_CHECK_EQ( (bits.get_bits<1>(0)),  B1("0b0")    );
  UTST_CHECK_EQ( (bits.get_bits<1>(1)),  B1("0b1")    );
  UTST_CHECK_EQ( (bits.get_bits<1>(2)),  B1("0b0")    );
  UTST_CHECK_EQ( (bits.get_bits<1>(3)),  B1("0b1")    );

  UTST_CHECK_EQ( (bits.get_bits<2>(0)),  B2("0b10")   );
  UTST_CHECK_EQ( (bits.get_bits<2>(1)),  B2("0b01")   );
  UTST_CHECK_EQ( (bits.get_bits<2>(2)),  B2("0b10")   );

  UTST_CHECK_EQ( (bits.get_bits<3>(0)),  B3("0b010")  );
  UTST_CHECK_EQ( (bits.get_bits<3>(1)),  B3("0b101")  );

  UTST_CHECK_EQ( (bits.get_bits<4>(0)),  B4("0b1010") );

  // set_bits (specify static length explicitly)

  UTST_CHECK_EQ( (bits.set_bits<0,1>(B1("0b1"))), B4("0b1011") );
  UTST_CHECK_EQ( (bits.set_bits<1,1>(B1("0b0"))), B4("0b1001") );
  UTST_CHECK_EQ( (bits.set_bits<2,1>(B1("0b1"))), B4("0b1101") );
  UTST_CHECK_EQ( (bits.set_bits<3,1>(B1("0b0"))), B4("0b0101") );

  // set_bits (infer static length from argument)

  UTST_CHECK_EQ( (bits.set_bits<0>(B1("0b0"))),   B4("0b0100") );
  UTST_CHECK_EQ( (bits.set_bits<1>(B1("0b1"))),   B4("0b0110") );
  UTST_CHECK_EQ( (bits.set_bits<2>(B1("0b0"))),   B4("0b0010") );
  UTST_CHECK_EQ( (bits.set_bits<3>(B1("0b1"))),   B4("0b1010") );

  // set_bits (specify dynamic length)

  UTST_CHECK_EQ( (bits.set_bits<1>(0,B1("0b1"))), B4("0b1011") );
  UTST_CHECK_EQ( (bits.set_bits<1>(1,B1("0b0"))), B4("0b1001") );
  UTST_CHECK_EQ( (bits.set_bits<1>(2,B1("0b1"))), B4("0b1101") );
  UTST_CHECK_EQ( (bits.set_bits<1>(3,B1("0b0"))), B4("0b0101") );
}

//------------------------------------------------------------------------
// TestBitArray4bGetSetField
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestBitArray4bGetSetField )
{
  using namespace stdx;
  stdx::BitArray<4> bits("0b1010");

  typedef BitArray<1> B1;
  typedef BitArray<2> B2;
  typedef BitArray<3> B3;
  typedef BitArray<4> B4;

  // get_bits (explicit field)

  UTST_CHECK_EQ( (bits.get_field<0,0>()), B1("0b0")    );
  UTST_CHECK_EQ( (bits.get_field<1,1>()), B1("0b1")    );
  UTST_CHECK_EQ( (bits.get_field<2,2>()), B1("0b0")    );
  UTST_CHECK_EQ( (bits.get_field<3,3>()), B1("0b1")    );

  UTST_CHECK_EQ( (bits.get_field<1,0>()), B2("0b10")   );
  UTST_CHECK_EQ( (bits.get_field<2,1>()), B2("0b01")   );
  UTST_CHECK_EQ( (bits.get_field<3,2>()), B2("0b10")   );

  UTST_CHECK_EQ( (bits.get_field<2,0>()), B3("0b010")  );
  UTST_CHECK_EQ( (bits.get_field<3,1>()), B3("0b101")  );

  UTST_CHECK_EQ( (bits.get_field<3,0>()), B4("0b1010") );

  // set_bits (explicit field)

  UTST_CHECK_EQ( (bits.set_field<0,0>(B1("0b1"))), B4("0b1011") );
  UTST_CHECK_EQ( (bits.set_field<1,1>(B1("0b0"))), B4("0b1001") );
  UTST_CHECK_EQ( (bits.set_field<2,2>(B1("0b1"))), B4("0b1101") );
  UTST_CHECK_EQ( (bits.set_field<3,3>(B1("0b0"))), B4("0b0101") );

  // get/set field (named field)

  typedef StaticBitField<0,0> b00;
  UTST_CHECK_EQ( bits.get_field<b00>(),             B1("0b1")    );
  UTST_CHECK_EQ( bits.set_field<b00>(B1("0b0")),    B4("0b0100") );

  typedef StaticBitField<1,1> b11;
  UTST_CHECK_EQ( bits.get_field<b11>(),             B1("0b0")    );
  UTST_CHECK_EQ( bits.set_field<b11>(B1("0b1")),    B4("0b0110") );

  typedef StaticBitField<2,2> b22;
  UTST_CHECK_EQ( bits.get_field<b22>(),             B1("0b1")    );
  UTST_CHECK_EQ( bits.set_field<b22>(B1("0b0")),    B4("0b0010") );

  typedef StaticBitField<3,3> b33;
  UTST_CHECK_EQ( bits.get_field<b33>(),             B1("0b0")    );
  UTST_CHECK_EQ( bits.set_field<b33>(B1("0b1")),    B4("0b1010") );

  typedef StaticBitField<1,0> b10;
  UTST_CHECK_EQ( bits.get_field<b10>(),             B2("0b10")   );
  UTST_CHECK_EQ( bits.set_field<b10>(B2("0b01")),   B4("0b1001") );

  typedef StaticBitField<2,1> b21;
  UTST_CHECK_EQ( bits.get_field<b21>(),             B2("0b00")   );
  UTST_CHECK_EQ( bits.set_field<b21>(B2("0b11")),   B4("0b1111") );

  typedef StaticBitField<3,2> b32;
  UTST_CHECK_EQ( bits.get_field<b32>(),             B2("0b11")   );
  UTST_CHECK_EQ( bits.set_field<b32>(B2("0b00")),   B4("0b0011") );

  typedef StaticBitField<2,0> b20;
  UTST_CHECK_EQ( bits.get_field<b20>(),             B3("0b011")  );
  UTST_CHECK_EQ( bits.set_field<b20>(B3("0b100")),  B4("0b0100") );

  typedef StaticBitField<3,1> b31;
  UTST_CHECK_EQ( bits.get_field<b31>(),             B3("0b010")  );
  UTST_CHECK_EQ( bits.set_field<b31>(B3("0b101")),  B4("0b1010") );

  typedef StaticBitField<3,0> b30;
  UTST_CHECK_EQ( bits.get_field<b30>(),             B4("0b1010") );
  UTST_CHECK_EQ( bits.set_field<b30>(B4("0b0101")), B4("0b0101") );
}

//------------------------------------------------------------------------
// TestBitArray32bBasic
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestBitArray32bBasic )
{
  stdx::BitArray<32> bits(0xdeadbeef);
  UTST_CHECK_EQ( bits.to_ulong(), 0xdeadbeefu );
  UTST_CHECK_EQ( bits.size(),     32   );
  UTST_CHECK_EQ( bits.get(0),     1    );
  UTST_CHECK_EQ( bits.get(1),     1    );
  UTST_CHECK_EQ( bits.get(2),     1    );
  UTST_CHECK_EQ( bits.get(3),     1    );
  UTST_CHECK_EQ( bits.get(28),    1    );
  UTST_CHECK_EQ( bits.get(29),    0    );
  UTST_CHECK_EQ( bits.get(30),    1    );
  UTST_CHECK_EQ( bits.get(31),    1    );

  bits.set(16);   UTST_CHECK_EQ( bits.to_ulong(), 0xdeadbeefu );
  bits.reset(16); UTST_CHECK_EQ( bits.to_ulong(), 0xdeacbeefu );
  bits.set(16,1); UTST_CHECK_EQ( bits.to_ulong(), 0xdeadbeefu );
  bits.set(16,0); UTST_CHECK_EQ( bits.to_ulong(), 0xdeacbeefu );
  bits.reset();   UTST_CHECK_EQ( bits.to_ulong(), 0x00000000u );
  bits.set();     UTST_CHECK_EQ( bits.to_ulong(), 0xffffffffu );

  bits = 0xdeadbeef;
  stdx::BitArray<32> bitsA = bits;
  stdx::BitArray<32> bitsB(0xdeadbeefu);
  stdx::BitArray<32> bitsC(0x1);

  UTST_CHECK_EQ(  bits, bitsA );
  UTST_CHECK_EQ(  bits, bitsB );
  UTST_CHECK_NEQ( bits, bitsC );
}

//------------------------------------------------------------------------
// TestBitArray32bOperators
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestBitArray32bOperators )
{
  stdx::BitArray<32> bitsA("0xfcacacaf");
  stdx::BitArray<32> bitsB("0x7acacacf");
  stdx::BitArray<32> bits;

  // Unary operators

  UTST_CHECK_EQ( ~bitsA, stdx::BitArray<32>("0x03535350") );

  // Inplace operators

  bits = bitsA;
  UTST_CHECK_EQ( bits &= bitsB, stdx::BitArray<32>("0x7888888f") );

  bits = bitsA;
  UTST_CHECK_EQ( bits |= bitsB, stdx::BitArray<32>("0xfeeeeeef") );

  bits = bitsA;
  UTST_CHECK_EQ( bits ^= bitsB, stdx::BitArray<32>("0x86666660") );

  bits = bitsA;
  UTST_CHECK_EQ( bits <<= 2,    stdx::BitArray<32>("0xf2b2b2bc") );

  bits = bitsA;
  UTST_CHECK_EQ( bits >>= 2,    stdx::BitArray<32>("0x3f2b2b2b") );

  // Binary operators

  UTST_CHECK_EQ( bitsA & bitsB, stdx::BitArray<32>("0x7888888f") );
  UTST_CHECK_EQ( bitsA | bitsB, stdx::BitArray<32>("0xfeeeeeef") );
  UTST_CHECK_EQ( bitsA ^ bitsB, stdx::BitArray<32>("0x86666660") );
  UTST_CHECK_EQ( bitsA << 2,    stdx::BitArray<32>("0xf2b2b2bc") );
  UTST_CHECK_EQ( bitsA >> 2,    stdx::BitArray<32>("0x3f2b2b2b") );
}

//------------------------------------------------------------------------
// TestBitArray32bGetSetBits
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestBitArray32bGetSetBits )
{
  using namespace stdx;
  BitArray<32> bits("0xdeadbeef");

  typedef BitArray<8>  B8;
  typedef BitArray<16> B16;
  typedef BitArray<32> B32;

  // get_bits (static length)

  UTST_CHECK_EQ( (bits.get_bits<0,8>()),   B8("0xef") );
  UTST_CHECK_EQ( (bits.get_bits<8,8>()),   B8("0xbe") );
  UTST_CHECK_EQ( (bits.get_bits<16,8>()),  B8("0xad") );
  UTST_CHECK_EQ( (bits.get_bits<24,8>()),  B8("0xde") );

  UTST_CHECK_EQ( (bits.get_bits<0,16>()),  B16("0xbeef") );
  UTST_CHECK_EQ( (bits.get_bits<16,16>()), B16("0xdead") );

  UTST_CHECK_EQ( (bits.get_bits<0,32>()),  B32("0xdeadbeef") );

  UTST_CHECK_EQ( (bits.get_bits<1,16>()),  B16("0xdf77") );
  UTST_CHECK_EQ( (bits.get_bits<2,16>()),  B16("0x6fbb") );
  UTST_CHECK_EQ( (bits.get_bits<3,16>()),  B16("0xb7dd") );
  UTST_CHECK_EQ( (bits.get_bits<4,16>()),  B16("0xdbee") );

  // get_bits (dynamic length)

  UTST_CHECK_EQ( (bits.get_bits<8>(0)),    B8("0xef") );
  UTST_CHECK_EQ( (bits.get_bits<8>(8)),    B8("0xbe") );
  UTST_CHECK_EQ( (bits.get_bits<8>(16)),   B8("0xad") );
  UTST_CHECK_EQ( (bits.get_bits<8>(24)),   B8("0xde") );

  UTST_CHECK_EQ( (bits.get_bits<16>(0)),   B16("0xbeef") );
  UTST_CHECK_EQ( (bits.get_bits<16>(16)),  B16("0xdead") );

  UTST_CHECK_EQ( (bits.get_bits<32>(0)),   B32("0xdeadbeef") );

  UTST_CHECK_EQ( (bits.get_bits<16>(1)),   B16("0xdf77") );
  UTST_CHECK_EQ( (bits.get_bits<16>(2)),   B16("0x6fbb") );
  UTST_CHECK_EQ( (bits.get_bits<16>(3)),   B16("0xb7dd") );
  UTST_CHECK_EQ( (bits.get_bits<16>(4)),   B16("0xdbee") );

  // set_bits (specify static length explicitly)

  UTST_CHECK_EQ( (bits.set_bits<0,8>(B8("0xfe"))),  B32("0xdeadbefe") );
  UTST_CHECK_EQ( (bits.set_bits<8,8>(B8("0xeb"))),  B32("0xdeadebfe") );
  UTST_CHECK_EQ( (bits.set_bits<16,8>(B8("0xda"))), B32("0xdedaebfe") );
  UTST_CHECK_EQ( (bits.set_bits<24,8>(B8("0xed"))), B32("0xeddaebfe") );

  UTST_CHECK_EQ( (bits.set_bits<0,16>(B16("0xfeeb"))),  B32("0xeddafeeb") );
  UTST_CHECK_EQ( (bits.set_bits<16,16>(B16("0xdaed"))), B32("0xdaedfeeb") );

  UTST_CHECK_EQ( (bits.set_bits<0,32>(B32("0xfeebdaed"))),
                 B32("0xfeebdaed") );

  // set_bits (specify dynamic length)

  UTST_CHECK_EQ( (bits.set_bits<8>(0,B8("0xde"))),  B32("0xfeebdade") );
  UTST_CHECK_EQ( (bits.set_bits<8>(8,B8("0xad"))),  B32("0xfeebadde") );
  UTST_CHECK_EQ( (bits.set_bits<8>(16,B8("0xbe"))), B32("0xfebeadde") );
  UTST_CHECK_EQ( (bits.set_bits<8>(24,B8("0xef"))), B32("0xefbeadde") );

  UTST_CHECK_EQ( (bits.set_bits<16>(0,B16("0xedda"))),  B32("0xefbeedda") );
  UTST_CHECK_EQ( (bits.set_bits<16>(16,B16("0xebfe"))), B32("0xebfeedda") );

  UTST_CHECK_EQ( (bits.set_bits<32>(0,B32("0xaddeefbe"))),
                 B32("0xaddeefbe") );
}

//------------------------------------------------------------------------
// TestBitArray32bExtTrunc
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestBitArray32bExtTrunc )
{
  using namespace stdx;
  BitArray<32> bitsA("0xfcacacaf");
  BitArray<32> bitsB("0x7acacacf");

  // Static bit extension and truncation

  UTST_CHECK_EQ( bitsA.to_zext<37>(), BitArray<37>("0x00fcacacaf") );
  UTST_CHECK_EQ( bitsA.to_zext<67>(),
                 BitArray<67>("0x000000000fcacacaf") );

  UTST_CHECK_EQ( bitsB.to_zext<37>(), BitArray<37>("0x007acacacf") );
  UTST_CHECK_EQ( bitsB.to_zext<67>(),
                 BitArray<67>("0x0000000007acacacf") );

  UTST_CHECK_EQ( bitsA.to_sext<37>(), BitArray<37>("0x1ffcacacaf") );
  UTST_CHECK_EQ( bitsA.to_sext<67>(),
                 BitArray<67>("0x7fffffffffcacacaf") );

  UTST_CHECK_EQ( bitsB.to_sext<37>(), BitArray<37>("0x007acacacf") );
  UTST_CHECK_EQ( bitsB.to_sext<67>(),
                 BitArray<67>("0x0000000007acacacf") );

  UTST_CHECK_EQ( bitsA.to_trunc<8>(), BitArray<8>("0xaf") );
  UTST_CHECK_EQ( bitsB.to_trunc<8>(), BitArray<8>("0xcf") );
}

//------------------------------------------------------------------------
// TestBitArray37bBasic
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestBitArray37bBasic )
{
  stdx::BitArray<37> bits(0x3);
  UTST_CHECK_EQ( bits.to_str(), "0x0000000003" );
  UTST_CHECK_EQ( bits.size(),    37 );
  UTST_CHECK_EQ( bits.get(0),    1  );
  UTST_CHECK_EQ( bits.get(1),    1  );
  UTST_CHECK_EQ( bits.get(2),    0  );
  UTST_CHECK_EQ( bits.get(31),   0  );
  UTST_CHECK_EQ( bits.get(32),   0  );
  UTST_CHECK_EQ( bits.get(33),   0  );
  UTST_CHECK_EQ( bits.get(34),   0  );
  UTST_CHECK_EQ( bits.get(35),   0  );
  UTST_CHECK_EQ( bits.get(36),   0  );

  bits.set(0);   UTST_CHECK_EQ( bits.to_str(), "0x0000000003" );
  bits.reset(0); UTST_CHECK_EQ( bits.to_str(), "0x0000000002" );
  bits.set(0,1); UTST_CHECK_EQ( bits.to_str(), "0x0000000003" );
  bits.set(0,0); UTST_CHECK_EQ( bits.to_str(), "0x0000000002" );
  bits.reset();  UTST_CHECK_EQ( bits.to_str(), "0x0000000000" );
  bits.set();    UTST_CHECK_EQ( bits.to_str(), "0x1fffffffff" );

  bits.from_str("0x1a80000000");
  UTST_CHECK_EQ( bits.to_str(), "0x1a80000000" );
  UTST_CHECK_EQ( bits.get(0),    0  );
  UTST_CHECK_EQ( bits.get(1),    0  );
  UTST_CHECK_EQ( bits.get(2),    0  );
  UTST_CHECK_EQ( bits.get(31),   1  );
  UTST_CHECK_EQ( bits.get(32),   0  );
  UTST_CHECK_EQ( bits.get(33),   1  );
  UTST_CHECK_EQ( bits.get(34),   0  );
  UTST_CHECK_EQ( bits.get(35),   1  );
  UTST_CHECK_EQ( bits.get(36),   1  );

  bits.set(36);   UTST_CHECK_EQ( bits.to_str(), "0x1a80000000" );
  bits.reset(36); UTST_CHECK_EQ( bits.to_str(), "0x0a80000000" );
  bits.set(36,1); UTST_CHECK_EQ( bits.to_str(), "0x1a80000000" );
  bits.set(36,0); UTST_CHECK_EQ( bits.to_str(), "0x0a80000000" );

  stdx::BitArray<37> bitsA = bits;
  stdx::BitArray<37> bitsB("0x0a80000000");
  stdx::BitArray<37> bitsC("0x1a80000000");

  UTST_CHECK_EQ(  bits, bitsA );
  UTST_CHECK_EQ(  bits, bitsB );
  UTST_CHECK_NEQ( bits, bitsC );
}

//------------------------------------------------------------------------
// TestBitArray37bOperators
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestBitArray37bOperators )
{
  using namespace stdx;
  BitArray<37> bitsA("0x0facacacaf");
  BitArray<37> bitsB("0x1fcacacacf");
  BitArray<37> bits;

  // Unary operators

  UTST_CHECK_EQ( ~bitsA, BitArray<37>("0x1053535350") );

  // Inplace operators

  bits = bitsA;
  UTST_CHECK_EQ( bits &= bitsB, BitArray<37>("0x0f8888888f") );

  bits = bitsA;
  UTST_CHECK_EQ( bits |= bitsB, BitArray<37>("0x1feeeeeeef") );

  bits = bitsA;
  UTST_CHECK_EQ( bits ^= bitsB, BitArray<37>("0x1066666660") );

  bits = bitsA;
  UTST_CHECK_EQ( bits <<= 2,    BitArray<37>("0x1eb2b2b2bc") );

  bits = bitsA;
  UTST_CHECK_EQ( bits >>= 2,    BitArray<37>("0x03eb2b2b2b") );

  bits = bitsA;
  UTST_CHECK_EQ( bits <<= 16,   BitArray<37>("0x0cacaf0000") );

  bits = bitsA;
  UTST_CHECK_EQ( bits >>= 16,   BitArray<37>("0x00000facac") );

  // Binary operators

  UTST_CHECK_EQ( bitsA & bitsB, BitArray<37>("0x0f8888888f") );
  UTST_CHECK_EQ( bitsA | bitsB, BitArray<37>("0x1feeeeeeef") );
  UTST_CHECK_EQ( bitsA ^ bitsB, BitArray<37>("0x1066666660") );
  UTST_CHECK_EQ( bitsA << 2,    BitArray<37>("0x1eb2b2b2bc") );
  UTST_CHECK_EQ( bitsA >> 2,    BitArray<37>("0x03eb2b2b2b") );
  UTST_CHECK_EQ( bitsA << 16,   BitArray<37>("0x0cacaf0000") );
  UTST_CHECK_EQ( bitsA >> 16,   BitArray<37>("0x00000facac") );
}

//------------------------------------------------------------------------
// TestBitArray37bGetSetBits
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestBitArray37bGetSetBits )
{
  using namespace stdx;
  BitArray<37> bits("0x1fdeadbeef");

  typedef BitArray<5>  B5;
  typedef BitArray<8>  B8;
  typedef BitArray<16> B16;
  typedef BitArray<32> B32;
  typedef BitArray<36> B36;
  typedef BitArray<37> B37;

  // get_bits (static length)

  UTST_CHECK_EQ( (bits.get_bits<0,8>()),   B8("0xef") );
  UTST_CHECK_EQ( (bits.get_bits<8,8>()),   B8("0xbe") );
  UTST_CHECK_EQ( (bits.get_bits<16,8>()),  B8("0xad") );
  UTST_CHECK_EQ( (bits.get_bits<24,8>()),  B8("0xde") );
  UTST_CHECK_EQ( (bits.get_bits<32,5>()),  B5("0x1f") );

  UTST_CHECK_EQ( (bits.get_bits<0,16>()),  B16("0xbeef") );
  UTST_CHECK_EQ( (bits.get_bits<16,16>()), B16("0xdead") );

  UTST_CHECK_EQ( (bits.get_bits<0,32>()),  B32("0xdeadbeef") );

  UTST_CHECK_EQ( (bits.get_bits<1,16>()),  B16("0xdf77") );
  UTST_CHECK_EQ( (bits.get_bits<2,16>()),  B16("0x6fbb") );
  UTST_CHECK_EQ( (bits.get_bits<3,16>()),  B16("0xb7dd") );
  UTST_CHECK_EQ( (bits.get_bits<4,16>()),  B16("0xdbee") );

  UTST_CHECK_EQ( (bits.get_bits<15,16>()), B16("0xbd5b") );
  UTST_CHECK_EQ( (bits.get_bits<17,16>()), B16("0xef56") );
  UTST_CHECK_EQ( (bits.get_bits<19,16>()), B16("0xfbd5") );
  UTST_CHECK_EQ( (bits.get_bits<21,16>()), B16("0xfef5") );

  // get_bits (dynamic length)

  UTST_CHECK_EQ( (bits.get_bits<8>(0)),    B8("0xef") );
  UTST_CHECK_EQ( (bits.get_bits<8>(8)),    B8("0xbe") );
  UTST_CHECK_EQ( (bits.get_bits<8>(16)),   B8("0xad") );
  UTST_CHECK_EQ( (bits.get_bits<8>(24)),   B8("0xde") );
  UTST_CHECK_EQ( (bits.get_bits<5>(32)),   B5("0x1f") );

  UTST_CHECK_EQ( (bits.get_bits<16>(0)),   B16("0xbeef") );
  UTST_CHECK_EQ( (bits.get_bits<16>(16)),  B16("0xdead") );

  UTST_CHECK_EQ( (bits.get_bits<32>(0)),   B32("0xdeadbeef") );

  UTST_CHECK_EQ( (bits.get_bits<16>(1)),   B16("0xdf77") );
  UTST_CHECK_EQ( (bits.get_bits<16>(2)),   B16("0x6fbb") );
  UTST_CHECK_EQ( (bits.get_bits<16>(3)),   B16("0xb7dd") );
  UTST_CHECK_EQ( (bits.get_bits<16>(4)),   B16("0xdbee") );

  UTST_CHECK_EQ( (bits.get_bits<16>(15)),  B16("0xbd5b") );
  UTST_CHECK_EQ( (bits.get_bits<16>(17)),  B16("0xef56") );
  UTST_CHECK_EQ( (bits.get_bits<16>(19)),  B16("0xfbd5") );
  UTST_CHECK_EQ( (bits.get_bits<16>(21)),  B16("0xfef5") );

  // set_bits (specify static length explicitly)

  UTST_CHECK_EQ( (bits.set_bits<0,8>(B8("0xfe"))),  B37("0x1fdeadbefe") );
  UTST_CHECK_EQ( (bits.set_bits<8,8>(B8("0xeb"))),  B37("0x1fdeadebfe") );
  UTST_CHECK_EQ( (bits.set_bits<16,8>(B8("0xda"))), B37("0x1fdedaebfe") );
  UTST_CHECK_EQ( (bits.set_bits<24,8>(B8("0xed"))), B37("0x1feddaebfe") );
  UTST_CHECK_EQ( (bits.set_bits<32,5>(B5("0x0a"))), B37("0x0aeddaebfe") );

  UTST_CHECK_EQ( (bits.set_bits<0,16>(B16("0xfeeb"))),  B37("0x0aeddafeeb") );
  UTST_CHECK_EQ( (bits.set_bits<16,16>(B16("0xdaed"))), B37("0x0adaedfeeb") );

  UTST_CHECK_EQ( (bits.set_bits<0,37>(B37("0x1bfeebdaed"))),
                 B37("0x1bfeebdaed") );

  UTST_CHECK_EQ( (bits.set_bits<20,16>(B16("0x1234"))),
                 B37("0x11234bdaed") );

  // set_bits (specify dynamic length)

  UTST_CHECK_EQ( (bits.set_bits<0,8>(B8("0xde"))),  B37("0x11234bdade") );
  UTST_CHECK_EQ( (bits.set_bits<8,8>(B8("0xad"))),  B37("0x11234badde") );
  UTST_CHECK_EQ( (bits.set_bits<16,8>(B8("0xb4"))), B37("0x1123b4adde") );
  UTST_CHECK_EQ( (bits.set_bits<24,8>(B8("0x32"))), B37("0x1132b4adde") );
  UTST_CHECK_EQ( (bits.set_bits<32,5>(B5("0x01"))), B37("0x0132b4adde") );

  UTST_CHECK_EQ( (bits.set_bits<0,16>(B16("0xedda"))),  B37("0x0132b4edda") );
  UTST_CHECK_EQ( (bits.set_bits<16,16>(B16("0x4b23"))), B37("0x014b23edda") );

  UTST_CHECK_EQ( (bits.set_bits<0,37>(B37("0x1adde32b41"))),
                 B37("0x1adde32b41") );

  UTST_CHECK_EQ( (bits.set_bits<20,16>(B16("0x1234"))),
                 B37("0x1123432b41") );
}

//------------------------------------------------------------------------
// TestBitArray37bExtTrunc
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestBitArray37bExtTrunc )
{
  using namespace stdx;
  BitArray<37> bitsA("0x0facacacaf");
  BitArray<37> bitsB("0x1fcacacacf");

  UTST_CHECK_EQ( bitsA.to_zext<47>(), BitArray<47>("0x000facacacaf") );
  UTST_CHECK_EQ( bitsA.to_zext<67>(),
                 BitArray<67>("0x00000000facacacaf") );

  UTST_CHECK_EQ( bitsB.to_zext<47>(), BitArray<47>("0x001fcacacacf") );
  UTST_CHECK_EQ( bitsB.to_zext<67>(),
                 BitArray<67>("0x00000001fcacacacf") );

  UTST_CHECK_EQ( bitsA.to_sext<47>(), BitArray<47>("0x000facacacaf") );
  UTST_CHECK_EQ( bitsA.to_sext<67>(),
                 BitArray<67>("0x00000000facacacaf") );

  UTST_CHECK_EQ( bitsB.to_sext<47>(), BitArray<47>("0x7fffcacacacf") );
  UTST_CHECK_EQ( bitsB.to_sext<67>(),
                 BitArray<67>("0x7ffffffffcacacacf") );

  UTST_CHECK_EQ( bitsA.to_trunc<8>(),  BitArray<8>("0xaf") );
  UTST_CHECK_EQ( bitsB.to_trunc<8>(),  BitArray<8>("0xcf") );
  UTST_CHECK_EQ( bitsA.to_trunc<33>(), BitArray<33>("0x1acacacaf") );
  UTST_CHECK_EQ( bitsB.to_trunc<33>(), BitArray<33>("0x1cacacacf") );
}

//------------------------------------------------------------------------
// TestBitArrayLongShifts
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestBitArrayLongShifts )
{
  typedef stdx::BitArray<127> B;
  B bits("0x_1cacacac_acacacac_acacacac_acacacac");
  #define CHECK UTST_CHECK_EQ

  // Left shifts

  CHECK( bits <<   0, B("0x_1cacacac_acacacac_acacacac_acacacac") );

  CHECK( bits <<  16, B("0x_2cacacac_acacacac_acacacac_acac0000") );
  CHECK( bits <<  32, B("0x_2cacacac_acacacac_acacacac_00000000") );
  CHECK( bits <<  48, B("0x_2cacacac_acacacac_acac0000_00000000") );
  CHECK( bits <<  64, B("0x_2cacacac_acacacac_00000000_00000000") );
  CHECK( bits <<  80, B("0x_2cacacac_acac0000_00000000_00000000") );
  CHECK( bits <<  96, B("0x_2cacacac_00000000_00000000_00000000") );
  CHECK( bits << 112, B("0x_2cac0000_00000000_00000000_00000000") );

  CHECK( bits <<  17, B("0x_59595959_59595959_59595959_59580000") );
  CHECK( bits <<  33, B("0x_59595959_59595959_59595958_00000000") );
  CHECK( bits <<  49, B("0x_59595959_59595959_59580000_00000000") );
  CHECK( bits <<  65, B("0x_59595959_59595958_00000000_00000000") );
  CHECK( bits <<  81, B("0x_59595959_59580000_00000000_00000000") );
  CHECK( bits <<  97, B("0x_59595958_00000000_00000000_00000000") );
  CHECK( bits << 113, B("0x_59580000_00000000_00000000_00000000") );

  CHECK( bits << 128, B("0x_00000000_00000000_00000000_00000000") );

  // Right shifts

  CHECK( bits >>   0, B("0x_1cacacac_acacacac_acacacac_acacacac") );

  CHECK( bits >>  16, B("0x_00001cac_acacacac_acacacac_acacacac") );
  CHECK( bits >>  32, B("0x_00000000_1cacacac_acacacac_acacacac") );
  CHECK( bits >>  48, B("0x_00000000_00001cac_acacacac_acacacac") );
  CHECK( bits >>  64, B("0x_00000000_00000000_1cacacac_acacacac") );
  CHECK( bits >>  80, B("0x_00000000_00000000_00001cac_acacacac") );
  CHECK( bits >>  96, B("0x_00000000_00000000_00000000_1cacacac") );
  CHECK( bits >> 112, B("0x_00000000_00000000_00000000_00001cac") );

  CHECK( bits >>  17, B("0x_00000e56_56565656_56565656_56565656") );
  CHECK( bits >>  33, B("0x_00000000_0e565656_56565656_56565656") );
  CHECK( bits >>  49, B("0x_00000000_00000e56_56565656_56565656") );
  CHECK( bits >>  65, B("0x_00000000_00000000_0e565656_56565656") );
  CHECK( bits >>  81, B("0x_00000000_00000000_00000e56_56565656") );
  CHECK( bits >>  97, B("0x_00000000_00000000_00000000_0e565656") );
  CHECK( bits >> 113, B("0x_00000000_00000000_00000000_00000e56") );

  CHECK( bits >> 128, B("0x_00000000_00000000_00000000_00000000") );

  #undef CHECK
}

//------------------------------------------------------------------------
// TestBitArrayInvalidBitIndexException
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestBitArrayInvalidBitIndexException )
{
  using namespace stdx::BitContainerExceptions;

  stdx::BitArray<2> barray2(0x0);
  UTST_CHECK_THROW( EInvalidBitIndex, barray2.set(3)  );
  UTST_CHECK_THROW( EInvalidBitIndex, barray2.get(3)  );
  UTST_CHECK_THROW( EInvalidBitIndex, barray2.set(-1) );
  UTST_CHECK_THROW( EInvalidBitIndex, barray2.get(-1) );

  stdx::BitArray<37> barray37("0x1adeadbeef");
  UTST_CHECK_THROW( EInvalidBitIndex, barray37.set(37) );
  UTST_CHECK_THROW( EInvalidBitIndex, barray37.get(37) );
  UTST_CHECK_THROW( EInvalidBitIndex, barray37.set(-1) );
  UTST_CHECK_THROW( EInvalidBitIndex, barray37.get(-1) );
}

//------------------------------------------------------------------------
// TestBitArrayStringConversion
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestBitArrayStringConversion )
{
  using namespace stdx;
  using namespace stdx::BitContainerExceptions;
  #define CHECK UTST_CHECK_EQ

  CHECK( BitArray<2>("0x3").to_str(),               "0x3"          );
  CHECK( BitArray<5>("0x18").to_str(),              "0x18"         );
  CHECK( BitArray<6>("0x18").to_str(),              "0x18"         );
  CHECK( BitArray<7>("0x18").to_str(),              "0x18"         );
  CHECK( BitArray<8>("0x18").to_str(),              "0x18"         );
  CHECK( BitArray<32>("0xdeadbeef").to_str(),       "0xdeadbeef"   );
  CHECK( BitArray<32>("0xdead_beef").to_str(),      "0xdeadbeef"   );
  CHECK( BitArray<32>("0x_dead_beef_").to_str(),    "0xdeadbeef"   );
  CHECK( BitArray<32>("0x__dead__beef__").to_str(), "0xdeadbeef"   );
  CHECK( BitArray<37>("0x03").to_str(),             "0x0000000003" );
  CHECK( BitArray<37>("0x1adeadbeef").to_str(),     "0x1adeadbeef" );

  CHECK( BitArray<2>("0b11").to_str(),              "0x3"          );
  CHECK( BitArray<8>("0b1111_1111").to_str(),       "0xff"         );
  CHECK( BitArray<8>("0b_1111_1111_").to_str(),     "0xff"         );
  CHECK( BitArray<8>("0b__1111__1111__").to_str(),  "0xff"         );

  BitArray<37> long_barray("0b1101011110000111100001111000011110000");
  CHECK( long_barray.to_str(), "0x1af0f0f0f0" );

  UTST_CHECK_THROW( EInvalidStringConversion, BitArray<2>("0xdeadbeef") );
  UTST_CHECK_THROW( EInvalidStringConversion, BitArray<32>("deadbeef")  );
  UTST_CHECK_THROW( EInvalidStringConversion, BitArray<32>("0xinvalid") );

  UTST_CHECK_THROW( EInvalidStringConversion, BitArray<2>("0xdeadbeef") );
  UTST_CHECK_THROW( EInvalidStringConversion, BitArray<32>("deadbeef")  );
  UTST_CHECK_THROW( EInvalidStringConversion, BitArray<32>("0xinvalid") );

  #undef CHECK
}

//------------------------------------------------------------------------
// TestBitArrayUlongConversion
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestBitArrayUlongConversion )
{
  using namespace stdx;
  using namespace stdx::BitContainerExceptions;

  UTST_CHECK_EQ( BitArray<2>(0x3).to_ulong(),         0x03u          );
  UTST_CHECK_EQ( BitArray<2>(0x18).to_ulong(),        0x18u          );
  UTST_CHECK_EQ( BitArray<32>(0xdeadbeef).to_ulong(), 0xdeadbeefu    );
  UTST_CHECK_EQ( BitArray<37>(0x3).to_str(),          "0x0000000003" );

  UTST_CHECK_THROW( EInvalidUlongConversion, BitArray<2>(0xdeadbeef) );
  UTST_CHECK_THROW( EInvalidUlongConversion, \
                    BitArray<64>(0x3).to_ulong() );
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv );
}

