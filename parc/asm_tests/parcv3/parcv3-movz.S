//========================================================================
// parcv3-movz.S
//========================================================================

#include "parc-macros.h"

    TEST_PARC_BEGIN

    li $2, 1
    li $3, 0xdeadbeef
    li $4, 0xffffffff
    movz $4, $3, $2
    TEST_CHECK_EQ( $4, 0xffffffff )

    li $2, 0
    movz $4, $3, $2
    TEST_CHECK_EQ( $4, 0xdeadbeef )

    TEST_PARC_END
