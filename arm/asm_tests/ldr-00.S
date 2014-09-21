#include "arm-macros.h"
TEST_BEGIN

tdata_0: .word 0x000000FF

ldr r4, =tdata_0
ldr r5, [r4, #0]
cmp r5, #0x00000FF

TEST_END
