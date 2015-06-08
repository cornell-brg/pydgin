//========================================================================
// parcv3-vecincr.S
//========================================================================

#include "parc-macros.h"

  TEST_PARC_BEGIN

  li       $8,  8          // length
  la       $9,  tdata_0    // start_addr
  subu.xi  $10, $9, $8     // call vecincr

  TEST_CHECK_EQ( $8, $10 ) // check if all elements were visited

  la       $11, tdata_8
1:
  lw       $12, 0($9)      // load value
  lw       $13, 0($11)     // load ref
  TEST_CHECK_EQ( $12, $13 )
  addiu    $9,  $9,  4
  addiu    $11, $11, 4
  addiu    $8,  $8,  -1
  bnez     $8,  1b
  j        _pass

  TEST_PARC_END

//------------------------------------------------------------------------
// Test data
//------------------------------------------------------------------------

   .data
   .align 4

tdata_0:   .word 0x00000001
tdata_1:   .word 0x00000002
tdata_2:   .word 0x00000003
tdata_3:   .word 0x00000004
tdata_4:   .word 0x00000005
tdata_5:   .word 0x00000006
tdata_6:   .word 0x00000007
tdata_7:   .word 0x00000008

tdata_8:   .word 0x00000002
tdata_9:   .word 0x00000003
tdata_10:  .word 0x00000004
tdata_11:  .word 0x00000005
tdata_12:  .word 0x00000006
tdata_13:  .word 0x00000007
tdata_14:  .word 0x00000008
tdata_15:  .word 0x00000009
