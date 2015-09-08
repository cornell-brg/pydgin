//========================================================================
// pydgin.h
//========================================================================
//
// Header file for calls exposed to applications linking agains pydgin
// library.

#ifndef __PYDGIN_H__
#define __PYDGIN_H__

#define PYDGIN_EXIT_SYSCALL       0
#define PYDGIN_EXCEPTION          1
#define PYDGIN_REACHED_MAX_INSTS  2

#include <inttypes.h>

// note: the extern c is necessary when using this library from the c++
// world (otherwise it can't find the symbols during linking)
#ifdef __cplusplus
extern "C" {
#endif

// this needs to be called before any of the calls below
void rpython_startup_code();

int pydgin_init_elf( char *filename, int argc, char **argv, char **envp,
                     char **debug_flags, uint8_t *pmem, int do_not_load );

struct PydginReturn {
  // status of pydgin execution
  int pydgin_status;
  // the simulated program status if applicable
  int prog_status;
};

// simulate for number of instructions
void pydgin_simulate_num_insts( long long num_insts, struct PydginReturn *ret );

// simulate until the program ends
void pydgin_simulate( struct PydginReturn *ret );

//------------------------------------------------------------------------
// architectural access
//------------------------------------------------------------------------
// TODO: these might be a bit too architecture-specific; make them less so

struct PydginArmArchState {
  uint32_t rf[ 16 ];
  uint32_t pc;
  uint32_t cpsr;
  uint32_t brk_point;
};

void pydgin_get_arch_state( struct PydginArmArchState *state );
void pydgin_set_arch_state( struct PydginArmArchState *state );

void pydgin_set_ptable( int *ptable, int ptable_nentries );
int pydgin_get_ptable( int *ptable );

#ifdef __cplusplus
}
#endif

#endif
