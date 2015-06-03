//========================================================================
// parcv3-amo-and.S
//========================================================================

#include "parc-macros.h"

    TEST_PARC_BEGIN

    //--------------------------------------------------------------------
    // Basic tests
    //--------------------------------------------------------------------

    TEST_AMO_OP( amo.and, tdata_0, 0xffffff00, 0xdeadbeef, 0xdeadbe00 )
    TEST_AMO_OP( amo.and, tdata_0, 0xffff00ff, 0xdeadbe00, 0xdead0000 )
    TEST_AMO_OP( amo.and, tdata_0, 0xff00ffff, 0xdead0000, 0xde000000 )
    TEST_AMO_OP( amo.and, tdata_0, 0x00ffffff, 0xde000000, 0x00000000 )

    TEST_AMO_OP( amo.and, tdata_1, 0xf0f0f0f0, 0xdeadbeef, 0xd0a0b0e0 )
    TEST_AMO_OP( amo.and, tdata_1, 0x0f0f0f0f, 0xd0a0b0e0, 0x00000000 )

    //--------------------------------------------------------------------
    // Destination bypassing tests
    //--------------------------------------------------------------------

    TEST_AMO_DEST_BYP( 0, amo.and, tdata_2, 0xf0f0f0f0, 0xdeadbeef, 0xd0a0b0e0 )
    TEST_AMO_DEST_BYP( 1, amo.and, tdata_3, 0xffffff00, 0xdeadbeef, 0xdeadbe00 )
    TEST_AMO_DEST_BYP( 2, amo.and, tdata_3, 0xffff00ff, 0xdeadbe00, 0xdead0000 )
    TEST_AMO_DEST_BYP( 3, amo.and, tdata_3, 0xff00ffff, 0xdead0000, 0xde000000 )
    TEST_AMO_DEST_BYP( 4, amo.and, tdata_3, 0x00ffffff, 0xde000000, 0x00000000 )

    //--------------------------------------------------------------------
    // Source bypassing tests
    //--------------------------------------------------------------------

    TEST_AMO_SRC01_BYP( 0, 0, amo.and, tdata_4, 0xf0f0f0f0, 0xdeadbeef, 0xd0a0b0e0 )
    TEST_AMO_SRC01_BYP( 0, 1, amo.and, tdata_5, 0xffffff00, 0xdeadbeef, 0xdeadbe00 )
    TEST_AMO_SRC01_BYP( 0, 2, amo.and, tdata_5, 0xffff00ff, 0xdeadbe00, 0xdead0000 )
    TEST_AMO_SRC01_BYP( 0, 3, amo.and, tdata_5, 0xff00ffff, 0xdead0000, 0xde000000 )
    TEST_AMO_SRC01_BYP( 0, 4, amo.and, tdata_5, 0x00ffffff, 0xde000000, 0x00000000 )

    TEST_AMO_SRC01_BYP( 1, 0, amo.and, tdata_6, 0xf0f0f0f0, 0xdeadbeef, 0xd0a0b0e0 )
    TEST_AMO_SRC01_BYP( 1, 1, amo.and, tdata_6, 0x0f0f0f0f, 0xd0a0b0e0, 0x00000000 )

    TEST_AMO_SRC10_BYP( 0, 0, amo.and, tdata_7, 0xf0f0f0f0, 0xdeadbeef, 0xd0a0b0e0 )
    TEST_AMO_SRC10_BYP( 0, 1, amo.and, tdata_8, 0xffffff00, 0xdeadbeef, 0xdeadbe00 )
    TEST_AMO_SRC10_BYP( 0, 2, amo.and, tdata_8, 0xffff00ff, 0xdeadbe00, 0xdead0000 )
    TEST_AMO_SRC10_BYP( 0, 3, amo.and, tdata_8, 0xff00ffff, 0xdead0000, 0xde000000 )
    TEST_AMO_SRC10_BYP( 0, 4, amo.and, tdata_8, 0x00ffffff, 0xde000000, 0x00000000 )

    TEST_AMO_SRC10_BYP( 1, 0, amo.and, tdata_9, 0xf0f0f0f0, 0xdeadbeef, 0xd0a0b0e0 )
    TEST_AMO_SRC10_BYP( 1, 1, amo.and, tdata_9, 0x0f0f0f0f, 0xd0a0b0e0, 0x00000000 )

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
