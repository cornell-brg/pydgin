#include "arm-macros.h"
TEST_BEGIN

mov  r1, #0x00100000
mov  r3, #0x00100000
mov  r5, #1
adcs r1, r1, r3, asr r5

TEST_END
