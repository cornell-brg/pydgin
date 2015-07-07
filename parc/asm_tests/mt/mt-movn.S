//========================================================================
// mt-movn.S
//========================================================================

#include "mt-macros.h"

    TEST_MT_BEGIN

    //--------------------------------------------------------------------
    // Basic tests
    //--------------------------------------------------------------------

    TEST_CMOV_OP( movn,  0,  0,  0,  0 )
    TEST_CMOV_OP( movn,  1,  2,  0,  1 )
    TEST_CMOV_OP( movn,  1,  2,  1,  2 )
    TEST_CMOV_OP( movn,  3,  4, -1,  4 )
    TEST_CMOV_OP( movn, -1, -2,  0, -1 )
    TEST_CMOV_OP( movn, -1, -2,  1, -2 )
    TEST_CMOV_OP( movn, -3, -4, -1, -4 )

    //--------------------------------------------------------------------
    // Source/Destination tests
    //--------------------------------------------------------------------

    TEST_CMOV_SRC0_EQ_DEST( movn, 0, 0, 0 )
    TEST_CMOV_SRC0_EQ_DEST( movn, 1, 0, 1 )
    TEST_CMOV_SRC0_EQ_DEST( movn, 2, 1, 2 )
    TEST_CMOV_SRC0_EQ_DEST( movn, 3, 2, 3 )
    TEST_CMOV_SRC0_EQ_DEST( movn, 4, 0, 4 )

    TEST_CMOV_SRC1_EQ_DEST( movn, 0, 0, 0 )
    TEST_CMOV_SRC1_EQ_DEST( movn, 1, 0, 0 )
    TEST_CMOV_SRC1_EQ_DEST( movn, 2, 1, 2 )
    TEST_CMOV_SRC1_EQ_DEST( movn, 3, 2, 3 )
    TEST_CMOV_SRC1_EQ_DEST( movn, 4, 3, 4 )

    TEST_CMOV_SRCS_EQ_DEST( movn, 0, 0 )
    TEST_CMOV_SRCS_EQ_DEST( movn, 1, 1 )
    TEST_CMOV_SRCS_EQ_DEST( movn, 2, 2 )
    TEST_CMOV_SRCS_EQ_DEST( movn, 3, 3 )

    //--------------------------------------------------------------------
    // Bypassing tests
    //--------------------------------------------------------------------

    TEST_CMOV_DEST_BYP( 0, movn, 13, 24, 0, 13 )
    TEST_CMOV_DEST_BYP( 1, movn, 14, 25, 1, 25 )
    TEST_CMOV_DEST_BYP( 2, movn, 15, 26, 0, 15 )
    TEST_CMOV_DEST_BYP( 3, movn, 16, 27, 1, 27 )
    TEST_CMOV_DEST_BYP( 4, movn, 17, 28, 0, 17 )

    TEST_CMOV_SRC01_BYP( 0, 0, movn, 13, 24, 0, 13 )
    TEST_CMOV_SRC01_BYP( 0, 1, movn, 14, 25, 1, 25 )
    TEST_CMOV_SRC01_BYP( 0, 2, movn, 15, 26, 0, 15 )
    TEST_CMOV_SRC01_BYP( 0, 3, movn, 16, 27, 1, 27 )
    TEST_CMOV_SRC01_BYP( 0, 4, movn, 17, 28, 0, 17 )

    TEST_CMOV_SRC01_BYP( 1, 0, movn, 13, 24, 0, 13 )
    TEST_CMOV_SRC01_BYP( 1, 1, movn, 14, 25, 1, 25 )
    TEST_CMOV_SRC01_BYP( 2, 0, movn, 15, 26, 0, 15 )

    TEST_CMOV_SRC10_BYP( 0, 0, movn, 13, 24, 0, 13 )
    TEST_CMOV_SRC10_BYP( 0, 1, movn, 14, 25, 1, 25 )
    TEST_CMOV_SRC10_BYP( 0, 2, movn, 15, 26, 0, 15 )
    TEST_CMOV_SRC10_BYP( 0, 3, movn, 16, 27, 1, 27 )
    TEST_CMOV_SRC10_BYP( 0, 4, movn, 17, 28, 0, 17 )

    TEST_CMOV_SRC10_BYP( 1, 0, movn, 13, 24, 0, 13 )
    TEST_CMOV_SRC10_BYP( 1, 1, movn, 14, 25, 1, 25 )
    TEST_CMOV_SRC10_BYP( 2, 0, movn, 15, 26, 0, 15 )

    TEST_MT_END

