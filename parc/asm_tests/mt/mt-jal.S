//========================================================================
// mt-jal
//========================================================================

#include "mt-macros.h"

    TEST_MT_BEGIN

    jal 1f
linkaddr_0:
    TEST_CHECK_FAIL
1:

    la $2, linkaddr_0
    TEST_CHECK_EQ( $31, $2 )

    TEST_MT_END

