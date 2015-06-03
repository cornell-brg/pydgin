//========================================================================
// parcv3-amo-and.S
//========================================================================

#include "parc-macros.h"

    TEST_PARC_BEGIN

    //--------------------------------------------------------------------
    // Basic tests
    //--------------------------------------------------------------------

    TEST_AMO_OP( amo.add, tdata_0, 0xffff8000, 0x80000000, 0x7fff8000 )
    TEST_AMO_OP( amo.add, tdata_0, 0x00010000, 0x7fff8000, 0x80008000 )
    TEST_AMO_OP( amo.add, tdata_0, 0x2abc2def, 0x80008000, 0xaabcadef )
    TEST_AMO_OP( amo.add, tdata_0, 0x11111111, 0xaabcadef, 0xbbcdbf00 )
    TEST_AMO_OP( amo.add, tdata_0, 0x80000000, 0xbbcdbf00, 0x3bcdbf00 )

    TEST_AMO_OP( amo.add, tdata_1, 0x00007fff, 0x7fffffff, 0x80007ffe )
    TEST_AMO_OP( amo.add, tdata_1, 0x0000beef, 0x80007ffe, 0x80013eed )

    //--------------------------------------------------------------------
    // Destination bypassing tests
    //--------------------------------------------------------------------

    TEST_AMO_DEST_BYP( 0, amo.add, tdata_2, 0xffff8000, 0x80000000, 0x7fff8000 )
    TEST_AMO_DEST_BYP( 1, amo.add, tdata_2, 0x00010000, 0x7fff8000, 0x80008000 )
    TEST_AMO_DEST_BYP( 2, amo.add, tdata_2, 0x2abc2def, 0x80008000, 0xaabcadef )
    TEST_AMO_DEST_BYP( 3, amo.add, tdata_2, 0x11111111, 0xaabcadef, 0xbbcdbf00 )
    TEST_AMO_DEST_BYP( 4, amo.add, tdata_2, 0x80000000, 0xbbcdbf00, 0x3bcdbf00 )

    //--------------------------------------------------------------------
    // Source bypassing tests
    //--------------------------------------------------------------------

    TEST_AMO_SRC01_BYP( 0, 0, amo.add, tdata_3, 0xffff8000, 0x80000000, 0x7fff8000 )
    TEST_AMO_SRC01_BYP( 0, 1, amo.add, tdata_3, 0x00010000, 0x7fff8000, 0x80008000 )
    TEST_AMO_SRC01_BYP( 0, 2, amo.add, tdata_3, 0x2abc2def, 0x80008000, 0xaabcadef )
    TEST_AMO_SRC01_BYP( 0, 3, amo.add, tdata_3, 0x11111111, 0xaabcadef, 0xbbcdbf00 )
    TEST_AMO_SRC01_BYP( 0, 4, amo.add, tdata_3, 0x80000000, 0xbbcdbf00, 0x3bcdbf00 )

    TEST_AMO_SRC01_BYP( 1, 0, amo.add, tdata_4, 0x00007fff, 0x7fffffff, 0x80007ffe )
    TEST_AMO_SRC01_BYP( 1, 1, amo.add, tdata_4, 0x0000beef, 0x80007ffe, 0x80013eed )

    TEST_AMO_SRC10_BYP( 0, 0, amo.add, tdata_5, 0xffff8000, 0x80000000, 0x7fff8000 )
    TEST_AMO_SRC10_BYP( 0, 1, amo.add, tdata_5, 0x00010000, 0x7fff8000, 0x80008000 )
    TEST_AMO_SRC10_BYP( 0, 2, amo.add, tdata_5, 0x2abc2def, 0x80008000, 0xaabcadef )
    TEST_AMO_SRC10_BYP( 0, 3, amo.add, tdata_5, 0x11111111, 0xaabcadef, 0xbbcdbf00 )
    TEST_AMO_SRC10_BYP( 0, 4, amo.add, tdata_5, 0x80000000, 0xbbcdbf00, 0x3bcdbf00 )

    TEST_AMO_SRC10_BYP( 1, 0, amo.add, tdata_6, 0x00007fff, 0x7fffffff, 0x80007ffe )
    TEST_AMO_SRC10_BYP( 1, 1, amo.add, tdata_6, 0x0000beef, 0x80007ffe, 0x80013eed )

    TEST_PARC_END

    //--------------------------------------------------------------------
    // Test data
    //--------------------------------------------------------------------

    .data
    .align

tdata_0: .word 0x80000000
tdata_1: .word 0x7fffffff
tdata_2: .word 0x80000000
tdata_3: .word 0x80000000
tdata_4: .word 0x7fffffff
tdata_5: .word 0x80000000
tdata_6: .word 0x7fffffff
