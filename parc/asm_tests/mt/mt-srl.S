//========================================================================
// mt-srl
//========================================================================

#include "mt-macros.h"

    TEST_MT_BEGIN

    //--------------------------------------------------------------------
    // Arithmetic tests
    //--------------------------------------------------------------------

    TEST_IMM_OP( srl, 0x80000000,  0, 0x80000000 )
    TEST_IMM_OP( srl, 0x80000000,  1, 0x40000000 )
    TEST_IMM_OP( srl, 0x80000000,  7, 0x01000000 )
    TEST_IMM_OP( srl, 0x80000000, 14, 0x00020000 )
    TEST_IMM_OP( srl, 0x80000001, 31, 0x00000001 )

    TEST_IMM_OP( srl, 0xffffffff,  0, 0xffffffff )
    TEST_IMM_OP( srl, 0xffffffff,  1, 0x7fffffff )
    TEST_IMM_OP( srl, 0xffffffff,  7, 0x01ffffff )
    TEST_IMM_OP( srl, 0xffffffff, 14, 0x0003ffff )
    TEST_IMM_OP( srl, 0xffffffff, 31, 0x00000001 )

    TEST_IMM_OP( srl, 0x21212121,  0, 0x21212121 )
    TEST_IMM_OP( srl, 0x21212121,  1, 0x10909090 )
    TEST_IMM_OP( srl, 0x21212121,  7, 0x00424242 )
    TEST_IMM_OP( srl, 0x21212121, 14, 0x00008484 )
    TEST_IMM_OP( srl, 0x21212121, 31, 0x00000000 )

    //--------------------------------------------------------------------
    // Source/Destination tests
    //--------------------------------------------------------------------

    TEST_IMM_SRC0_EQ_DEST( srl, 0x80000000, 7, 0x01000000 )

    //--------------------------------------------------------------------
    // Bypassing tests
    //--------------------------------------------------------------------

    TEST_IMM_DEST_BYP( 0, srl, 0x80000001,  7, 0x01000000 )
    TEST_IMM_DEST_BYP( 1, srl, 0x80000001, 14, 0x00020000 )
    TEST_IMM_DEST_BYP( 2, srl, 0x80000001, 31, 0x00000001 )
    TEST_IMM_DEST_BYP( 3, srl, 0x80000001, 27, 0x00000010 )
    TEST_IMM_DEST_BYP( 4, srl, 0x80000001, 22, 0x00000200 )

    TEST_IMM_SRC0_BYP( 0, srl, 0x80000001,  7, 0x01000000 )
    TEST_IMM_SRC0_BYP( 1, srl, 0x80000001, 14, 0x00020000 )
    TEST_IMM_SRC0_BYP( 2, srl, 0x80000001, 31, 0x00000001 )
    TEST_IMM_SRC0_BYP( 3, srl, 0x80000001, 27, 0x00000010 )
    TEST_IMM_SRC0_BYP( 4, srl, 0x80000001, 22, 0x00000200 )

    TEST_MT_END

