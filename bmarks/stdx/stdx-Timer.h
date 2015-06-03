//========================================================================
// stdx-Timer : Fast delegation of void member functions
//========================================================================

#ifndef STDX_TIMER_H
#define STDX_TIMER_H

#include "stdx-Exception.h"
#include <iostream>

namespace stdx {

  class Timer {

   public:

    //--------------------------------------------------------------------
    // ElapsedTime
    //--------------------------------------------------------------------
    // This object is used to represent a timer's elapsed time. Although
    // it can represent times at a picosecond resolution, most timers
    // have much worse resolution. The division and multiplication
    // operators are useful when we want to divide an elapsed time or
    // multiply a elapsed time by an integer number.

    class ElapsedTime {

     public:

      ElapsedTime();
      ElapsedTime( double secs );
      ElapsedTime( long long psecs );

      double get_secs() const;
      long long get_psecs() const;

      ElapsedTime operator/( int num ) const;
      ElapsedTime operator*( int num ) const;

     private:

      typedef ElapsedTime this_t;

      friend std::ostream&
      operator<<( std::ostream& os, const this_t& time );

      friend bool operator==( const this_t& time0, const this_t& time1 );
      friend bool operator!=( const this_t& time0, const this_t& time1 );
      friend bool operator<( const this_t& time0, const this_t& time1 );
      friend bool operator>( const this_t& time0, const this_t& time1 );

      long long m_psecs;

    };

    //--------------------------------------------------------------------
    // Constructors/Destructors
    //--------------------------------------------------------------------

    Timer();

    //--------------------------------------------------------------------
    // start/stop
    //--------------------------------------------------------------------
    // Starting a timer will also reset that timer.

    void start();
    void stop();

    //--------------------------------------------------------------------
    // get_elapsed
    //--------------------------------------------------------------------
    // Getting the elapsed time will either return the time since the
    // timer was started or if the timer has been stopped, then it will
    // return the elapsed time between when the timer was last started
    // and stopped.

    ElapsedTime get_elapsed() const;

    //--------------------------------------------------------------------
    // get_resolution
    //--------------------------------------------------------------------
    // We determine the timer's resolution at run-time by first starting
    // the timer and then running a while loop until the time changes.

    static ElapsedTime get_resolution();

    //--------------------------------------------------------------------
    // estimate_required_trials
    //--------------------------------------------------------------------
    // This helper function will run repeatedly run the given function
    // object to determine how many trials we need to achieve the given
    // amount of significance based on the timers resolution. The
    // significance is expressed as a multiple of the timer resolution.
    // The minimum number of trials should be the number of trials
    // required to ensure the function is sufficiently warmed up.

    template < typename Func >
    static int
    estimate_required_trials( const Func& func,
                              int significance = 1000,
                              int min_trials   = 10 );

    //--------------------------------------------------------------------
    // Private Functions and Data
    //--------------------------------------------------------------------

   private:

    bool m_running;
    long long m_psecs;

  };

  //----------------------------------------------------------------------
  // ERequiredTrialsTooLarge
  //----------------------------------------------------------------------
  // This exception is thrown by estimate_required_trials if the
  // required number of trials exceeds the max size of an int. This can
  // sometimes happen with very short test functions and very poor timer
  // resolution (eg. having to use the clock() function).

  class ERequiredTrialsTooLarge : public stdx::Exception { };

  //----------------------------------------------------------------------
  // ElapsedTime free function operators
  //----------------------------------------------------------------------

  std::ostream& operator<<( std::ostream& os,
                            const Timer::ElapsedTime& time );

  bool operator==( const Timer::ElapsedTime& time0,
                   const Timer::ElapsedTime& time1 );

  bool operator!=( const Timer::ElapsedTime& time0,
                   const Timer::ElapsedTime& time1 );

  bool operator<( const Timer::ElapsedTime& time0,
                  const Timer::ElapsedTime& time1 );

  bool operator>( const Timer::ElapsedTime& time0,
                  const Timer::ElapsedTime& time1 );

}

#include "stdx-Timer.inl"
#endif /* STDX_TIMER_H */

