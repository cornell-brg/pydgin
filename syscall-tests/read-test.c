//========================================================================
// read-test.c
//========================================================================
// Tests read()

#include <unistd.h>
#include <stdio.h>

int main() {

  // test reading from command line and printing it

  char buf[1000];

  int len = read( 0, buf, 1000 );

  // we need to null-terminate the string
  buf[len] = '\0';

  printf( "read len=%d\ndata=%s", len, buf );

  return 0;
}
