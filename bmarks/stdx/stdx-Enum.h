//========================================================================
// stdx-Enum : Typesafe and IO friendly enumerations
//========================================================================
// Standard C++ enums have some problems including type-safety issues,
// lack of a containing namespace, inability to easily read/write enums
// to streams, and no support for extending an enum. The following
// simple class solves these problems with relatively little burden on
// the programmer. For example, a user first declares the enumeration in
// the header file as follows:
//
//  struct Fruit : public stdx::Enum<Fruit>
//  {
//    static const Fruit apple;
//    static const Fruit orange;
//    static const Fruit pear;
//  };
//
// Since the enumeration items are static constants we need to
// initialize them in the source file like this:
//
//  const Fruit Fruit::apple  = Fruit::static_init( Fruit::apple,  "apple"  );
//  const Fruit Fruit::orange = Fruit::static_init( Fruit::orange, "orange" );
//  const Fruit Fruit::pear   = Fruit::static_init( Fruit::pear,   "pear"   );
//
// To simplify the syntax for initializing the static variables we can
// use a helper macro as shown below:
//
//  STDX_ENUM_ITEM( Fruit, apple  );
//  STDX_ENUM_ITEM( Fruit, orange );
//  STDX_ENUM_ITEM( Fruit, pear   );
//
// We can use enumerations just like a normal class. Here is an example
// where we define a fruit variable and test what kind of fruit it is.
//
//  Fruit fruit_a = Fruit::apple;
//  Fruit fruit_b = fruit_b;
//  if ( fruit_a == Fruit::apple )
//    std::cout << "fruit_b == apple" << std::endl;
//  else
//    std::cout << "fruit_b != apple" << std::endl;
//
// Let's clarify some terminology. Fruit is an "enumeration type", and
// apple is a an "enumeration item". In the above example, fruit_a is an
// "enumeration" of type Fruit. Essentially an enumeration type is just
// a class which derives from stdx::Enum<T> and the enumeration items
// are just static constant instances of the enumeration type.
//
// We need to be careful how we initialize the static constants since
// the initialization order is undefined. For example, if another class
// has a static data member which is an enumeration and initializes this
// enumeration with one of the enumeration items there is no guarentee
// that the enumeration item will already be initialized. We provide a
// free function called static_init that does the static initialization.
// If another class needs to access an enumeration at static
// initialization time it must use the static_access function. For
// example, assume the class TestClass wants to include a static data
// member which is an instance of the Fruit enumeration. It would use
// the following syntax:
//
//  class TestClass {
//    static Fruit s_fruit;
//  };
//
//  Fruit TestClass::s_fruit = Fruit::static_access( Fruit::apple );
//
// By using the static_access method we guarantee that the Fruit::apple
// enumeration item is initialized before initializing s_fruit. It would
// be incorrect to initialize the static data member directly using
// Fruit::apple like this:
//
//  Fruit TestClass::s_fruit = Fruit::apple; // Incorrect!
//
// In addition to static initialization, the static_init function also
// stores the name of the enumeration item as a string to enable
// inserting and extracting the enumeration from a stream. Note that the
// string format is just the enumeration item name without the full
// namespace qualification. This is used to support inserting and
// extracting enum items from streams. There is also a convenient
// get_items() static method which can be used to get a list of all the
// possible items for an enumeration. For example, this will print out
// all the possible fruit items.
//
//  std::vector<Fruit> fruits = Fruit::get_items();
//  for ( int idx = 0; idx < static_cast<int>(fruits.size()); ++idx )
//    std::cout << fruits.at(idx) << std::endl;
//
// Eventually we might want to add support to choose whether or not to
// include the prefix in the output.

#ifndef STDX_ENUM_H
#define STDX_ENUM_H

#include <iostream>
#include <vector>
#include <string>
#include <map>

namespace stdx {

  template < typename T >
  class Enum {

   public:

    Enum();

    // Useful if one wants to set up a jump table manually
    int get_id() const { return m_id; }

    // Return a vector of all of the possible items for this enumeration
    static std::vector<T> get_items();

    // Set the prefix to something other than the enumeration type
    static void set_prefix( const std::string& prefix );

    // Set the prefix to something other than the enumeration type
    static std::string get_prefix();

    // Methods for use during static initialization phase
    static const T& static_access( const T& t );
    static const T& static_init( const T& t, const std::string& name );

   private:

    // Insertion/extraction operators need access to private name table
    template < typename U >
    friend std::ostream& operator<<( std::ostream& os, const Enum<U>& rhs );

    template < typename U >
    friend std::istream& operator>>( std::istream& is, Enum<U>& rhs );

    // Make enumeration item from id
    static T mk_item( int id );

    // Static members
    static std::string& s_prefix();
    static std::vector<std::string>& s_names();
    static std::vector<std::pair<const T*,T> >& s_inits();
    static int& s_counter();

    // The actual enum id
    int m_id;

  };

  //----------------------------------------------------------------------
  // Non-member operators
  //----------------------------------------------------------------------

  template < typename T >
  std::ostream& operator<<( std::ostream& os, const Enum<T>& rhs );

  template < typename T >
  std::istream& operator>>( std::istream& is, Enum<T>& rhs );

  template < typename T >
  bool operator==( const Enum<T>& lhs, const Enum<T>& rhs );

  template < typename T >
  bool operator!=( const Enum<T>& lhs, const Enum<T>& rhs );

}

//------------------------------------------------------------------------
// STDX_ENUM_ITEM
//------------------------------------------------------------------------
// To manually initialize an enumeration item we use this syntax:
//
//  const Fruit Fruit::apple = Fruit::static_init(Fruit::apple,"apple");
//
// This is pretty cumbersome since we have to include "Fruit" four
// times and "apple" three times. To simplify the syntax (and avoid
// typos) we can use the STDX_ENUM_ITEM macro as follows:
//
//  STDX_ENUM_ITEM( Fruit, apple );
//

#define STDX_ENUM_ITEM( enum_, item_ ) \
  STDX_ENUM_ITEM_( enum_, item_ )

#include "stdx-Enum.inl"
#endif /* STDX_ENUM_H */

