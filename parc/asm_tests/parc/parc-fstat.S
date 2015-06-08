//------------------------------------------------------------------------
// parcv3-fstat.S
//------------------------------------------------------------------------

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //----------------------------------------------------------------
        // Basic test
        //----------------------------------------------------------------

        li $v0, 9
        li $a0, 1
        la $a1, tdata0
        li $a2, 0
        syscall
        la $t0, tdata0
        lw $t1, 0($t0)
        la $t0, tdata1
        lw $t1, 0($t0)
        la $t0, tdata2
        lw $t1, 0($t0)
        la $t0, tdata3
        lw $t1, 0($t0)
        la $t0, tdata4
        lw $t1, 0($t0)
        la $t0, tdata5
        lw $t1, 0($t0)
        la $t0, tdata6
        lw $t1, 0($t0)
        la $t0, tdata7
        lw $t1, 0($t0)
        la $t0, tdata8
        lw $t1, 0($t0)
        la $t0, tdata9
        lw $t1, 0($t0)
        la $t0, tdata10
        lw $t1, 0($t0)
        la $t0, tdata11
        lw $t1, 0($t0)
        la $t0, tdata12
        lw $t1, 0($t0)
        la $t0, tdata13
        lw $t1, 0($t0)
        la $t0, tdata14
        lw $t1, 0($t0)
        la $t0, tdata15
        lw $t1, 0($t0)
        li $v0, 1
        syscall

        TEST_PARC_END

        //----------------------------------------------------------------
        // Test data
        //----------------------------------------------------------------

        .data
        .align 4

tdata0: .word 0x00000000
tdata1: .word 0x00000000
tdata2: .word 0x00000000
tdata3: .word 0x00000000
tdata4: .word 0x00000000
tdata5: .word 0x00000000
tdata6: .word 0x00000000
tdata7: .word 0x00000000
tdata8: .word 0x00000000
tdata9: .word 0x00000000
tdata10: .word 0x00000000
tdata11: .word 0x00000000
tdata12: .word 0x00000000
tdata13: .word 0x00000000
tdata14: .word 0x00000000
tdata15: .word 0x00000000
