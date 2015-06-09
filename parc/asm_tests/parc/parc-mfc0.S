//========================================================================
// parcv2-mfc0.S
//========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //--------------------------------------------------------------------
        // Basic test
        //--------------------------------------------------------------------

        li   $2, 7
        mfc0 $2, $c0_coreid
        TEST_CHECK_EQ( $2, 0x0 )

        //--------------------------------------------------------------------
        // Bypassing tests
        //--------------------------------------------------------------------

        li   $2, 7
        mfc0 $2, $c0_coreid
        addiu $2, 0
        TEST_CHECK_EQ( $2, 0x0 )

        li   $2, 7
        mfc0 $2, $c0_coreid
        TEST_INSERT_NOPS( 1 )
        addiu $2, 0
        TEST_CHECK_EQ( $2, 0x0 )

        li   $2, 7
        mfc0 $2, $c0_coreid
        TEST_INSERT_NOPS( 2 )
        addiu $2, 0
        TEST_CHECK_EQ( $2, 0x0 )

        li   $2, 7
        mfc0 $2, $c0_coreid
        TEST_INSERT_NOPS( 3 )
        addiu $2, 0
        TEST_CHECK_EQ( $2, 0x0 )

        li   $2, 7
        mfc0 $2, $c0_coreid
        TEST_INSERT_NOPS( 4 )
        addiu $2, 0
        TEST_CHECK_EQ( $2, 0x0 )

        TEST_PARC_END
