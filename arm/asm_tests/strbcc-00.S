#include "arm-macros.h"
TEST_BEGIN

tdata_0: .word 0x10000000

ldr r4, =tdata_0
mov r5, #0xff
strccb r5, [r4]
ldr r6, [r4]

TEST_END
