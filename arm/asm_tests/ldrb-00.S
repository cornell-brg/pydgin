#include "arm-macros.h"
TEST_BEGIN

tdata_0: .word 0x0F0F0F0F

ldr r4, =tdata_0
ldrb r5, [r4]

TEST_END
