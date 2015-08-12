//========================================================================
// pydgin.h
//========================================================================
//
// Header file for calls exposed to applications linking agains pydgin
// library.

#ifndef __PYDGIN_H__
#define __PYDGIN_H__

// note: the extern c is necessary when using this library from the c++
// world (otherwise it can't find the symbols during linking)
#ifdef __cplusplus
extern "C" {
#endif

// this needs to be called before any of the calls below
void rpython_startup_code();

int pydgin_simulate_elf( char *filename );

#ifdef __cplusplus
}
#endif

#endif
