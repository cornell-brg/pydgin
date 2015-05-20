
#include "stdio.h"

#ifdef _MIPS_ARCH_MAVEN
int loop_parc( int n ) {
  int i, j;
  int sum;
  for ( i = 0; i < n; i++ )
    for ( j = 0; j < n; j++ ) {
      // load sum to register
      register int sum_r = sum;
      incr_label:
      __asm__ ( "addiu %0, %1, 1" : "=r" (sum_r) : "r" (sum_r) );
      // store the register back
      sum = sum_r;
      if ( i == 90 && j == 50 ) {
        // modify incr_label with addiu sum_r, sum_r, -1
        unsigned int *incr_label_ptr;
        incr_label_ptr = (unsigned int *) &&incr_label;
        *incr_label_ptr = 0x2610ffff;
      } else if ( i == 160 && j == 50 ) {
        // modify incr_label with addiu sum_r, sum_r, 2
        unsigned int *incr_label_ptr;
        incr_label_ptr = (unsigned int *) &&incr_label;
        *incr_label_ptr = 0x26100002;
      }

    }

  return sum;
}
#endif

int loop( int n ) {
  int i, j;
  int sum;
  for ( i = 0; i < n; i++ )
    for ( j = 0; j < n; j++ )
      sum += 1;

  return sum;
}


int main() {

  int sum;
  #ifdef _MIPS_ARCH_MAVEN
  sum = loop_parc( 250 );
  #else
  sum = loop( 250 );
  #endif
  printf( "sum: %d\n", sum );
  if ( sum == 49949 ) {
    printf( "TEST PASSED!\n" );
  } else {
    printf( "TEST FAILED! Was expecting 49949\n" );
  }
  return 0;

}
