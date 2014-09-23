#include <stdio.h>
#include <stdlib.h>
#include <sys/utsname.h>

int main( int argc, char** argv ) {

  struct utsname x;

  printf("hello %p\n", &x);

  uname( &x ) ;

  printf("%p  %d   %s\n", &x.sysname,  sizeof(x.sysname),  x.sysname  );
  printf("%p  %d   %s\n", &x.nodename, sizeof(x.nodename), x.nodename );
  printf("%p  %d   %s\n", &x.release,  sizeof(x.release),  x.release  );
  printf("%p  %d   %s\n", &x.version,  sizeof(x.version),  x.version  );
  printf("%p  %d   %s\n", &x.machine,  sizeof(x.machine),  x.machine  );

  return 1;
}
