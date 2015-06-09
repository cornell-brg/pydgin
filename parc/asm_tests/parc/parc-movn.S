//========================================================================
// parcv3-movn.S
//========================================================================

#include "parc-macros.h"

    TEST_PARC_BEGIN

    li $2, 0
    li $3, 0xdeadbeef
    li $4, 0xffffffff
    movn $4, $3, $2
    TEST_CHECK_EQ( $4, 0xffffffff )

    li $2, 1
    movn $4, $3, $2
    TEST_CHECK_EQ( $4, 0xdeadbeef )

    TEST_PARC_END
