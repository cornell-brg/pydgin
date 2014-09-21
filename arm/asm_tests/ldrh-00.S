#include "arm-macros.h"
TEST_BEGIN

tdata_0: .word 0x00010101

ldr r4, =tdata_0
ldrh r5, [r4]

TEST_END
