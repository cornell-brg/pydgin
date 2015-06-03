//========================================================================
// stdx-Timer Unit Tests
//========================================================================

#include "stdx-Timer.h"
#include "utst.h"

//------------------------------------------------------------------------
// TestBasic
//------------------------------------------------------------------------

int gcd( int a, int b )
{
  if ( a == 0 )
    return b;

  return gcd( b % a, a );
}

void trial()
{
  gcd( 10946, 6765 ); // should require 20 recursive function calls
}

UTST_AUTO_TEST_CASE( TestBasic )
{
  UTST_LOG_VAR( stdx::Timer::get_resolution() );
  int num_trials = stdx::Timer::estimate_required_trials( &trial, 10 );
  UTST_LOG_VAR( num_trials );

  stdx::Timer timer;
  timer.start();
  for ( int i = 0; i < num_trials*10; i++ )
    trial();
  timer.stop();
  stdx::Timer::ElapsedTime time_per_trial
    = timer.get_elapsed()/(num_trials*10);

  UTST_LOG_VAR( timer.get_elapsed() );
  UTST_LOG_VAR( time_per_trial );
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv );
}

