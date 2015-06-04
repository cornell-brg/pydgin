//========================================================================
// mt-macros.h
//========================================================================

#ifndef MT_MACROS_H
#define MT_MACROS_H

#include "parc-macros.h"
#include <machine/syscfg.h>

//------------------------------------------------------------------------
// TEST_MT_BEGIN
//------------------------------------------------------------------------
// Create a memory location for the tohost value and an entry point
// where the test should start. The test server will take care of
// initializing the _numcores location with the number of threads active
// in the machine. We also create an array of result values with one
// element per thread for communicating with the master thread. We need
// to activate the threads so that they are all running.

#define TEST_MT_BEGIN                                                   \
    .data;                                                              \
    .align  4;                                                          \
_tohost:   .word -1;                                                    \
_numcores: .word 1;                                                     \
_results:  .space 4*MAVEN_SYSCFG_MAX_PROCS, -1;                         \
                                                                        \
    .text;                                                              \
    .align  4;                                                          \
    .global _test;                                                      \
    .ent    _test;                                                      \
_test:                                                                  \

//------------------------------------------------------------------------
// TEST_MT_END
//------------------------------------------------------------------------
// Assumes that the result is in register number 30. This macro takes
// care of collecting the results across all of the threads. Each thread
// writes its result to its element of the results array. The master
// thread waits on each element until it doesn not equal -1. Then it
// checks to see if that thread's result is non-zero and if so it checks
// if the error line number is less than the current error line number.
// This way the tohost value for the whole test will either be zero if
// all threads pass, or it will be the linenumber of the _first_ errror.

#define TEST_MT_END                                                     \
_pass:                                                                  \
    addiu  $29, $0, 0;                                                  \
                                                                        \
_fail:                                                                  \
    /* every thread writes $29 to its element of result array */        \
    mfc0   $10, $c0_coreid;                                             \
    sll    $2, $10, 2;                                                  \
    la     $3, _results;                                                \
    addu   $3, $2;                                                      \
    sw     $29, ($3);                                                   \
                                                                        \
    /* worker threads spin, master thread falls through */              \
1:  bne    $10, $0, 1b;                                                 \
                                                                        \
    /* wait for each element of result array to not equal -1 */         \
    /*lw     $5, (_numcores);                                        */ \
    /* TODO: temporary _numcores mechanism */                           \
    mfc0   $5, $19;                                                     \
_joinloop:                                                              \
1:  lw     $4, ($3);                                                    \
    beq    $4, -1, 1b;                                                  \
                                                                        \
    /* $29 holds final result, either zero if all threads pass or   */  \
    /* the lowest line number of a failure                          */  \
    /*  if ( !($0 < $29) || (($0 < $4) && ($4 < $29)) ) $29 = $4    */  \
    sltu   $6, $0, $29;                                                 \
    nor    $6, $0;                                                      \
    andi   $6, 0x1;                                                     \
    sltu   $7, $0, $4;                                                  \
    sltu   $8, $4, $29;                                                 \
    and    $7, $8;                                                      \
    or     $6, $7;                                                      \
    /* Modification for ECE4750/PARC infrastructure:                */  \
    /* - no movn instruction, must use a branch                     */  \
    /* if $29 is 0, make it 1, otherwise $29 = $4 */                    \
    /*movn   $29, $4, $6;                                           */  \
    beqz   $6, _noerror;                                                \
    move   $29, $4;                                                     \
_noerror:                                                               \
                                                                        \
    /* next element */                                                  \
    addiu  $3, 4;                                                       \
    addiu  $5, -1;                                                      \
    bgtz   $5, _joinloop;                                               \
                                                                        \
    /* Modifications for ECE4750/PARC infrastructure:               */  \
    /* - we use mtc0 as the status register instead of _tohost      */  \
    /* - a value of 1 in the status register is passing, not 0      */  \
    /* write final tohost value */                                      \
    /*sw     $29, (_tohost);*/                                          \
    /* If $29 is zero, add 1 to indicate a passing text */              \
    bnez   $29, _noerror2;                                              \
    addiu  $29,  1;                                                     \
_noerror2:                                                              \
    mtc0   $29, $1;                                                    \
1:  j      1b;                                                          \
                                                                        \
    .end   _test                                                        \

//------------------------------------------------------------------------
// TEST_AMO : Helper macros for atomic memory instructions
//------------------------------------------------------------------------

#define TEST_MT_AMO_OP( inst_, base_, orig_, src_, result_ )            \
    la    $2, base_;                                                    \
    li    $3, orig_;                                                    \
    sw    $3, ($2);                                                     \
    li    $4, src_;                                                     \
    inst_ $5, $2, $4;                                                   \
    TEST_CHECK_EQ( $3, $5 );                                            \
    lw    $5, ($2);                                                     \
    TEST_CHECK_EQ( $5, result_ );                                       \

#endif /* MT_MACROS_H */

