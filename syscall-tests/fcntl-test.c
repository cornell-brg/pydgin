//========================================================================
// fcntl-test.c
//========================================================================
// This doesn't really test the simulator, but more of the c library. We
// use this to check different fcntl flag values and what simulator
// assumes what.

#include <stdio.h>
#include <fcntl.h>


int main() {

  printf( "the following are the actual values of fcntl (hex):\n" );
  printf( "O_RDONLY    %x\n", O_RDONLY    );
  printf( "O_WRONLY    %x\n", O_WRONLY    );
  printf( "O_RDWR      %x\n", O_RDWR      );
  printf( "O_APPEND    %x\n", O_APPEND    );
  printf( "O_CREAT     %x\n", O_CREAT     );
  printf( "O_TRUNC     %x\n", O_TRUNC     );
  printf( "O_EXCL      %x\n", O_EXCL      );
  printf( "O_SYNC      %x\n", O_SYNC      );
  printf( "O_NONBLOCK  %x\n", O_NONBLOCK  );
  printf( "O_NOCTTY    %x\n", O_NOCTTY    );
  // the following don't seem to be defined for all compiler toolchains:
  //printf( "O_DIRECT    %x\n", O_DIRECT    );
  //printf( "O_BINARY    %x\n", O_BINARY    );
  //printf( "O_TEXT      %x\n", O_TEXT      );
  //printf( "O_NOINHERIT %x\n", O_NOINHERIT );
  //printf( "O_CLOEXEC   %x\n", O_CLOEXEC   );

  // we also try to open the file with various flags
  const char *filename = "/tmp/fcntl-test-deleteme";

  open( filename, O_RDONLY   );
  open( filename, O_WRONLY   );
  open( filename, O_RDWR     );
  open( filename, O_APPEND   );
  open( filename, O_CREAT    );
  open( filename, O_TRUNC    );
  open( filename, O_EXCL     );
  open( filename, O_SYNC     );
  open( filename, O_NONBLOCK );
  open( filename, O_NOCTTY   );
  //open( filename, O_DIRECT   );

  // we also check what fopen turns into
  printf( "fopen( \"r\" )\n" );
  fopen( filename, "r" );
  printf( "fopen( \"r+\" )\n" );
  fopen( filename, "r+" );
  printf( "fopen( \"w\" )\n" );
  fopen( filename, "w" );
  printf( "fopen( \"w+\" )\n" );
  fopen( filename, "w+" );
  printf( "fopen( \"a\" )\n" );
  fopen( filename, "a" );
  printf( "fopen( \"a+\" )\n" );
  fopen( filename, "a+" );

}
