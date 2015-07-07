//========================================================================
// mt-amo-and.S
//========================================================================
// This only really works if the number of threads is less than 32 which
// is the assumed number of bits in a word.

#include "mt-macros.h"
#include <machine/syscfg.h>

    TEST_MT_BEGIN

    //--------------------------------------------------------------------
    // Setup
    //--------------------------------------------------------------------

    // Keep this thread's core id in register $10

    mfc0    $10, $c0_coreid

    // Worker threads jump around the basic amo tests

    bne     $10, $0, atomicity_test

    //--------------------------------------------------------------------
    // Arithmetic tests
    //--------------------------------------------------------------------

    TEST_MT_AMO_OP( amo.and, tdata_0, 0xff00ff00, 0x0f0f0f0f, 0x0f000f00 )
    TEST_MT_AMO_OP( amo.and, tdata_0, 0x0ff00ff0, 0xf0f0f0f0, 0x00f000f0 )
    TEST_MT_AMO_OP( amo.and, tdata_0, 0x00ff00ff, 0x0f0f0f0f, 0x000f000f )
    TEST_MT_AMO_OP( amo.and, tdata_0, 0xf00ff00f, 0xf0f0f0f0, 0xf000f000 )

    //--------------------------------------------------------------------
    // Atomicity test
    //--------------------------------------------------------------------

atomicity_test:

    // All threads update atomic location

    li      $2, 1
    sllv    $2, $2, $10
    nor     $2, $0
    la      $3, amo_var
    amo.and $0, $3, $2
    sync.l

    // Threads set appropriate element of done array and spin

    sll     $2, $10, 2
    la      $3, done_array
    addu    $3, $2
    li      $2, 1
    sw      $2, ($3)

    // Worker threads are done now

    bne     $10, $0, _pass

    // Master thread waits for all threads to finish

master_thread:

    la      $3, done_array
    li      $2, 1
    sw      $2, ($3)
    lw      $5, (_numcores)

join_loop:
1:  lw      $4, ($3)
    beq     $4, $0, 1b
    addiu   $3, 4
    addiu   $5, -1
    bgtz    $5, join_loop

    // Master thread checks for correct result

    lw      $5, _numcores
    lw      $6, amo_var

check_loop:
    andi    $7, $6, 0x1
    TEST_CHECK_EQ( $7, 0x0 )
    srl     $6, 1
    addiu   $5, -1
    bgtz    $5, check_loop

    TEST_MT_END

    //--------------------------------------------------------------------
    // Test data
    //--------------------------------------------------------------------

    .data
    .align 4

tdata_0:    .word 0xdeadbeef

amo_var:    .word 0
done_array: .fill MAVEN_SYSCFG_MAX_PROCS, 4, 0xffffffff

