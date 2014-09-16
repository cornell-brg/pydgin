//========================================================================
// stat-test.c
//========================================================================
// Tests stat syscall

#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>


int main() {

  // read a path
  char path[ 100 ];

  fgets( path, 100, stdin );

  printf( "path: %s\n", path );

  // strip out the newline

  int len = strlen( path );
  if ( path[ len - 1 ] == '\n' )
    path[ len - 1 ] = '\0';

  struct stat stat_buf;

  int ret = stat( path, &stat_buf );

  if ( ret ) {
    printf( "Error in stat! errno=%d\n", errno );
  } else {
    printf( "stat successful!\n" );
    printf( "st_mode  %x\n", stat_buf.st_mode  );
    printf( "st_ino   %x\n", stat_buf.st_ino   );
    printf( "st_dev   %x\n", stat_buf.st_dev   );
    printf( "st_nlink %x\n", stat_buf.st_nlink );
    printf( "st_uid   %x\n", stat_buf.st_uid   );
    printf( "st_gid   %x\n", stat_buf.st_gid   );
    printf( "st_size  %x\n", stat_buf.st_size  );
    printf( "st_atime %x\n", stat_buf.st_atime );
    printf( "st_mtime %x\n", stat_buf.st_mtime );
    printf( "st_ctime %x\n", stat_buf.st_ctime );

  }

}
