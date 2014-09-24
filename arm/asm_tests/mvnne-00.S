#include "arm-macros.h"
TEST_BEGIN

mov r2, #7
cmp r2, #6
mvnne r1, r2

TEST_END
