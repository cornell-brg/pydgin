//========================================================================
// stdx-ImplPtr Unit Tests
//========================================================================

#include "stdx-ImplPtr.h"
#include "utst.h"
#include <string>
#include <vector>

//------------------------------------------------------------------------
// TestDefault
//------------------------------------------------------------------------

// Header file

class Foo {

 public:

  void set_value( int value );
  int  get_value();

 private:

  struct Impl;
  stdx::ImplPtr<Impl> impl;

};

// Source file

struct Foo::Impl {
  int value;
};

void Foo::set_value( int value ) { impl->value = value; }
int  Foo::get_value()            { return impl->value;  }

// Test case

UTST_AUTO_TEST_CASE( TestDefault )
{
  Foo foo1;
  foo1.set_value( 1 );
  UTST_CHECK_EQ( foo1.get_value(), 1 );

  Foo foo2 = foo1;
  UTST_CHECK_EQ( foo2.get_value(), 1 );
  foo2.set_value( 2 );
  UTST_CHECK_EQ( foo1.get_value(), 1 );
  UTST_CHECK_EQ( foo2.get_value(), 2 );
}

//------------------------------------------------------------------------
// TestExplicitConstruction
//------------------------------------------------------------------------

// Header file

class Bar {

 public:

  Bar();
  void set_value( int value );
  int  get_value();

 private:

  struct Impl;
  stdx::ImplPtr<Impl> impl;

};

// Source file

struct Bar::Impl {
  Impl( int a_value ) : value(a_value) { }
  int value;
};

Bar::Bar() : impl( new Bar::Impl(1) )
{ }

void Bar::set_value( int value ) { impl->value = value; }
int  Bar::get_value()            { return impl->value;  }

// Test case

UTST_AUTO_TEST_CASE( TestExplicitConstruction )
{
  Bar bar1;
  bar1.set_value( 1 );
  UTST_CHECK_EQ( bar1.get_value(), 1 );

  Bar bar2 = bar1;
  UTST_CHECK_EQ( bar2.get_value(), 1 );
  bar2.set_value( 2 );
  UTST_CHECK_EQ( bar1.get_value(), 1 );
  UTST_CHECK_EQ( bar2.get_value(), 2 );
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv );
}

