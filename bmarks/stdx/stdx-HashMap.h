//========================================================================
// stdx-HashMap : Wraper class around either a hash table or map
//========================================================================
// A simple wrapper class which represents a hash table. The key
// advantage of this class is that if it is used on older systems it
// will wrap a standard STL map, but on newer systems with the STL
// hash_map extension, it will wrap a hash_map creating a true hash
// table. It uses the default hash function and equality function for
// hash_maps and the default comparison function for STL maps so if you
// want to use anything other than these you will need to explicitly
// choose a hash_map or a map.
//
// The HashMap works just like a normal STL map container. For example,
// this is how we can insert key,value pairs into the HashMap and then
// extract them:
//
//  stdx::HashMap<std::string,int> hmap;
//  hmap["one"]   = 1;
//  hmap["two"]   = 2;
//  hmap["three"] = 3;
//
//  std::cout << hmap["one"]   << ","
//            << hmap["two"]   << ","
//            << hmap["three"] << std::endl;
//
// The HashMap has a couple extensions not found in the standard map
// container. First, it includes a has_key method which returns true or
// false based on whether or not the map contains the given key. Second,
// it contains a force_find/force_insert methods which throw an
// exception if the given key is already present/not-present
// repsectively.
//
// TODO:
//  - Memoize last key accessed with has_key for use in find()
//

#ifndef STDX_HASH_MAP_H
#define STDX_HASH_MAP_H

#include "stdx-config.h"
#include "stdx-Exception.h"
#include <map>

#ifdef STDX_HAVE_TR1_UNORDERED_MAP
  #include <tr1/unordered_map>
#endif

namespace stdx {

  //======================================================================
  // Exceptions
  //======================================================================

  struct EKeyNotFound       : public stdx::Exception { };
  struct EKeyAlreadyPresent : public stdx::Exception { };

  //======================================================================
  // HashMap
  //======================================================================

  template <typename Key, typename Data>
  class HashMap {

    //--------------------------------------------------------------------
    // InternalMap typedef
    //--------------------------------------------------------------------

   private:

    #ifdef STDX_HAVE_TR1_UNORDERED_MAP
      typedef std::tr1::unordered_map<Key,Data> InternalMap;
    #else
      typedef std::map<Key,Data> InternalMap;
    #endif

   public:

    //--------------------------------------------------------------------
    // Typedefs
    //--------------------------------------------------------------------

    typedef Key                                  key_type;
    typedef Data                                 data_type;
    typedef std::pair<const Key, Data>           value_type;
    typedef typename InternalMap::iterator       iterator;
    typedef typename InternalMap::const_iterator const_iterator;
    typedef typename InternalMap::size_type      size_type;
    typedef value_type&                          reference;
    typedef const value_type&                    const_reference;

    //--------------------------------------------------------------------
    // Constructors/Destructors
    //--------------------------------------------------------------------

    HashMap();

    //--------------------------------------------------------------------
    // Accessors
    //--------------------------------------------------------------------

    // Standard begin and end methods

    iterator       begin();
    const_iterator begin() const;

    iterator       end();
    const_iterator end() const;

    // Methods to check size of hash map

    size_type size() const;
    bool      empty() const;

    // New explicit check to see if hash map has given key

    bool has_key( const key_type& key ) const;

    // Find methods return end() if not found

    iterator       find( const key_type& key );
    const_iterator find( const key_type& key ) const;

    // Force find throws EKeyNotFound exception if key not present

    data_type&       force_find( const key_type& key );
    const data_type& force_find( const key_type& key ) const;

    //--------------------------------------------------------------------
    // Mutators
    //--------------------------------------------------------------------

    // The [] operator returns a reference to the data associated with
    // the given key. If key doesn't exist then we create a new data
    // item using the default constructor.

    data_type& operator[]( const key_type& key );

    // Force insert throws EKeyAlreadyPresent exception if the key is
    // already in the hash map

    void force_insert( const key_type& key, const data_type& val );

    // Erase methods

    void erase( const key_type& key );
    void erase( iterator itr );
    void erase( iterator first, iterator last );

    // Clear the entire hash map

    void clear();

   private:

    InternalMap m_map;

  };

}

#include "stdx-HashMap.inl"
#endif /* STDX_HASH_MAP_H */

