//========================================================================
// mt-beq
//========================================================================

#include "mt-macros.h"

    TEST_MT_BEGIN

    //--------------------------------------------------------------------
    // Branch tests
    //--------------------------------------------------------------------

    TEST_BR2_OP_TAKEN( beq,  0,  0 )
    TEST_BR2_OP_TAKEN( beq,  1,  1 )
    TEST_BR2_OP_TAKEN( beq, -1, -1 )

    TEST_BR2_OP_NOTTAKEN( beq,  0,  1 )
    TEST_BR2_OP_NOTTAKEN( beq,  1,  0 )
    TEST_BR2_OP_NOTTAKEN( beq, -1,  1 )
    TEST_BR2_OP_NOTTAKEN( beq,  1, -1 )

    //--------------------------------------------------------------------
    // Bypassing tests
    //--------------------------------------------------------------------

    TEST_BR2_SRC01_BYP( 0, 0, beq, 0, -1 )
    TEST_BR2_SRC01_BYP( 0, 1, beq, 0, -1 )
    TEST_BR2_SRC01_BYP( 0, 2, beq, 0, -1 )
    TEST_BR2_SRC01_BYP( 0, 3, beq, 0, -1 )
    TEST_BR2_SRC01_BYP( 0, 4, beq, 0, -1 )

    TEST_BR2_SRC01_BYP( 1, 0, beq, 0, -1 )
    TEST_BR2_SRC01_BYP( 1, 1, beq, 0, -1 )
    TEST_BR2_SRC01_BYP( 2, 0, beq, 0, -1 )

    TEST_BR2_SRC01_BYP( 0, 0, beq, 0, -1 )
    TEST_BR2_SRC01_BYP( 0, 1, beq, 0, -1 )
    TEST_BR2_SRC01_BYP( 0, 2, beq, 0, -1 )
    TEST_BR2_SRC01_BYP( 0, 3, beq, 0, -1 )
    TEST_BR2_SRC01_BYP( 0, 4, beq, 0, -1 )

    TEST_BR2_SRC01_BYP( 1, 0, beq, 0, -1 )
    TEST_BR2_SRC01_BYP( 1, 1, beq, 0, -1 )
    TEST_BR2_SRC01_BYP( 2, 0, beq, 0, -1 )

    TEST_MT_END

