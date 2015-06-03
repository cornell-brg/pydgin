//========================================================================
// stdx-Enum Unit Tests
//========================================================================

#include "stdx-Enum.h"
#include "utst.h"
#include <iostream>

//------------------------------------------------------------------------
// Simple Test Enum
//------------------------------------------------------------------------

struct Fruit : public stdx::Enum<Fruit>
{
  static const Fruit apple;
  static const Fruit orange;
  static const Fruit pear;
};

// We initialize this static variable first to test static
// initialization. Assuming the compiler does the static initialization
// in file definition order, initializing s_fruit directly with
// Fruit::apple will cause a segfault or s_fruit won't really be an
// apple. Using the static_access method guarantees that you will get
// the same object as what Fruit::apple will eventually be initialized
// with.

static Fruit s_fruit = Fruit::static_access( Fruit::apple );

// Initialize the apple directly

const Fruit Fruit::apple
  = Fruit::static_init( Fruit::apple, "apple" );

// Initialize the orange and pear using the helper macro

STDX_ENUM_ITEM( Fruit, orange );
STDX_ENUM_ITEM( Fruit, pear   );

//------------------------------------------------------------------------
// Enum in Templated Class
//------------------------------------------------------------------------

template < typename T >
struct TestClass
{
  struct Color : public stdx::Enum<Color>
  {
    static const Color red;
    static const Color green;
    static const Color blue;
  };
};

typedef TestClass<int>::Color Color;

// As before we want to test static access

static Color s_color = Color::static_access( Color::red );

// Initialize items. Notice that we have to template the initialization,
// and thus we get separate items for each specialization of TestClass.
// Obviously we cannot use the STDX_ENUM_ITEM helper macro.

template < typename T >
const typename TestClass<T>::Color TestClass<T>::Color::red
  = TestClass<T>::Color::static_init(TestClass<T>::Color::red,"red");

template < typename T >
const typename TestClass<T>::Color TestClass<T>::Color::green
  = TestClass<T>::Color::static_init(TestClass<T>::Color::green,"green");

template < typename T >
const typename TestClass<T>::Color TestClass<T>::Color::blue
  = TestClass<T>::Color::static_init(TestClass<T>::Color::blue,"blue");

//------------------------------------------------------------------------
// TestComparison
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestComparison )
{
  // Compare fruit

  UTST_CHECK_EQ( Fruit::apple,  Fruit::apple  );
  UTST_CHECK_EQ( Fruit::orange, Fruit::orange );
  UTST_CHECK_EQ( Fruit::pear,   Fruit::pear   );

  UTST_CHECK_NEQ( Fruit::apple,  Fruit::orange );
  UTST_CHECK_NEQ( Fruit::orange, Fruit::pear   );
  UTST_CHECK_NEQ( Fruit::pear,   Fruit::apple  );

  Fruit test_fruit;

  test_fruit = Fruit::apple;
  UTST_CHECK_EQ( test_fruit, Fruit::apple );

  test_fruit = Fruit::orange;
  UTST_CHECK_EQ( test_fruit, Fruit::orange );

  test_fruit = Fruit::pear;
  UTST_CHECK_EQ( test_fruit, Fruit::pear );

  // Compare colors

  UTST_CHECK_EQ( Color::red,   Color::red   );
  UTST_CHECK_EQ( Color::green, Color::green );
  UTST_CHECK_EQ( Color::blue,  Color::blue  );

  UTST_CHECK_NEQ( Color::red,   Color::green );
  UTST_CHECK_NEQ( Color::green, Color::blue  );
  UTST_CHECK_NEQ( Color::blue,  Color::red   );

  Color test_color;

  test_color = Color::red;
  UTST_CHECK_EQ( test_color, Color::red );

  test_color = Color::green;
  UTST_CHECK_EQ( test_color, Color::green );

  test_color = Color::blue;
  UTST_CHECK_EQ( test_color, Color::blue );
}

//------------------------------------------------------------------------
// TestGetItems
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestGetItems )
{
  // Get items for fruit

  std::vector<Fruit> fruit_vec(3);
  fruit_vec.at(0) = Fruit::apple;
  fruit_vec.at(1) = Fruit::orange;
  fruit_vec.at(2) = Fruit::pear;

  UTST_CHECK_CONT_EQ( Fruit::get_items(), fruit_vec );

  // Get items for colors

  std::vector<Color> color_vec(3);
  color_vec.at(0) = Color::red;
  color_vec.at(1) = Color::green;
  color_vec.at(2) = Color::blue;

  UTST_CHECK_CONT_EQ( Color::get_items(), color_vec );
}

//------------------------------------------------------------------------
// TestStaticAccess
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestStaticAccess )
{
  // Static access for fruit

  UTST_CHECK_EQ(  s_fruit, Fruit::apple  );
  UTST_CHECK_NEQ( s_fruit, Fruit::orange );
  UTST_CHECK_NEQ( s_fruit, Fruit::pear   );

  s_fruit = Fruit::orange;

  UTST_CHECK_EQ(  s_fruit, Fruit::orange );
  UTST_CHECK_NEQ( s_fruit, Fruit::apple  );
  UTST_CHECK_NEQ( s_fruit, Fruit::pear   );

  // Static access for colors

  UTST_CHECK_EQ(  s_color, Color::red    );
  UTST_CHECK_NEQ( s_color, Color::green  );
  UTST_CHECK_NEQ( s_color, Color::blue   );

  s_color = Color::green;

  UTST_CHECK_EQ(  s_color, Color::green  );
  UTST_CHECK_NEQ( s_color, Color::red    );
  UTST_CHECK_NEQ( s_color, Color::blue   );
}

//------------------------------------------------------------------------
// TestIO
//------------------------------------------------------------------------

template <typename T>
T from_s( const std::string& str )
{
  std::istringstream ist(str);
  T ret_val;
  ist >> ret_val;
  UTST_CHECK( !ist.fail() );
  return ret_val;
}

template < class T >
std::string to_s( const T& in )
{
  std::ostringstream ost;
  ost << in;
  return ost.str();
}

UTST_AUTO_TEST_CASE( TestIO )
{
  using namespace stdx;

  // IO for fruit

  UTST_CHECK_EQ( to_s(Fruit::apple),  "apple"  );
  UTST_CHECK_EQ( to_s(Fruit::orange), "orange" );
  UTST_CHECK_EQ( to_s(Fruit::pear),   "pear"   );

  Fruit test_fruit;

  test_fruit = Fruit::apple;
  UTST_CHECK_EQ( to_s(test_fruit), "apple" );

  test_fruit = Fruit::orange;
  UTST_CHECK_EQ( to_s(test_fruit), "orange" );

  test_fruit = Fruit::pear;
  UTST_CHECK_EQ( to_s(test_fruit), "pear" );

  UTST_CHECK_EQ( from_s<Fruit>("apple"),  Fruit::apple  );
  UTST_CHECK_EQ( from_s<Fruit>("orange"), Fruit::orange );
  UTST_CHECK_EQ( from_s<Fruit>("pear"),   Fruit::pear   );

  UTST_CHECK_EQ( from_s<Fruit>("Fruit::apple"),  Fruit::apple  );
  UTST_CHECK_EQ( from_s<Fruit>("Fruit::orange"), Fruit::orange );
  UTST_CHECK_EQ( from_s<Fruit>("Fruit::pear"),   Fruit::pear   );

  // IO for colors

  UTST_CHECK_EQ( to_s(Color::red),   "red"   );
  UTST_CHECK_EQ( to_s(Color::green), "green" );
  UTST_CHECK_EQ( to_s(Color::blue),  "blue"  );

  Color test_color;

  test_color = Color::red;
  UTST_CHECK_EQ( to_s(test_color), "red" );

  test_color = Color::green;
  UTST_CHECK_EQ( to_s(test_color), "green" );

  test_color = Color::blue;
  UTST_CHECK_EQ( to_s(test_color), "blue" );

  UTST_CHECK_EQ( from_s<Color>("red"),   Color::red   );
  UTST_CHECK_EQ( from_s<Color>("green"), Color::green );
  UTST_CHECK_EQ( from_s<Color>("blue"),  Color::blue  );

  UTST_CHECK_EQ( from_s<Color>("TestClass<int>::Color::red"),   Color::red   );
  UTST_CHECK_EQ( from_s<Color>("TestClass<int>::Color::green"), Color::green );
  UTST_CHECK_EQ( from_s<Color>("TestClass<int>::Color::blue"),  Color::blue  );

  TestClass<int>::Color::set_prefix("Color");

  UTST_CHECK_EQ( from_s<Color>("red"),   Color::red   );
  UTST_CHECK_EQ( from_s<Color>("green"), Color::green );
  UTST_CHECK_EQ( from_s<Color>("blue"),  Color::blue  );

  UTST_CHECK_EQ( from_s<Color>("Color::red"),   Color::red   );
  UTST_CHECK_EQ( from_s<Color>("Color::green"), Color::green );
  UTST_CHECK_EQ( from_s<Color>("Color::blue"),  Color::blue  );
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv );
}
