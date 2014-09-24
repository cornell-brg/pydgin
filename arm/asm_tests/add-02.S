#include "arm-macros.h"
TEST_BEGIN

mov  r1, #0
mov  r3, #0x00100000
mov  lr, #0x0000001f
adds r1, r1, r3, lsl lr

TEST_END
