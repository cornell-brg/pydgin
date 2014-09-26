#include "arm-macros.h"
TEST_BEGIN

mov   r2,     #0x83000000
orr   r2, r2, #0x004e0000
orr   r2, r2, #0x00000b00
orr   r2, r2, #0x0000005f
mov   lr,     #0x00007e00
orr   lr, lr, #0x00000056
smull r1, r3, r2, lr

TEST_END
