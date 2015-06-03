//========================================================================
// stdx-MathUtils.inl
//========================================================================

#include <cmath>

namespace stdx {

  //----------------------------------------------------------------------
  // fp_close
  //----------------------------------------------------------------------
  // Originally I used the implementation from Knuth via the C++ FAQ
  //
  //  http://www.parashift.com/c++-faq-lite/newbie.html#faq-29.17
  //
  // but this seemed to return false for some numbers which were really
  // close enough in my mind. Part of this is because the Knuth approach
  // doesn't do the first check to see if the parameters are within a
  // reasonable absolute error. Overall, I am happier with the approach
  // described in the begining of the following white paper:
  //
  //  http://www.cygnus-software.com/papers/comparingfloats/comparingfloats.htm
  //
  // You might want to look at the integer based comparison if this
  // operation is in your critical loop.

  template < typename T >
  bool fp_close( T num0, T num1, T max_abs_error, T max_rel_error )
  {
    T abs_error = std::abs( num0 - num1 );
    if ( abs_error <= max_abs_error )
      return true;

    T rel_error;
    if ( std::abs(num1) > std::abs(num0) )
      rel_error = std::abs((num0 - num1) / num1);
    else
      rel_error = std::abs((num0 - num1) / num0);

    return ( rel_error <= max_rel_error );
  }

}

