//========================================================================
// stdx-Enum.inl
//========================================================================
// The implementation of enumerations is a little intricate to give us
// the performance and syntax we desire while still guaranteeing that we
// never use an uninitialized enumeration during the static
// initialization phase. One solution to the static initialization
// problem is to use static member functions which return a reference to
// a _local_ static object (initialized within the member function) as
// opposed to directly exposing the static member as done above. See
// Item 47 in Scott Meyer's "Effective C++" for more information on this
// approach.
//
// Unforunately, there are two issues with this approach. First, it
// means every reference to an enumeration item requires a function call
// and second, the syntax for using an enumeration item looks like a
// function call instead of like a name. So for enumerations we use a
// different approach.
//
// During the static initialization phase a user should always
// initialize a specific enumeration item with the static_init function
// and should always access that enumeration item with the static_access
// function. The basic syntax for static_init is as follows:
//
//  const Fruit Fruit::apple = Fruit::static_init(Fruit::apple,"apple");
//
// We can ignore the name string for now. The static_init function is a
// static member of stdx::Enum<Fruit> and it accesses some static data
// in this base class. Since the base class is templated (by the
// enumeration type) the static data is _unique_ for each enumeration
// type. The static data includes an "inits" vector and a counter. The
// inits vector contains pairs of addresses and enumeration instances.
// Here is the interesting part. Each address is the address of one of
// the static const enumeration items (eg. Fruit::apple). So what
// static_init does is first take the address of the static const
// enumeration item which is passed in as a parameter (Fruit::apple) and
// look through the table to see if it finds an entry with the same
// address. If it doesn't exist then we create a new entry in the table
// with the address of Fruit::apple and a brand new enumeration
// instance. We make sure that the new enumeration instance has a unique
// id by using the static counter. Then we return a reference to the
// brand new enumeration instance. The assignment operator copies the
// brand new enumeration instance into the static constant Fruit::apple
// during the static initialization phase. If the address already exists
// in the table, then all we need to do is return a reference to the
// associated enumeration instance. How could this ever happen, you
// might ask? How could an entry already be in the table? The only way
// that could happen is if someone else already called static_init ...
// or if they called static_access!
//
// The static_access method is basically how other code can access the
// static variable during the static initialization phase. It is works
// the same as static_init except that there is no name string. So they
// key point is that it doesn't matter what order static_init and
// static_access are called during the static initialization phase since
// both functions check to see if they are the first to be called and if
// so create a new entry in the inits table otherwise they just return
// the already exisiting item in the table.
//
// The name string just gives us a way to convert enumerations to and
// from strings. We keep a static vector of name strings (in
// stdx::Enum<Fruit>) and use the unique id number to index into this
// table whenever we need to do the conversion.

#include "stdx-ReflectionUtils.h"
#include <cassert>
#include <iostream>

namespace stdx {

  //----------------------------------------------------------------------
  // Static member accessor methods
  //----------------------------------------------------------------------

  template < typename T >
  std::string& Enum<T>::s_prefix()
  {
    static std::string s_prefix = stdx::demangle_type<T>();
    return s_prefix;
  }

  template < typename T >
  std::vector<std::string>& Enum<T>::s_names()
  {
    static std::vector<std::string> s_names;
    return s_names;
  }

  template < typename T >
  std::vector<std::pair<const T*,T> >& Enum<T>::s_inits()
  {
    static std::vector< std::pair<const T*,T> > s_inits;
    return s_inits;
  }

  template < typename T >
  int& Enum<T>::s_counter()
  {
    static int s_counter = -1;
    return s_counter;
  }

  //----------------------------------------------------------------------
  // get_items()
  //----------------------------------------------------------------------

  template < typename T >
  std::vector<T> Enum<T>::get_items()
  {
    std::vector<T> items(s_inits().size());
    for ( int idx = 0; idx < static_cast<int>(s_inits().size()); ++idx )
      items.at(idx) = s_inits().at(idx).second;
    return items;
  }

  template < typename T >
  void Enum<T>::set_prefix( const std::string& prefix )
  {
    s_prefix() = prefix;
  }

  template < typename T >
  std::string Enum<T>::get_prefix()
  {
    return s_prefix();
  }

  //----------------------------------------------------------------------
  // Static access/init methods for enum items
  //----------------------------------------------------------------------

  template < typename T >
  const T& Enum<T>::static_access( const T& t )
  {

    // See if we have already initialized the given enumeration item
    // and if so just return a reference to the correct item
    typedef typename std::vector<std::pair<const T*,T> >::iterator ITR;
    for ( ITR itr = s_inits().begin(); itr != s_inits().end(); ++itr ) {
      if ( &t == itr->first )
        return itr->second;
    }

    // If we haven't already initialized the enumeration item then do so
    // and return a reference to the newly created item
    s_inits().push_back( std::make_pair( &t, mk_item(++s_counter()) ) );
    return s_inits().back().second;

  }

  template < typename T >
  const T& Enum<T>::static_init( const T& t, const std::string& name )
  {
    // Make sure the item is already initialized
    const T& item = static_access(t);

    // Add the name to the static names vector
    if ( item.m_id+1 > static_cast<int>(s_names().size()) )
      s_names().resize(item.m_id+1);
    s_names().at(item.m_id) = name;

    return item;
  }

  //----------------------------------------------------------------------
  // Constructors & Destructors
  //----------------------------------------------------------------------

  template < typename T >
  Enum<T>::Enum() : m_id(-1)
  { }

  //----------------------------------------------------------------------
  // Make enumeration item from id
  //----------------------------------------------------------------------

  template < typename T >
  T Enum<T>::mk_item( int id )
  {
    T item;
    item.m_id = id;
    return item;
  }

  //----------------------------------------------------------------------
  // operator <<
  //----------------------------------------------------------------------

  template < typename T >
  std::ostream& operator<<( std::ostream& os, const Enum<T>& rhs )
  {
    // Currently we always output the short form (ie no prefix).
    // Eventually we should add support to choose whether or not to
    // include the prefix in the output.

    if ( rhs.m_id == -1 )
      os << "UNDEFINED";
    else
      os << Enum<T>::s_names().at(rhs.m_id);
    return os;
  }

  //----------------------------------------------------------------------
  // operator >>
  //----------------------------------------------------------------------

  template < typename T >
  std::istream& operator>>( std::istream& is, Enum<T>& rhs )
  {
    std::string name;
    is >> name;

    // See if the name has the correct prefix and if so strip it off
    std::string prefix = Enum<T>::s_prefix()+"::";
    if (    ( name.length() > prefix.length() )
         && ( name.substr(0,prefix.length()) == prefix ) )
    {
      name = name.substr( prefix.length() );
    }

    // Find the name in the names vector and extract corresponding item
    std::vector<std::string>& names = Enum<T>::s_names();
    for ( int idx = 0; idx < static_cast<int>(names.size()); idx++ ) {
      if ( name == names[idx] ) {
        rhs = Enum<T>::mk_item(idx);
        return is;
      }
    }

    // If we couldn't find the name then signal an error
    is.clear( std::ios_base::badbit );
    return is;
  }

  //----------------------------------------------------------------------
  // operator ==
  //----------------------------------------------------------------------

  template < typename T >
  inline bool operator==( const Enum<T>& lhs, const Enum<T>& rhs )
  {
    return ( lhs.get_id() == rhs.get_id() );
  }

  //----------------------------------------------------------------------
  // operator !=
  //----------------------------------------------------------------------

  template < typename T >
  inline bool operator!=( const Enum<T>& lhs, const Enum<T>& rhs )
  {
    return ( lhs.get_id() != rhs.get_id() );
  }

}

//------------------------------------------------------------------------
// STDX_ENUM_ITEM
//------------------------------------------------------------------------

#define STDX_ENUM_ITEM_( enum_, item_ )                                 \
  const enum_ enum_::item_                                              \
    = enum_::static_init( enum_::item_, #item_ );                       \

