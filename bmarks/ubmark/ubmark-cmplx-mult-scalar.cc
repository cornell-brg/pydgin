//========================================================================
// ubmark-cmplx-mult-scalar
//========================================================================
// We can use the optimize function attribute to force the compiler to
// unroll this loop. We get better code if we use the special
// __restrict__ keyword so that the compiler knows the arrays don't
// overlap, and if we use pointer bumps as opposed to array indexing.

#include "ubmark-cmplx-mult-scalar.h"

__attribute__ ((noinline,optimize("unroll-loops")))
void cmplx_mult_scalar( Complex* __restrict__ dest,
                        Complex* __restrict__ src0,
                        Complex* __restrict__ src1, int size )
{
  for ( int i = 0; i < size; i++ )
    *dest++ = *src0++ * *src1++;
}

