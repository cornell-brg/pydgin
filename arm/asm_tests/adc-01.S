#include "arm-macros.h"
TEST_BEGIN

mov  r2, #1
mov  r3, #1

# Set the carry bit
mov  r0, #0xa000000b
movs r0, r0, RRX

adc  r4, r2, r3

TEST_END
