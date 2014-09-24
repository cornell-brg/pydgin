#include "arm-macros.h"
TEST_BEGIN

<<<<<<< HEAD
mov r4, #1
mov r5, #8
movs r4, r5, LSL #1
=======
#Rotate right with extend, carry = 1
mov r4, #0xFFFFFFFF
cmp r4, #0
mov r3, #0xa000000b
movs r3, r3, RRX
>>>>>>> [arm/asm_tests]data-processing addressing modes tested

TEST_END
