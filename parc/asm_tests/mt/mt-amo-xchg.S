//========================================================================
// mt-amo-xchg.S
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

    TEST_MT_AMO_OP( amo.xchg, tdata_0, 0xff00ff00, 0x0f0f0f0f, 0x0f0f0f0f )
    TEST_MT_AMO_OP( amo.xchg, tdata_0, 0xdeadbeef, 0x8badf00d, 0x8badf00d )
    TEST_MT_AMO_OP( amo.xchg, tdata_0, 0xdeadbabe, 0xcafed00d, 0xcafed00d )
    TEST_MT_AMO_OP( amo.xchg, tdata_0, 0xfaceb00c, 0xfacefeed, 0xfacefeed )

    //--------------------------------------------------------------------
    // Atomicity test
    //--------------------------------------------------------------------

atomicity_test:

    // All threads update atomic location
 
   
    li       $4, 1
    la       $3, amo_var 

try_lock:
    amo.xchg $4, $3, $4
    bnez     $4, try_lock

    la       $5, add_var
    lw       $6, ($5)
    addu     $6, 1
    sw       $6, ($5)
    amo.xchg $0, $3, $0
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
    lw      $6, add_var

    TEST_CHECK_EQ( $6, $5 )

    TEST_MT_END

    //--------------------------------------------------------------------
    // Test data
    //--------------------------------------------------------------------

    .data
    .align 4

tdata_0:     .word 0xdeadbeef

amo_var:     .word 0
add_var:     .word 0
done_array:  .fill MAVEN_SYSCFG_MAX_PROCS, 4, 0xffffffff

