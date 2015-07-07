//========================================================================
// parcv3-amo-or.S
//========================================================================

#include "parc-macros.h"

    TEST_PARC_BEGIN

    //--------------------------------------------------------------------
    // Basic tests
    //--------------------------------------------------------------------

    TEST_AMO_OP( amo.or, tdata_0, 0x000000ff, 0xdeadbeef, 0xdeadbeff )
    TEST_AMO_OP( amo.or, tdata_0, 0x0000ff00, 0xdeadbeff, 0xdeadffff )
    TEST_AMO_OP( amo.or, tdata_0, 0x00ff0000, 0xdeadffff, 0xdeffffff )
    TEST_AMO_OP( amo.or, tdata_0, 0xff000000, 0xdeffffff, 0xffffffff )

    TEST_AMO_OP( amo.or, tdata_1, 0xf0f0f0f0, 0xdeadbeef, 0xfefdfeff )
    TEST_AMO_OP( amo.or, tdata_1, 0x0f0f0f0f, 0xfefdfeff, 0xffffffff )

    //--------------------------------------------------------------------
    // Destination bypassing tests
    //--------------------------------------------------------------------

    TEST_AMO_DEST_BYP( 0, amo.or, tdata_2, 0xf0f0f0f0, 0xdeadbeef, 0xfefdfeff )
    TEST_AMO_DEST_BYP( 1, amo.or, tdata_3, 0x000000ff, 0xdeadbeef, 0xdeadbeff )
    TEST_AMO_DEST_BYP( 2, amo.or, tdata_3, 0x0000ff00, 0xdeadbeff, 0xdeadffff )
    TEST_AMO_DEST_BYP( 3, amo.or, tdata_3, 0x00ff0000, 0xdeadffff, 0xdeffffff )
    TEST_AMO_DEST_BYP( 4, amo.or, tdata_3, 0xff000000, 0xdeffffff, 0xffffffff )

    //--------------------------------------------------------------------
    // Source bypassing tests
    //--------------------------------------------------------------------

    TEST_AMO_SRC01_BYP( 0, 0, amo.or, tdata_4, 0xf0f0f0f0, 0xdeadbeef, 0xfefdfeff )
    TEST_AMO_SRC01_BYP( 0, 1, amo.or, tdata_5, 0x000000ff, 0xdeadbeef, 0xdeadbeff )
    TEST_AMO_SRC01_BYP( 0, 2, amo.or, tdata_5, 0x0000ff00, 0xdeadbeff, 0xdeadffff )
    TEST_AMO_SRC01_BYP( 0, 3, amo.or, tdata_5, 0x00ff0000, 0xdeadffff, 0xdeffffff )
    TEST_AMO_SRC01_BYP( 0, 4, amo.or, tdata_5, 0xff000000, 0xdeffffff, 0xffffffff )

    TEST_AMO_SRC01_BYP( 1, 0, amo.or, tdata_6, 0xf0f0f0f0, 0xdeadbeef, 0xfefdfeff )
    TEST_AMO_SRC01_BYP( 1, 1, amo.or, tdata_6, 0x0f0f0f0f, 0xfefdfeff, 0xffffffff )

    TEST_AMO_SRC10_BYP( 0, 0, amo.or, tdata_7, 0xf0f0f0f0, 0xdeadbeef, 0xfefdfeff )
    TEST_AMO_SRC10_BYP( 0, 1, amo.or, tdata_8, 0x000000ff, 0xdeadbeef, 0xdeadbeff )
    TEST_AMO_SRC10_BYP( 0, 2, amo.or, tdata_8, 0x0000ff00, 0xdeadbeff, 0xdeadffff )
    TEST_AMO_SRC10_BYP( 0, 3, amo.or, tdata_8, 0x00ff0000, 0xdeadffff, 0xdeffffff )
    TEST_AMO_SRC10_BYP( 0, 4, amo.or, tdata_8, 0xff000000, 0xdeffffff, 0xffffffff )

    TEST_AMO_SRC10_BYP( 1, 0, amo.or, tdata_9, 0xf0f0f0f0, 0xdeadbeef, 0xfefdfeff )
    TEST_AMO_SRC10_BYP( 1, 1, amo.or, tdata_9, 0x0f0f0f0f, 0xfefdfeff, 0xffffffff )

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

