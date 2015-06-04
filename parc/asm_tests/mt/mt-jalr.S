//========================================================================
// mt-jalr
//========================================================================

#include "mt-macros.h"

    TEST_MT_BEGIN

    //--------------------------------------------------------------------
    // Basic test
    //--------------------------------------------------------------------

    li   $31, 0xdeadbeef
    la   $3, 1f

    jalr $4, $3
linkaddr_0:
    TEST_CHECK_FAIL
1:

    la $2, linkaddr_0
    TEST_CHECK_EQ( $4, $2 )

    // Make sure $31 not overwritten
    TEST_CHECK_EQ( $31, 0xdeadbeef )

    //--------------------------------------------------------------------
    // Check $0 link destination
    //--------------------------------------------------------------------

    li   $31, 0xdeadbeef
    la   $3, 1f

    jalr $0, $3
    TEST_CHECK_FAIL
1:

    // Make sure $31 not overwritten
    TEST_CHECK_EQ( $31, 0xdeadbeef )

    //--------------------------------------------------------------------
    // Bypassing tests
    //--------------------------------------------------------------------

    TEST_JR_SRC0_BYP( 0, jalr )
    TEST_JR_SRC0_BYP( 1, jalr )
    TEST_JR_SRC0_BYP( 2, jalr )
    TEST_JR_SRC0_BYP( 3, jalr )
    TEST_JR_SRC0_BYP( 4, jalr )

    TEST_MT_END

