#include "arm-macros.h"
TEST_BEGIN

#arithmetic shift right by immediate
mov r3, #0xf0000000
mov r4, #0x9C000000
cmp r3, r3, ASR #3

TEST_END
