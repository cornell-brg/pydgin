//========================================================================
// ubmark-cmplx-mult-scalar
//========================================================================
// We had to move this into its own file to avoid issues that were
// causing very odd problems in the xloop code. If we put the
// implementation in the ubmark-cmplx-mult.cc then for some reason the
// compiler generates code which uses registers that makes it just
// fundamentally incorrect.

#ifndef UBMARK_CMPLX_MULT_SCALAR_H
#define UBMARK_CMPLX_MULT_SCALAR_H

#include "ubmark-cmplx-mult-Complex.h"

void cmplx_mult_scalar( Complex* __restrict__ dest,
                        Complex* __restrict__ src0,
                        Complex* __restrict__ src1, int size );

#endif /* UBMARK_CMPLX_MULT_SCALAR_H */

