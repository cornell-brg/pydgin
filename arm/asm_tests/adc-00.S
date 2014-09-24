#include "arm-macros.h"
TEST_BEGIN

mov  r2, #1
mov  r3, #1
mov  r4, #0
adc  r4, r2, r3

TEST_END
