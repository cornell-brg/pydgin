//=========================================================================
// extensions-gcd.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        // test gcd( 24, 100 ) == 4
        li    $1, 24
        li    $2, 100
        gcd   $3, $2, $1
        li    $4, 4
        TEST_CHECK_EQ( $3, $4 )

        // test gcd( 8, 4 ) == 4
        li    $1, 8
        li    $2, 4
        gcd   $3, $2, $1
        li    $4, 4
        TEST_CHECK_EQ( $3, $4 )

        TEST_PARC_END
