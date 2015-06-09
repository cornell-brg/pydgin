//========================================================================
// parcv3-amo-min.S
//========================================================================

#include "parc-macros.h"

    TEST_PARC_BEGIN

    //--------------------------------------------------------------------
    // Basic tests
    //--------------------------------------------------------------------

    TEST_AMO_OP( amo.min, tdata_0, 0x08888888, 0x09999999, 0x08888888 )
    TEST_AMO_OP( amo.min, tdata_0, 0x0aaaaaaa, 0x08888888, 0x08888888 )
    TEST_AMO_OP( amo.min, tdata_0, 0x08888888, 0x08888888, 0x08888888 )
    TEST_AMO_OP( amo.min, tdata_1, 0xfffffffe, 0xffffffff, 0xfffffffe )
    TEST_AMO_OP( amo.min, tdata_1, 0xffffffff, 0xfffffffe, 0xfffffffe )

    //--------------------------------------------------------------------
    // Destination bypassing tests
    //--------------------------------------------------------------------

    TEST_AMO_DEST_BYP( 0, amo.min, tdata_2, 0x08888888, 0x09999999, 0x08888888 )
    TEST_AMO_DEST_BYP( 1, amo.min, tdata_2, 0x0aaaaaaa, 0x08888888, 0x08888888 )
    TEST_AMO_DEST_BYP( 2, amo.min, tdata_2, 0x08888888, 0x08888888, 0x08888888 )
    TEST_AMO_DEST_BYP( 3, amo.min, tdata_3, 0xfffffffe, 0xffffffff, 0xfffffffe )
    TEST_AMO_DEST_BYP( 4, amo.min, tdata_3, 0xffffffff, 0xfffffffe, 0xfffffffe )

    //--------------------------------------------------------------------
    // Source bypassing tests
    //--------------------------------------------------------------------

    TEST_AMO_SRC01_BYP( 0, 0, amo.min, tdata_4, 0x08888888, 0x09999999, 0x08888888 )
    TEST_AMO_SRC01_BYP( 0, 1, amo.min, tdata_4, 0x0aaaaaaa, 0x08888888, 0x08888888 )
    TEST_AMO_SRC01_BYP( 0, 2, amo.min, tdata_4, 0x08888888, 0x08888888, 0x08888888 )
    TEST_AMO_SRC01_BYP( 0, 3, amo.min, tdata_5, 0xfffffffe, 0xffffffff, 0xfffffffe )
    TEST_AMO_SRC01_BYP( 0, 4, amo.min, tdata_5, 0xffffffff, 0xfffffffe, 0xfffffffe )

    TEST_AMO_SRC01_BYP( 1, 0, amo.min, tdata_6, 0x08888888, 0x09999999, 0x08888888 )
    TEST_AMO_SRC01_BYP( 1, 1, amo.min, tdata_6, 0x0aaaaaaa, 0x08888888, 0x08888888 )

    TEST_AMO_SRC10_BYP( 0, 0, amo.min, tdata_7, 0x08888888, 0x09999999, 0x08888888 )
    TEST_AMO_SRC10_BYP( 0, 1, amo.min, tdata_7, 0x0aaaaaaa, 0x08888888, 0x08888888 )
    TEST_AMO_SRC10_BYP( 0, 2, amo.min, tdata_7, 0x08888888, 0x08888888, 0x08888888 )
    TEST_AMO_SRC10_BYP( 0, 3, amo.min, tdata_8, 0xfffffffe, 0xffffffff, 0xfffffffe )
    TEST_AMO_SRC10_BYP( 0, 4, amo.min, tdata_8, 0xffffffff, 0xfffffffe, 0xfffffffe )

    TEST_AMO_SRC10_BYP( 1, 0, amo.min, tdata_9, 0x08888888, 0x09999999, 0x08888888 )
    TEST_AMO_SRC10_BYP( 1, 1, amo.min, tdata_9, 0x0aaaaaaa, 0x08888888, 0x08888888 )

    TEST_PARC_END

    //--------------------------------------------------------------------
    // Test data
    //--------------------------------------------------------------------

    .data
    .align

tdata_0: .word 0x09999999
tdata_1: .word 0xffffffff
tdata_2: .word 0x09999999
tdata_3: .word 0xffffffff
tdata_4: .word 0x09999999
tdata_5: .word 0xffffffff
tdata_6: .word 0x09999999
tdata_7: .word 0x09999999
tdata_8: .word 0xffffffff
tdata_9: .word 0x09999999
