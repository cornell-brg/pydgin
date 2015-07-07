//========================================================================
// mt-bne
//========================================================================

#include "mt-macros.h"

    TEST_MT_BEGIN

    //--------------------------------------------------------------------
    // Branch tests
    //--------------------------------------------------------------------

    TEST_BR2_OP_TAKEN( bne,  0,  1 )
    TEST_BR2_OP_TAKEN( bne,  1,  0 )
    TEST_BR2_OP_TAKEN( bne, -1,  1 )
    TEST_BR2_OP_TAKEN( bne,  1, -1 )

    TEST_BR2_OP_NOTTAKEN( bne,  0,  0 )
    TEST_BR2_OP_NOTTAKEN( bne,  1,  1 )
    TEST_BR2_OP_NOTTAKEN( bne, -1, -1 )

    //--------------------------------------------------------------------
    // Bypassing tests
    //--------------------------------------------------------------------

    TEST_BR2_SRC01_BYP( 0, 0, bne, 0, 0 )
    TEST_BR2_SRC01_BYP( 0, 1, bne, 0, 0 )
    TEST_BR2_SRC01_BYP( 0, 2, bne, 0, 0 )
    TEST_BR2_SRC01_BYP( 0, 3, bne, 0, 0 )
    TEST_BR2_SRC01_BYP( 0, 4, bne, 0, 0 )

    TEST_BR2_SRC01_BYP( 1, 0, bne, 0, 0 )
    TEST_BR2_SRC01_BYP( 1, 1, bne, 0, 0 )
    TEST_BR2_SRC01_BYP( 2, 0, bne, 0, 0 )

    TEST_BR2_SRC01_BYP( 0, 0, bne, 0, 0 )
    TEST_BR2_SRC01_BYP( 0, 1, bne, 0, 0 )
    TEST_BR2_SRC01_BYP( 0, 2, bne, 0, 0 )
    TEST_BR2_SRC01_BYP( 0, 3, bne, 0, 0 )
    TEST_BR2_SRC01_BYP( 0, 4, bne, 0, 0 )

    TEST_BR2_SRC01_BYP( 1, 0, bne, 0, 0 )
    TEST_BR2_SRC01_BYP( 1, 1, bne, 0, 0 )
    TEST_BR2_SRC01_BYP( 2, 0, bne, 0, 0 )

    TEST_MT_END

