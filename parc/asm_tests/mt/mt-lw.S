//========================================================================
// mt-lw
//========================================================================

#include "mt-macros.h"

    TEST_MT_BEGIN

    //--------------------------------------------------------------------
    // Basic tests
    //--------------------------------------------------------------------

    TEST_LD_OP( lw, 0,  tdata_0, 0x00ff00ff )
    TEST_LD_OP( lw, 4,  tdata_0, 0xff00ff00 )
    TEST_LD_OP( lw, 8,  tdata_0, 0x0ff00ff0 )
    TEST_LD_OP( lw, 12, tdata_0, 0xf00ff00f )

    // Test with negative offset

    TEST_LD_OP( lw, -12, tdata_3, 0x00ff00ff )
    TEST_LD_OP( lw,  -8, tdata_3, 0xff00ff00 )
    TEST_LD_OP( lw,  -4, tdata_3, 0x0ff00ff0 )
    TEST_LD_OP( lw,   0, tdata_3, 0xf00ff00f )

    // Test with a negative base

    la    $2, tdata_0
    addiu $2, $2, -32
    lw    $4, 32($2)
    TEST_CHECK_EQ( $4, 0x00ff00ff )

    // Test with unaligned base

    la    $2, tdata_0
    addiu $2, $2, -3
    lw    $4, 7($2)
    TEST_CHECK_EQ( $4, 0xff00ff00 )

    //--------------------------------------------------------------------
    // Bypassing tests
    //--------------------------------------------------------------------

    TEST_LD_DEST_BYP( 0, lw, 4, tdata_1, 0x0ff00ff0 )
    TEST_LD_DEST_BYP( 1, lw, 4, tdata_2, 0xf00ff00f )
    TEST_LD_DEST_BYP( 2, lw, 4, tdata_3, 0xabcdef01 )
    TEST_LD_DEST_BYP( 3, lw, 4, tdata_4, 0xbcdef012 )
    TEST_LD_DEST_BYP( 4, lw, 4, tdata_5, 0xcdef0123 )

    TEST_LD_SRC0_BYP( 0, lw, 4, tdata_1, 0x0ff00ff0 )
    TEST_LD_SRC0_BYP( 1, lw, 4, tdata_2, 0xf00ff00f )
    TEST_LD_SRC0_BYP( 2, lw, 4, tdata_3, 0xabcdef01 )
    TEST_LD_SRC0_BYP( 3, lw, 4, tdata_4, 0xbcdef012 )
    TEST_LD_SRC0_BYP( 4, lw, 4, tdata_5, 0xcdef0123 )

    //--------------------------------------------------------------------
    // Test write-after-write hazard
    //--------------------------------------------------------------------

    la $4, tdata_0
    lw $3, 0($4)
    li $3, 2
    TEST_CHECK_EQ( $3, 2 )

    la $5, tdata_0
    lw $6, 0($5)
    nop
    li $6, 2
    TEST_CHECK_EQ( $6, 2 )

    TEST_MT_END

    //--------------------------------------------------------------------
    // Test data
    //--------------------------------------------------------------------

    .data
    .align 4

tdata_0: .word 0x00ff00ff
tdata_1: .word 0xff00ff00
tdata_2: .word 0x0ff00ff0
tdata_3: .word 0xf00ff00f
tdata_4: .word 0xabcdef01
tdata_5: .word 0xbcdef012
tdata_6: .word 0xcdef0123

