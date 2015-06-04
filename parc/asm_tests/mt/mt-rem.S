//========================================================================
// mt-rem.S
//========================================================================
// Not sure what is the "right" thing to do for negative operands.

#include "mt-macros.h"

    TEST_MT_BEGIN

    //--------------------------------------------------------------------
    // Arithmetic tests
    //--------------------------------------------------------------------

    // Zero and one operands

    TEST_RR_OP( rem,  0,  1, 0 )
    TEST_RR_OP( rem,  1,  1, 0 )

    // Positive evenly-divisible operands

    TEST_RR_OP( rem,       546,    42, 0 )
    TEST_RR_OP( rem,     63724,   716, 0 )
    TEST_RR_OP( rem, 167882820, 20154, 0 )

    // Positive not evenly-divisible operands

    TEST_RR_OP( rem,        50,   546,    50 )
    TEST_RR_OP( rem,       546,    50,    46 )
    TEST_RR_OP( rem,     63724,   793,   284 )
    TEST_RR_OP( rem, 167882820, 20150, 13170 )

    //--------------------------------------------------------------------
    // Source/Destination tests
    //--------------------------------------------------------------------

    TEST_RR_SRC0_EQ_DEST( rem, 143, 10, 3 )
    TEST_RR_SRC1_EQ_DEST( rem, 154, 10, 4 )
    TEST_RR_SRC0_EQ_SRC1( rem, 15, 0 )
    TEST_RR_SRCS_EQ_DEST( rem, 16, 0 )

    //--------------------------------------------------------------------
    // Bypassing tests
    //--------------------------------------------------------------------

    TEST_RR_DEST_BYP( 0, rem, 143, 10, 3 )
    TEST_RR_DEST_BYP( 1, rem, 154, 10, 4 )
    TEST_RR_DEST_BYP( 2, rem, 165, 10, 5 )
    TEST_RR_DEST_BYP( 3, rem, 176, 10, 6 )
    TEST_RR_DEST_BYP( 4, rem, 187, 10, 7 )

    TEST_RR_SRC01_BYP( 0, 0, rem, 143, 10, 3 )
    TEST_RR_SRC01_BYP( 0, 1, rem, 154, 10, 4 )
    TEST_RR_SRC01_BYP( 0, 2, rem, 165, 10, 5 )
    TEST_RR_SRC01_BYP( 0, 3, rem, 176, 10, 6 )
    TEST_RR_SRC01_BYP( 0, 4, rem, 187, 10, 7 )

    TEST_RR_SRC01_BYP( 1, 0, rem, 143, 10, 3 )
    TEST_RR_SRC01_BYP( 1, 1, rem, 154, 10, 4 )
    TEST_RR_SRC01_BYP( 2, 0, rem, 165, 10, 5 )

    TEST_RR_SRC10_BYP( 0, 0, rem, 143, 10, 3 )
    TEST_RR_SRC10_BYP( 0, 1, rem, 154, 10, 4 )
    TEST_RR_SRC10_BYP( 0, 2, rem, 165, 10, 5 )
    TEST_RR_SRC10_BYP( 0, 3, rem, 176, 10, 6 )
    TEST_RR_SRC10_BYP( 0, 4, rem, 187, 10, 7 )

    TEST_RR_SRC10_BYP( 1, 0, rem, 143, 10, 3 )
    TEST_RR_SRC10_BYP( 1, 1, rem, 154, 10, 4 )
    TEST_RR_SRC10_BYP( 2, 0, rem, 165, 10, 5 )

    TEST_MT_END

