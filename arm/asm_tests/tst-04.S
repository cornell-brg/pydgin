#include "arm-macros.h"
TEST_BEGIN

mov r2, #0xbf000000
orr r2, #0x00e80000
orr r2, #0x0000b800
orr r2, #0x00000060
tst r2, #3

TEST_END
