#include "arm-macros.h"
TEST_BEGIN

tdata_0: .word 0x000000ff
tdata_1: .word 0x00000ff0

ldr r4, =tdata_1
ldr r5, [r4, #-4]

TEST_END
