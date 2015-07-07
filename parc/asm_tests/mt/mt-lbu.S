//========================================================================
// mt-lbu
//========================================================================

#include "mt-macros.h"

    TEST_MT_BEGIN

    //--------------------------------------------------------------------
    // Basic tests
    //--------------------------------------------------------------------

    TEST_LD_OP( lbu, 0, tdata_0, 0x00000001 )
    TEST_LD_OP( lbu, 1, tdata_0, 0x00000002 )
    TEST_LD_OP( lbu, 2, tdata_0, 0x00000003 )
    TEST_LD_OP( lbu, 3, tdata_0, 0x00000004 )

    // Test no sign extension

    TEST_LD_OP( lbu, 0, tdata_7, 0x00000081 )
    TEST_LD_OP( lbu, 1, tdata_7, 0x00000082 )
    TEST_LD_OP( lbu, 2, tdata_7, 0x00000083 )
    TEST_LD_OP( lbu, 3, tdata_7, 0x000000ff )

    // Test with negative offset

    TEST_LD_OP( lbu, -3, tdata_3, 0x00000001 )
    TEST_LD_OP( lbu, -2, tdata_3, 0x00000002 )
    TEST_LD_OP( lbu, -1, tdata_3, 0x00000003 )
    TEST_LD_OP( lbu,  0, tdata_3, 0x00000004 )

    // Test with a negative base

    la    $2, tdata_0
    addiu $2, $2, -31
    lbu   $4, 31($2)
    TEST_CHECK_EQ( $4, 0x00000001 )

    // Test with unaligned base

    la    $2, tdata_0
    addiu $2, $2, -3
    lbu   $4, 4($2)
    TEST_CHECK_EQ( $4, 0x00000002 )

    //--------------------------------------------------------------------
    // Bypassing tests
    //--------------------------------------------------------------------

    TEST_LD_DEST_BYP( 0, lbu, 1, tdata_1, 0x00000003 )
    TEST_LD_DEST_BYP( 1, lbu, 1, tdata_2, 0x00000004 )
    TEST_LD_DEST_BYP( 2, lbu, 1, tdata_3, 0x00000005 )
    TEST_LD_DEST_BYP( 3, lbu, 1, tdata_4, 0x00000006 )
    TEST_LD_DEST_BYP( 4, lbu, 1, tdata_5, 0x00000007 )

    TEST_LD_SRC0_BYP( 0, lbu, 1, tdata_1, 0x00000003 )
    TEST_LD_SRC0_BYP( 1, lbu, 1, tdata_2, 0x00000004 )
    TEST_LD_SRC0_BYP( 2, lbu, 1, tdata_3, 0x00000005 )
    TEST_LD_SRC0_BYP( 3, lbu, 1, tdata_4, 0x00000006 )
    TEST_LD_SRC0_BYP( 4, lbu, 1, tdata_5, 0x00000007 )

    //--------------------------------------------------------------------
    // Test write-after-write hazard
    //--------------------------------------------------------------------

    la  $4, tdata_0
    lbu $3, 0($4)
    li  $3, 2
    TEST_CHECK_EQ( $3, 2 )

    la  $5, tdata_0
    lbu $6, 0($5)
    nop
    li  $6, 2
    TEST_CHECK_EQ( $6, 2 )

    TEST_MT_END

    //--------------------------------------------------------------------
    // Test data
    //--------------------------------------------------------------------

    .data
    .align 1

tdata_0:  .byte 0x01
tdata_1:  .byte 0x02
tdata_2:  .byte 0x03
tdata_3:  .byte 0x04
tdata_4:  .byte 0x05
tdata_5:  .byte 0x06
tdata_6:  .byte 0x07
tdata_7:  .byte 0x81
tdata_8:  .byte 0x82
tdata_9:  .byte 0x83
tdata_11: .byte 0xff

