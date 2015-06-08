//========================================================================
// tloops-scan.S
//========================================================================

#include "parc-macros.h"

    TEST_PARC_BEGIN

    // Test a simple loop with only integer operations

    // add dummy instructions to fit in cache line and not induce a primary
    // miss
    li     $2,  0
    li     $3,  0
    li     $4,  5
    li     $2,  0
    li     $2,  0
    li     $3,  0
    li     $3,  0
    la     $5,  tdata_4

    // lw instruction feeds a instruction in for loop body
    lw     $5,  0($5)
    j      l
1:  lw     $6,  0($5)
    addu   $3,  $3,  $2
    //addiu  $3,  $3,  2
    //addiu  $2,  $2,  1
    //mul    $6,  $6, $2
l:  for.u  $2,  $4,  1b
    j      _pass
    TEST_PARC_END

//------------------------------------------------------------------------
// Test data
//------------------------------------------------------------------------

   .data
   .align 4

tdata_0:   .word 0x00000001
tdata_1:   .word 0x00000001
tdata_2:   .word 0x00000001
tdata_3:   .word 0x00000001
tdata_4:   .word 0x00000001

