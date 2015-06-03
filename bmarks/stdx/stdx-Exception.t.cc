//========================================================================
// stdx-Exception Unit Tests
//========================================================================

#include "stdx-Exception.h"
#include "utst.h"
#include <string>
#include <vector>

//------------------------------------------------------------------------
// Example exception classes
//------------------------------------------------------------------------

struct ETestException1 : public stdx::Exception { };
struct ETestException2 : public stdx::Exception { };
struct ETestException3 : public stdx::Exception { };

//------------------------------------------------------------------------
// Free function which throws exception
//------------------------------------------------------------------------

void throw_exception()
{
  STDX_THROW( ETestException1, "Thrown from throw_exception()!" );
}

//------------------------------------------------------------------------
// Member functions which throw exceptions
//------------------------------------------------------------------------

struct Base {

  virtual ~Base() { };
  virtual void foo_e() = 0;
  virtual void foo_a() = 0;

  virtual void bar_e()
  {
    STDX_M_THROW( ETestException2, "Thrown from Base::bar()" );
  };

  virtual void bar_a()
  {
    STDX_M_ASSERT( 1 == 2 );
  };

};

template <typename T>
struct Derived : public Base {

  virtual void foo_e()
  {
    STDX_M_THROW( ETestException3, "Thrown from Derived::foo()" );
  }

  virtual void foo_a()
  {
    STDX_M_ASSERT( 1 == 2 );
  }

};

//------------------------------------------------------------------------
// TestException
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestException )
{
  UTST_CHECK_THROW( ETestException1, throw_exception() );

  Derived<int> derived;
  UTST_CHECK_THROW( ETestException2, derived.bar_e() );
  UTST_CHECK_THROW( ETestException3, derived.foo_e() );

  Base* basePtr = &derived;
  UTST_CHECK_THROW( ETestException2, basePtr->bar_e() );
  UTST_CHECK_THROW( ETestException3, basePtr->foo_e() );
}

//------------------------------------------------------------------------
// TestAssert
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestAssert )
{
  UTST_CHECK_THROW( stdx::EAssert, STDX_ASSERT( 1 == 2 ) );

  Derived<int> derived;
  UTST_CHECK_THROW( stdx::EAssert, derived.bar_a() );
  UTST_CHECK_THROW( stdx::EAssert, derived.foo_a() );

  Base* basePtr = &derived;
  UTST_CHECK_THROW( stdx::EAssert, basePtr->bar_a() );
  UTST_CHECK_THROW( stdx::EAssert, basePtr->foo_a() );
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv );
}

