#include "arm-macros.h"
TEST_BEGIN

/*LDMDA:Decrement address After each transfer*/
tdata_0: .word 0x00000001
tdata_1: .word 0x00000002
tdata_2: .word 0x00000003

ldr r4, =tdata_2
ldmdb r4!, {r5, r6}

TEST_END
