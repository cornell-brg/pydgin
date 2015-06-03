//========================================================================
// stdx-ReflectionUtils Unit Tests
//========================================================================

#include "stdx-ReflectionUtils.h"
#include "stdx-config.h"
#include "utst.h"
#include <string>
#include <vector>

//------------------------------------------------------------------------
// Test is_a Operator
//------------------------------------------------------------------------

struct Base                   { virtual ~Base() { }     };
struct DerivedA : public Base { virtual ~DerivedA() { } };
struct DerivedB : public Base { virtual ~DerivedB() { } };

UTST_AUTO_TEST_CASE( TestIsA )
{
  Base     base;
  DerivedA derived_a;
  DerivedB derived_b;
  Base*    derived_a_ptr = &derived_a;
  Base*    derived_b_ptr = &derived_b;

  UTST_CHECK( stdx::is_a<Base>(base) );
  UTST_CHECK( stdx::is_a<DerivedA>(derived_a) );
  UTST_CHECK( stdx::is_a<DerivedB>(derived_b) );

  UTST_CHECK( stdx::is_a<Base>(derived_a) );
  UTST_CHECK( stdx::is_a<Base>(derived_b) );
  UTST_CHECK( stdx::is_a<Base>(*derived_a_ptr) );
  UTST_CHECK( stdx::is_a<Base>(*derived_b_ptr) );

  UTST_CHECK( !stdx::is_a<DerivedA>(derived_b) );
  UTST_CHECK( !stdx::is_a<DerivedB>(derived_a) );
  UTST_CHECK( !stdx::is_a<DerivedA>(*derived_b_ptr) );
  UTST_CHECK( !stdx::is_a<DerivedB>(*derived_a_ptr) );
}

//------------------------------------------------------------------------
// Test Demangle Type
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestDemangleType )
{
  using namespace stdx;

  #ifndef STDX_HAVE_ABI_CXA_DEMANGLE
    UTST_OUTPUT_MSG( "Skipping tests because "
                     "abi::__cxa_demangle is unavailable" );
    return;
  #endif

  // Demangle primitive type

  int num;
  typedef int int_t;
  UTST_CHECK_EQ( demangle_type<int>(),   "int" );
  UTST_CHECK_EQ( demangle_type<int_t>(), "int" );
  UTST_CHECK_EQ( demangle_type(num),     "int" );

  // Demangle string class

  std::string str;
  typedef std::string string_t;
  UTST_CHECK_EQ( demangle_type<std::string>(), "std::string" );
  UTST_CHECK_EQ( demangle_type<string_t>(),    "std::string" );
  UTST_CHECK_EQ( demangle_type(str),           "std::string" );

  // Demangle vector class (notice that default template arguments are
  // included in the result from the demangler)

  std::vector<int> vec;
  typedef std::vector<int> vec_t;

  UTST_CHECK_EQ( demangle_type<std::vector<int> >(),
                 "std::vector<int, std::allocator<int> >" );

  UTST_CHECK_EQ( demangle_type<vec_t>(),
                 "std::vector<int, std::allocator<int> >" );

  UTST_CHECK_EQ( demangle_type(vec),
                 "std::vector<int, std::allocator<int> >" );
}

//------------------------------------------------------------------------
// Test Demangle Function Name
//------------------------------------------------------------------------

// Non-templated free functions

std::string bar()
{
  return STDX_SHORT_FUNCTION_NAME;
}

std::string bar( int a, int b )
{
  return STDX_SHORT_FUNCTION_NAME;
}

// Templated free functions

template <typename T>
std::string tmpl_bar()
{
  return STDX_SHORT_FUNCTION_NAME;
}

template <typename T>
std::string tmpl_bar( int a, int b )
{
  return STDX_SHORT_FUNCTION_NAME;
}

// Non-templated test class

struct Foo
{
  std::string bar()
  {
    return STDX_SHORT_FUNCTION_NAME;
  }

  std::string bar( int a, int b )
  {
    return STDX_SHORT_FUNCTION_NAME;
  }

  static std::string s_bar( int a, int b )
  {
    return STDX_SHORT_FUNCTION_NAME;
  }
};

// Templated test class

template <typename T>
struct TmplFoo
{
  std::string bar()
  {
    return STDX_SHORT_FUNCTION_NAME;
  }

  std::string bar( int a, int b )
  {
    return STDX_SHORT_FUNCTION_NAME;
  }

  static std::string s_bar( int a, int b )
  {
    return STDX_SHORT_FUNCTION_NAME;
  }
};

UTST_AUTO_TEST_CASE( TestDemangleFunctionName )
{

  // Check free functions

  UTST_CHECK_EQ( bar(),    "bar" );
  UTST_CHECK_EQ( bar(1,2), "bar" );

  // Check templated free functions

  UTST_CHECK_EQ( tmpl_bar<int>(),    "tmpl_bar" );
  UTST_CHECK_EQ( tmpl_bar<int>(1,2), "tmpl_bar" );

  #ifndef STDX_HAVE_GNU_PRETTY_FUNCTION
    UTST_LOG_MSG( "Skipping rest of tests because "
                  "__PRETTY_FUNCTION__ not available" );
    return;
  #endif

  // Check member functions

  Foo foo;
  UTST_CHECK_EQ( foo.bar(),       "Foo::bar"   );
  UTST_CHECK_EQ( foo.bar(1,2),    "Foo::bar"   );
  UTST_CHECK_EQ( Foo::s_bar(1,2), "Foo::s_bar" );

  // Check member functions of templated class

  TmplFoo<int> tmpl_foo;
  UTST_CHECK_EQ( tmpl_foo.bar(),           "TmplFoo<T>::bar"   );
  UTST_CHECK_EQ( tmpl_foo.bar(1,2),        "TmplFoo<T>::bar"   );
  UTST_CHECK_EQ( TmplFoo<int>::s_bar(1,2), "TmplFoo<T>::s_bar" );
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv );
}

