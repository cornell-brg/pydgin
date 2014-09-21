#include "arm-macros.h"
TEST_BEGIN

tdata_0: .word 0x000000ff
tdata_1: .word 0x00000ff0
tdata_2: .word 0x0000ff00

ldr r4, =tdata_0
mov r6, #8
ldr r5, [r4, r6]

TEST_END
