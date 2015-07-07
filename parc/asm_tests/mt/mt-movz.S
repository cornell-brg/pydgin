//========================================================================
// mt-movz.S
//========================================================================

#include "mt-macros.h"

    TEST_MT_BEGIN

    //--------------------------------------------------------------------
    // Basic tests
    //--------------------------------------------------------------------

    TEST_CMOV_OP( movz,  0,  0,  0,  0 )
    TEST_CMOV_OP( movz,  1,  2,  0,  2 )
    TEST_CMOV_OP( movz,  1,  2,  1,  1 )
    TEST_CMOV_OP( movz,  3,  4, -1,  3 )
    TEST_CMOV_OP( movz, -1, -2,  0, -2 )
    TEST_CMOV_OP( movz, -1, -2,  1, -1 )
    TEST_CMOV_OP( movz, -3, -4, -1, -3 )

    //--------------------------------------------------------------------
    // Source/Destination tests
    //--------------------------------------------------------------------

    TEST_CMOV_SRC0_EQ_DEST( movz, 0, 0, 0 )
    TEST_CMOV_SRC0_EQ_DEST( movz, 1, 0, 1 )
    TEST_CMOV_SRC0_EQ_DEST( movz, 2, 1, 2 )
    TEST_CMOV_SRC0_EQ_DEST( movz, 3, 2, 3 )
    TEST_CMOV_SRC0_EQ_DEST( movz, 4, 0, 4 )

    TEST_CMOV_SRC1_EQ_DEST( movz, 0, 0, 0 )
    TEST_CMOV_SRC1_EQ_DEST( movz, 1, 0, 1 )
    TEST_CMOV_SRC1_EQ_DEST( movz, 2, 1, 1 )
    TEST_CMOV_SRC1_EQ_DEST( movz, 3, 2, 2 )
    TEST_CMOV_SRC1_EQ_DEST( movz, 4, 3, 3 )

    TEST_CMOV_SRCS_EQ_DEST( movz, 0, 0 )
    TEST_CMOV_SRCS_EQ_DEST( movz, 1, 1 )
    TEST_CMOV_SRCS_EQ_DEST( movz, 2, 2 )
    TEST_CMOV_SRCS_EQ_DEST( movz, 3, 3 )

    //--------------------------------------------------------------------
    // Bypassing tests
    //--------------------------------------------------------------------

    TEST_CMOV_DEST_BYP( 0, movz, 13, 24, 0, 24 );
    TEST_CMOV_DEST_BYP( 1, movz, 14, 25, 1, 14 );
    TEST_CMOV_DEST_BYP( 2, movz, 15, 26, 0, 26 );
    TEST_CMOV_DEST_BYP( 3, movz, 16, 27, 1, 16 );
    TEST_CMOV_DEST_BYP( 4, movz, 17, 28, 0, 28 );

    TEST_CMOV_SRC01_BYP( 0, 0, movz, 13, 24, 0, 24 );
    TEST_CMOV_SRC01_BYP( 0, 1, movz, 14, 25, 1, 14 );
    TEST_CMOV_SRC01_BYP( 0, 2, movz, 15, 26, 0, 26 );
    TEST_CMOV_SRC01_BYP( 0, 3, movz, 16, 27, 1, 16 );
    TEST_CMOV_SRC01_BYP( 0, 4, movz, 17, 28, 0, 28 );

    TEST_CMOV_SRC01_BYP( 1, 0, movz, 13, 24, 0, 24 );
    TEST_CMOV_SRC01_BYP( 1, 1, movz, 14, 25, 1, 14 );
    TEST_CMOV_SRC01_BYP( 2, 0, movz, 15, 26, 0, 26 );

    TEST_CMOV_SRC10_BYP( 0, 0, movz, 13, 24, 0, 24 );
    TEST_CMOV_SRC10_BYP( 0, 1, movz, 14, 25, 1, 14 );
    TEST_CMOV_SRC10_BYP( 0, 2, movz, 15, 26, 0, 26 );
    TEST_CMOV_SRC10_BYP( 0, 3, movz, 16, 27, 1, 16 );
    TEST_CMOV_SRC10_BYP( 0, 4, movz, 17, 28, 0, 28 );

    TEST_CMOV_SRC10_BYP( 1, 0, movz, 13, 24, 0, 24 );
    TEST_CMOV_SRC10_BYP( 1, 1, movz, 14, 25, 1, 14 );
    TEST_CMOV_SRC10_BYP( 2, 0, movz, 15, 26, 0, 26 );

    TEST_MT_END

