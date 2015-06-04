//========================================================================
// parcv3-amo-xchg.S
//========================================================================

#include "parc-macros.h"

    TEST_PARC_BEGIN

    //--------------------------------------------------------------------
    // Basic tests
    //--------------------------------------------------------------------

    TEST_AMO_OP( amo.xchg, tdata_0, 0x0a0a0a0a, 0xdeadbeef, 0x0a0a0a0a )
    TEST_AMO_OP( amo.xchg, tdata_0, 0x0b0b0b0b, 0x0a0a0a0a, 0x0b0b0b0b )
    TEST_AMO_OP( amo.xchg, tdata_0, 0x0c0c0c0c, 0x0b0b0b0b, 0x0c0c0c0c )
    TEST_AMO_OP( amo.xchg, tdata_0, 0x0d0d0d0d, 0x0c0c0c0c, 0x0d0d0d0d )

    TEST_AMO_OP( amo.xchg, tdata_1, 0x0e0e0e0e, 0xdeadbeef, 0x0e0e0e0e )
    TEST_AMO_OP( amo.xchg, tdata_1, 0x0f0f0f0f, 0x0e0e0e0e, 0x0f0f0f0f )

    //--------------------------------------------------------------------
    // Destination bypassing tests
    //--------------------------------------------------------------------

    TEST_AMO_DEST_BYP( 0, amo.xchg, tdata_2, 0x0a0a0a0a, 0xdeadbeef, 0x0a0a0a0a )
    TEST_AMO_DEST_BYP( 1, amo.xchg, tdata_3, 0x0a0a0a0a, 0xdeadbeef, 0x0a0a0a0a )
    TEST_AMO_DEST_BYP( 2, amo.xchg, tdata_3, 0x0b0b0b0b, 0x0a0a0a0a, 0x0b0b0b0b )
    TEST_AMO_DEST_BYP( 3, amo.xchg, tdata_3, 0x0c0c0c0c, 0x0b0b0b0b, 0x0c0c0c0c )
    TEST_AMO_DEST_BYP( 4, amo.xchg, tdata_3, 0x0d0d0d0d, 0x0c0c0c0c, 0x0d0d0d0d )

    //--------------------------------------------------------------------
    // Source bypassing tests
    //--------------------------------------------------------------------

    TEST_AMO_SRC01_BYP( 0, 0, amo.xchg, tdata_4, 0x0a0a0a0a, 0xdeadbeef, 0x0a0a0a0a )
    TEST_AMO_SRC01_BYP( 0, 1, amo.xchg, tdata_5, 0x0a0a0a0a, 0xdeadbeef, 0x0a0a0a0a )
    TEST_AMO_SRC01_BYP( 0, 2, amo.xchg, tdata_5, 0x0b0b0b0b, 0x0a0a0a0a, 0x0b0b0b0b )
    TEST_AMO_SRC01_BYP( 0, 3, amo.xchg, tdata_5, 0x0c0c0c0c, 0x0b0b0b0b, 0x0c0c0c0c )
    TEST_AMO_SRC01_BYP( 0, 4, amo.xchg, tdata_5, 0x0d0d0d0d, 0x0c0c0c0c, 0x0d0d0d0d )

    TEST_AMO_SRC01_BYP( 1, 0, amo.xchg, tdata_6, 0x0e0e0e0e, 0xdeadbeef, 0x0e0e0e0e )
    TEST_AMO_SRC01_BYP( 1, 1, amo.xchg, tdata_6, 0x0f0f0f0f, 0x0e0e0e0e, 0x0f0f0f0f )

    TEST_AMO_SRC10_BYP( 0, 0, amo.xchg, tdata_7, 0x0a0a0a0a, 0xdeadbeef, 0x0a0a0a0a )
    TEST_AMO_SRC10_BYP( 0, 1, amo.xchg, tdata_8, 0x0a0a0a0a, 0xdeadbeef, 0x0a0a0a0a )
    TEST_AMO_SRC10_BYP( 0, 2, amo.xchg, tdata_8, 0x0b0b0b0b, 0x0a0a0a0a, 0x0b0b0b0b )
    TEST_AMO_SRC10_BYP( 0, 3, amo.xchg, tdata_8, 0x0c0c0c0c, 0x0b0b0b0b, 0x0c0c0c0c )
    TEST_AMO_SRC10_BYP( 0, 4, amo.xchg, tdata_8, 0x0d0d0d0d, 0x0c0c0c0c, 0x0d0d0d0d )

    TEST_AMO_SRC10_BYP( 1, 0, amo.xchg, tdata_9, 0x0e0e0e0e, 0xdeadbeef, 0x0e0e0e0e )
    TEST_AMO_SRC10_BYP( 1, 1, amo.xchg, tdata_9, 0x0f0f0f0f, 0x0e0e0e0e, 0x0f0f0f0f )

    TEST_PARC_END

    //--------------------------------------------------------------------
    // Test data
    //--------------------------------------------------------------------

    .data
    .align

tdata_0: .word 0xdeadbeef
tdata_1: .word 0xdeadbeef
tdata_2: .word 0xdeadbeef
tdata_3: .word 0xdeadbeef
tdata_4: .word 0xdeadbeef
tdata_5: .word 0xdeadbeef
tdata_6: .word 0xdeadbeef
tdata_7: .word 0xdeadbeef
tdata_8: .word 0xdeadbeef
tdata_9: .word 0xdeadbeef
