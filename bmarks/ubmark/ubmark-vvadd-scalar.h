//========================================================================
// ubmark-vvadd-scalar
//========================================================================
// We had to move this into its own file to avoid issues that were
// causing very odd problems in the xloop code. If we put the
// implementation in the ubmark-vvadd.cc then for some reason the
// compiler generates code which uses registers that makes it just
// fundamentally incorrect.

#ifndef UBMARK_VVADD_SCALAR_H
#define UBMARK_VVADD_SCALAR_H

void vvadd_scalar( int* __restrict__ dest,
                   int* __restrict__ src0,
                   int* __restrict__ src1, int size );

#endif /* UBMARK_VVADD_SCALAR_H */

