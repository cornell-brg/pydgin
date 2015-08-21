//========================================================================
// pydgin.h
//========================================================================
//
// Header file for calls exposed to applications linking agains pydgin
// library.

#ifndef __PYDGIN_H__
#define __PYDGIN_H__

#include <inttypes.h>

// note: the extern c is necessary when using this library from the c++
// world (otherwise it can't find the symbols during linking)
#ifdef __cplusplus
extern "C" {
#endif

// this needs to be called before any of the calls below
void rpython_startup_code();

int pydgin_init_elf( char *filename, int argc, char **argv, char **envp,
                     char **debug_flags );

// simulate for number of instructions
int pydgin_simulate_num_insts( long long num_insts );

// simulate until the program ends
int pydgin_simulate();

//------------------------------------------------------------------------
// architectural access
//------------------------------------------------------------------------
// TODO: these might be a bit too architecture-specific; make them less so

struct PydginArmArchState {
  int32_t rf[ 16 ];
  int32_t pc;
  int32_t cpsr;
};

void pydgin_get_arch_state( struct PydginArmArchState *state );
void pydgin_set_arch_state( struct PydginArmArchState *state );

#ifdef __cplusplus
}
#endif

#endif
