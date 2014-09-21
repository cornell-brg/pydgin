#include "arm-macros.h"
TEST_BEGIN

/* MLA{S}{cond} Rd, Rn, Rm, Ra
 *
 * The MLA instruction multiplies the values from Rn and Rm, 
 * adds the value from Ra, and places the least significant 
 * 32 bits of the result in Rd.
*/

mov r1, #0x00001000
mov r2, #0x00010000
mov r5, #0x80000000
mlas r9, r1, r2, r5

TEST_END
