//========================================================================
// stat-test.c
//========================================================================
// Tests stat syscall

#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <inttypes.h>


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
  int32_t *stat_arr = (int32_t *) &stat_buf;

  printf( "before stat addr: %p %p\n", &stat_buf, stat_arr );

  int i;
  for ( i = 0; i < 100; i++ ) {
    printf( "offset: %02x val: %08x\n", i*4, stat_arr[i] );
  }

  int ret = stat( path, &stat_buf );

  printf( "after\n" );
  for ( i = 0; i < 100; i++ ) {
    printf( "offset: %02x val: %08x\n", i*4, stat_arr[i] );
  }

  printf( "stat sizeof=%d\n", sizeof( stat_buf ) );


  if ( ret ) {
    printf( "Error in stat! errno=%d\n", errno );
  } else {
    printf( "stat successful! addr: %p \n", &stat_buf );
    printf( "st_mode  off: %x size: %d val: %x \n", (int) &stat_buf.st_mode  - (int) &stat_buf, sizeof( stat_buf.st_mode ), stat_buf.st_mode  );
    printf( "st_ino   off: %x size: %d val: %x \n", (int) &stat_buf.st_ino   - (int) &stat_buf, sizeof( stat_buf.st_ino  ), stat_buf.st_ino   );
    printf( "st_dev   off: %x size: %d val: %x \n", (int) &stat_buf.st_dev   - (int) &stat_buf, sizeof( stat_buf.st_dev  ), stat_buf.st_dev   );
    printf( "st_nlink off: %x size: %d val: %x \n", (int) &stat_buf.st_nlink - (int) &stat_buf, sizeof( stat_buf.st_nlink), stat_buf.st_nlink );
    printf( "st_uid   off: %x size: %d val: %x \n", (int) &stat_buf.st_uid   - (int) &stat_buf, sizeof( stat_buf.st_uid  ), stat_buf.st_uid   );
    printf( "st_gid   off: %x size: %d val: %x \n", (int) &stat_buf.st_gid   - (int) &stat_buf, sizeof( stat_buf.st_gid  ), stat_buf.st_gid   );
    printf( "st_size  off: %x size: %d val: %x \n", (int) &stat_buf.st_size  - (int) &stat_buf, sizeof( stat_buf.st_size ), stat_buf.st_size  );
    printf( "st_atime off: %x size: %d val: %x \n", (int) &stat_buf.st_atime - (int) &stat_buf, sizeof( stat_buf.st_atime), stat_buf.st_atime );
    printf( "st_mtime off: %x size: %d val: %x \n", (int) &stat_buf.st_mtime - (int) &stat_buf, sizeof( stat_buf.st_mtime), stat_buf.st_mtime );
    printf( "st_ctime off: %x size: %d val: %x \n", (int) &stat_buf.st_ctime - (int) &stat_buf, sizeof( stat_buf.st_ctime), stat_buf.st_ctime );

  }

  #ifdef __USE_LARGEFILE64
  printf( "__USE_LARGEFILE64 defined\n" );
  #endif

  struct stat stat64_buf;
  int32_t *stat64_arr = (int32_t *) &stat64_buf;


  printf( "before stat addr: %p %p\n", &stat64_buf, stat64_arr );
  for ( i = 0; i < 100; i++ ) {
    printf( "offset: %02x val: %08x\n", i*4, stat64_arr[i] );
  }

  ret = stat64( path, &stat64_buf );

  printf( "after\n" );
  for ( i = 0; i < 100; i++ ) {
    printf( "offset: %02x val: %08x\n", i*4, stat64_arr[i] );
  }

  if ( ret ) {
    printf( "Error in stat! errno=%d\n", errno );
  } else {
    printf( "stat successful! addr: %p \n", &stat64_buf );
    printf( "st_mode  off: %x size: %d val: %x \n", (int) &stat64_buf.st_mode  - (int) &stat64_buf, sizeof( stat_buf.st_mode ), stat_buf.st_mode  );
    printf( "st_ino   off: %x size: %d val: %x \n", (int) &stat64_buf.st_ino   - (int) &stat64_buf, sizeof( stat_buf.st_ino  ), stat_buf.st_ino   );
    printf( "st_dev   off: %x size: %d val: %x \n", (int) &stat64_buf.st_dev   - (int) &stat64_buf, sizeof( stat_buf.st_dev  ), stat_buf.st_dev   );
    printf( "st_nlink off: %x size: %d val: %x \n", (int) &stat64_buf.st_nlink - (int) &stat64_buf, sizeof( stat_buf.st_nlink), stat_buf.st_nlink );
    printf( "st_uid   off: %x size: %d val: %x \n", (int) &stat64_buf.st_uid   - (int) &stat64_buf, sizeof( stat_buf.st_uid  ), stat_buf.st_uid   );
    printf( "st_gid   off: %x size: %d val: %x \n", (int) &stat64_buf.st_gid   - (int) &stat64_buf, sizeof( stat_buf.st_gid  ), stat_buf.st_gid   );
    printf( "st_size  off: %x size: %d val: %x \n", (int) &stat64_buf.st_size  - (int) &stat64_buf, sizeof( stat_buf.st_size ), stat_buf.st_size  );
    printf( "st_atime off: %x size: %d val: %x \n", (int) &stat64_buf.st_atime - (int) &stat64_buf, sizeof( stat_buf.st_atime), stat_buf.st_atime );
    printf( "st_mtime off: %x size: %d val: %x \n", (int) &stat64_buf.st_mtime - (int) &stat64_buf, sizeof( stat_buf.st_mtime), stat_buf.st_mtime );
    printf( "st_ctime off: %x size: %d val: %x \n", (int) &stat64_buf.st_ctime - (int) &stat64_buf, sizeof( stat_buf.st_ctime), stat_buf.st_ctime );

  }
}
