#include "arm-macros.h"
TEST_BEGIN

tdata_0: .word 0x000000ff

ldr r4, =tdata_0
mov r5, #0x10000000
strb r5, [r4]
ldr r6, [r4]

TEST_END
