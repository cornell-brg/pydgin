#include "arm-macros.h"
TEST_BEGIN

mov r1, #1
movs r2, #8
sublts r1, r1, r2

TEST_END
