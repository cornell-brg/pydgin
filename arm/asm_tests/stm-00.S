#include "arm-macros.h"
TEST_BEGIN

tdata_0: .word 0x000000ff

ldr r4, =tdata_0
mov r5, #1
mov r6, #2
stm r4, {r5, r6}
ldm r4, {r8, r9}

TEST_END
