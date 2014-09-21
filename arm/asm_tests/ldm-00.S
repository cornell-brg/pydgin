#include "arm-macros.h"
TEST_BEGIN

/*LDM in default is LDMIA.*/
tdata_0: .word 0x00000001
tdata_1: .word 0x00000002

ldr r4, =tdata_0
ldm r4, {r5, r6}

TEST_END
