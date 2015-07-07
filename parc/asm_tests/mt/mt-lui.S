//========================================================================
// mt-lui
//========================================================================

#include "mt-macros.h"

    TEST_MT_BEGIN

    //--------------------------------------------------------------------
    // Basic tests
    //--------------------------------------------------------------------

    lui $2, 0x0000
    TEST_CHECK_EQ( $2, 0x00000000 )

    lui $2, 0xffff
    TEST_CHECK_EQ( $2, 0xffff0000 )

    lui $2, 0x7fff
    TEST_CHECK_EQ( $2, 0x7fff0000 )

    lui $2, 0x8000
    TEST_CHECK_EQ( $2, 0x80000000 )

    //--------------------------------------------------------------------
    // Bypassing tests
    //--------------------------------------------------------------------

    lui   $2, 0xdead
    addiu $7, $2, 0
    TEST_CHECK_EQ( $7, 0xdead0000 )

    lui   $2, 0xeadd
    TEST_INSERT_NOPS( 1 )
    addiu $7, $2, 0
    TEST_CHECK_EQ( $7, 0xeadd0000 )

    lui   $2, 0xadde
    TEST_INSERT_NOPS( 2 )
    addiu $7, $2, 0
    TEST_CHECK_EQ( $7, 0xadde0000 )

    lui   $2, 0xddea
    TEST_INSERT_NOPS( 3 )
    addiu $7, $2, 0
    TEST_CHECK_EQ( $7, 0xddea0000 )

    lui   $2, 0xdead
    TEST_INSERT_NOPS( 4 )
    addiu $7, $2, 0
    TEST_CHECK_EQ( $7, 0xdead0000 )

    TEST_MT_END

