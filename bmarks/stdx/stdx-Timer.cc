//========================================================================
// stdx-Timer.cc
//========================================================================

#include "stdx-Timer.h"
#include <iostream>

//------------------------------------------------------------------------
// Choose timing implementation
//------------------------------------------------------------------------
// Our stdx.ac has a check to see if getrusage is available. If so it
// defines STDX_HAVE_GETRUSAGE in stdx-config.h. So we use getrusage if
// we have it, otherwise we default to using the ANSI standard clock()
// function. We have a special case for maven where we can use the
// non-standard get_cycles() function for very high resolution timing.

#include "stdx-config.h"

#ifdef _MIPS_ARCH_MAVEN
#include <sys/timex.h>
#elif defined STDX_HAVE_GETRUSAGE
#include <sys/resource.h>
#else
#include <ctime>
#endif

namespace {

  long long get_current_psecs()
  {
    long long psecs = 0;

    // On maven use get_cycle() function
    #ifdef _MIPS_ARCH_MAVEN

      psecs = get_cycles() * (1000000000000LL / get_cycles_per_sec());

    // Otherwise use getrusage if we have it
    #elif defined STDX_HAVE_GETRUSAGE

      rusage ru;
      getrusage( RUSAGE_SELF, &ru );
      psecs += ru.ru_utime.tv_sec  * 1000000000000LL;
      psecs += ru.ru_utime.tv_usec * 1000000LL;

    // Fall back on the ANSI standard clock() function
    #else

      psecs = clock() * (1000000000000LL / CLOCKS_PER_SEC);

    #endif
    return psecs;
  }

}

namespace stdx {

  //----------------------------------------------------------------------
  // Constructors/Destructors
  //----------------------------------------------------------------------

  Timer::Timer()
   : m_running(false),
     m_psecs(0)
  { }

  //----------------------------------------------------------------------
  // start/stop
  //----------------------------------------------------------------------

  void Timer::start()
  {
    m_psecs   = get_current_psecs();
    m_running = true;
  }

  void Timer::stop()
  {
    m_psecs   = get_current_psecs() - m_psecs;
    m_running = false;
  }

  //----------------------------------------------------------------------
  // get_elapsed
  //----------------------------------------------------------------------

  Timer::ElapsedTime Timer::get_elapsed() const
  {
    if ( !m_running )
      return ElapsedTime( m_psecs );

    return ElapsedTime( get_current_psecs() - m_psecs );
  }

  //----------------------------------------------------------------------
  // get_resolution
  //----------------------------------------------------------------------

  Timer::ElapsedTime Timer::get_resolution()
  {
    static ElapsedTime s_resolution = ElapsedTime();

    // On the first time we call this function we need to figure out
    // what the timer resolution is.
    if ( s_resolution == ElapsedTime() ) {

      // Create a timner, start it, and determine the elapsed time at
      // the very beginning.

      Timer timer;
      timer.start();
      Timer::ElapsedTime time_start = timer.get_elapsed();

      // Keep testing the timer as fast as possible until it returns a
      // time which is different from the start time - this is roughly
      // the timer resolution.

      while ( timer.get_elapsed() == time_start ) { }

      // We stop the timer and set the static resolution variable to
      // twice what we just found. The factor of two is to give us some
      // extra room.

      timer.stop();
      s_resolution = timer.get_elapsed() * 2;
    }

    return s_resolution;
  }

}

