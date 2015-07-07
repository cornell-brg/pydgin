//========================================================================
// mt-remu.S
//========================================================================
// Not sure what is the "right" thing to do for negative operands.

#include "mt-macros.h"

    TEST_MT_BEGIN

    //--------------------------------------------------------------------
    // Arithmetic tests
    //--------------------------------------------------------------------

    // Zero and one operands

    TEST_RR_OP( remu,  0,  1, 0 )
    TEST_RR_OP( remu,  1,  1, 0 )

    // Positive evenly-divisible operands

    TEST_RR_OP( remu,       546,    42, 0 )
    TEST_RR_OP( remu,     63724,   716, 0 )
    TEST_RR_OP( remu, 167882820, 20154, 0 )

    // Positive not evenly-divisible operands

    TEST_RR_OP( remu,        50,   546,    50 )
    TEST_RR_OP( remu,       546,    50,    46 )
    TEST_RR_OP( remu,     63724,   793,   284 )
    TEST_RR_OP( remu, 167882820, 20150, 13170 )

    //--------------------------------------------------------------------
    // Source/Destination tests
    //--------------------------------------------------------------------

    TEST_RR_SRC0_EQ_DEST( remu, 143, 10, 3 )
    TEST_RR_SRC1_EQ_DEST( remu, 154, 10, 4 )
    TEST_RR_SRC0_EQ_SRC1( remu, 15, 0 )
    TEST_RR_SRCS_EQ_DEST( remu, 16, 0 )

    //--------------------------------------------------------------------
    // Bypassing tests
    //--------------------------------------------------------------------

    TEST_RR_DEST_BYP( 0, remu, 143, 10, 3 )
    TEST_RR_DEST_BYP( 1, remu, 154, 10, 4 )
    TEST_RR_DEST_BYP( 2, remu, 165, 10, 5 )
    TEST_RR_DEST_BYP( 3, remu, 176, 10, 6 )
    TEST_RR_DEST_BYP( 4, remu, 187, 10, 7 )

    TEST_RR_SRC01_BYP( 0, 0, remu, 143, 10, 3 )
    TEST_RR_SRC01_BYP( 0, 1, remu, 154, 10, 4 )
    TEST_RR_SRC01_BYP( 0, 2, remu, 165, 10, 5 )
    TEST_RR_SRC01_BYP( 0, 3, remu, 176, 10, 6 )
    TEST_RR_SRC01_BYP( 0, 4, remu, 187, 10, 7 )

    TEST_RR_SRC01_BYP( 1, 0, remu, 143, 10, 3 )
    TEST_RR_SRC01_BYP( 1, 1, remu, 154, 10, 4 )
    TEST_RR_SRC01_BYP( 2, 0, remu, 165, 10, 5 )

    TEST_RR_SRC10_BYP( 0, 0, remu, 143, 10, 3 )
    TEST_RR_SRC10_BYP( 0, 1, remu, 154, 10, 4 )
    TEST_RR_SRC10_BYP( 0, 2, remu, 165, 10, 5 )
    TEST_RR_SRC10_BYP( 0, 3, remu, 176, 10, 6 )
    TEST_RR_SRC10_BYP( 0, 4, remu, 187, 10, 7 )

    TEST_RR_SRC10_BYP( 1, 0, remu, 143, 10, 3 )
    TEST_RR_SRC10_BYP( 1, 1, remu, 154, 10, 4 )
    TEST_RR_SRC10_BYP( 2, 0, remu, 165, 10, 5 )

    TEST_MT_END

