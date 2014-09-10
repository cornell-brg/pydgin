//========================================================================
// open-close-test.c
//========================================================================
// Tests open() and close()

#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>

int main() {

  // read a file name
  char buf[ 1000 ];
  char *filename = buf;

  fgets( filename, 1000, stdin );

  printf( "filename: %s\n", filename );

  // strip out the newline

  int len = strlen( filename );
  if ( filename[ len - 1 ] == '\n' )
    filename[ len - 1 ] = '\0';

  // open the file

  int fd = open( filename, O_RDONLY );

  if ( fd == -1 ) {
    printf( "Error in open! errno=%d\n", errno );
  } else {
    printf( "open successful!\n" );

    // read the contents of file and write to stdout
    int sz;
    do {
      sz = read( fd, buf, 1000 );
      if ( sz == -1 ) {
        printf( "Error in read! errno=%d\n", errno );
        break;
      }

      // we add a null char at the end and print
      buf[ sz ] = '\0';

      printf( "%s", buf );
    } while ( sz );

    // close the file
    if ( close( fd ) )
      printf( "Error in close! errno=%d\n", errno );
    else
      printf( "close successful!\n" );
  }

  return 0;
}
