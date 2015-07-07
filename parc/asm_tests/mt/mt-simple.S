//========================================================================
// mt-simple.S
//========================================================================
// We want to make sure our basic test macros are working.

#include "mt-macros.h"

    TEST_MT_BEGIN

    //--------------------------------------------------------------------
    // 1 + 1 = 2
    //--------------------------------------------------------------------
    // You can try forcing a failure by changing the expected value in
    // the following two TEST_CHECK_EQ macros. Try making one, the
    // other, and both fail and observe which line number is reported as
    // failing.

    li    $2, 1
    addiu $3, $2, 1

    mfc0  $10, $c0_coreid
    bne   $10, $0, notcore0

    TEST_CHECK_EQ( $3, 2 )

    j converge

notcore0:

    TEST_CHECK_EQ( $3, 2 )

converge:

    //--------------------------------------------------------------------
    // 1 + 2 = 3
    //--------------------------------------------------------------------

    li    $2, 1
    addiu $3, $2, 2
    TEST_CHECK_EQ( $3, 3 )

    TEST_MT_END

