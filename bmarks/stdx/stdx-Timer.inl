//========================================================================
// stdx-Timer.inl
//========================================================================
// For now we want the elapsed time stuff to get optimized away so we
// define all of the elapsed time functions as inline.

#include <limits>

namespace stdx {

  //----------------------------------------------------------------------
  // ElapsedTime: Constructors
  //----------------------------------------------------------------------

  inline Timer::ElapsedTime::ElapsedTime()
    : m_psecs(0)
  { }

  inline Timer::ElapsedTime::ElapsedTime( double secs )
    : m_psecs( static_cast<long long>(secs * 1000000000000LL) )
  { }

  inline Timer::ElapsedTime::ElapsedTime( long long psecs )
    : m_psecs(psecs)
  { }

  //----------------------------------------------------------------------
  // ElapsedTime: get_secs
  //----------------------------------------------------------------------

  inline double Timer::ElapsedTime::get_secs() const
  {
    return m_psecs / static_cast<double>(1000000000000LL);
  }

  //----------------------------------------------------------------------
  // ElapsedTime: get_psecs
  //----------------------------------------------------------------------

  inline long long Timer::ElapsedTime::get_psecs() const
  {
    return m_psecs;
  }

  //----------------------------------------------------------------------
  // ElapsedTime: operator /
  //----------------------------------------------------------------------

  inline Timer::ElapsedTime Timer::ElapsedTime::operator/( int num ) const
  {
    return ElapsedTime( m_psecs / num );
  }

  //----------------------------------------------------------------------
  // ElapsedTime: operator *
  //----------------------------------------------------------------------

  inline Timer::ElapsedTime Timer::ElapsedTime::operator*( int num ) const
  {
    return ElapsedTime( m_psecs * num );
  }

  //----------------------------------------------------------------------
  // ElapsedTime: operator <<
  //----------------------------------------------------------------------

  inline std::ostream& operator<<( std::ostream& os,
                                   const Timer::ElapsedTime& time )
  {
    os << time.get_secs();
    return os;
  }

  //----------------------------------------------------------------------
  // ElapsedTime: operator ==
  //----------------------------------------------------------------------

  inline bool operator==( const Timer::ElapsedTime& time0,
                          const Timer::ElapsedTime& time1 )
  {
    return ( time0.m_psecs == time1.m_psecs );
  }

  //----------------------------------------------------------------------
  // ElapsedTime: operator !=
  //----------------------------------------------------------------------

  inline bool operator!=( const Timer::ElapsedTime& time0,
                          const Timer::ElapsedTime& time1 )
  {
    return ( time0.m_psecs != time1.m_psecs );
  }

  //----------------------------------------------------------------------
  // ElapsedTime: operator <
  //----------------------------------------------------------------------

  inline bool operator<( const Timer::ElapsedTime& time0,
                         const Timer::ElapsedTime& time1 )
  {
    return ( time0.m_psecs < time1.m_psecs );
  }

  //----------------------------------------------------------------------
  // ElapsedTime: operator >
  //----------------------------------------------------------------------

  inline bool operator>( const Timer::ElapsedTime& time0,
                         const Timer::ElapsedTime& time1 )
  {
    return ( time0.m_psecs > time1.m_psecs );
  }

  //----------------------------------------------------------------------
  // estimate_required_trials
  //----------------------------------------------------------------------

  template < typename Func >
  int Timer::estimate_required_trials( const Func& func,
                                       int significance, int min_trials )
  {
    Timer timer;
    int num_trials = min_trials;
    bool done = false;

    while ( !done ) {

      // Try running the given function num_trials times

      timer.start();
      for ( int i = 0; i < num_trials; i++ )
        func();
      timer.stop();

      // If the time to run this number of trials is greater than the
      // resolution times the significance then this number of trials
      // should be good enough. Otherwise double the number of trials
      // and try again.

      if ( timer.get_elapsed() > (get_resolution() * significance) )
        done = true;
      else
        num_trials = num_trials * 2;

      if ( num_trials > (std::numeric_limits<int>::max()/4) )
        STDX_THROW( stdx::ERequiredTrialsTooLarge,
                    "Number of required trials exceeds max int size" );

    }
    return num_trials;
  }

}

