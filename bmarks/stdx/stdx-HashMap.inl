//========================================================================
// stdx-HashMap.inl
//========================================================================

namespace stdx {

  //----------------------------------------------------------------------
  // Constructors/Destructors
  //----------------------------------------------------------------------

  template <typename K, typename D>
  HashMap<K,D>::HashMap()
  { }

  //----------------------------------------------------------------------
  // begin/end
  //----------------------------------------------------------------------

  template <typename K, typename D>
  typename HashMap<K,D>::iterator HashMap<K,D>::begin()
  {
    return m_map.begin();
  }

  template <typename K, typename D>
  typename HashMap<K,D>::const_iterator HashMap<K,D>::begin() const
  {
    return m_map.begin();
  }

  template <typename K, typename D>
  typename HashMap<K,D>::iterator HashMap<K,D>::end()
  {
    return m_map.end();
  }

  template <typename K, typename D>
  typename HashMap<K,D>::const_iterator HashMap<K,D>::end() const
  {
    return m_map.end();
  }

  //----------------------------------------------------------------------
  // size
  //----------------------------------------------------------------------

  template <typename K, typename D>
  typename HashMap<K,D>::size_type HashMap<K,D>::size() const
  {
    return m_map.size();
  }

  //----------------------------------------------------------------------
  // empty
  //----------------------------------------------------------------------

  template <typename K, typename D>
  bool HashMap<K,D>::empty() const
  {
    return ( size() == 0u );
  }

  //----------------------------------------------------------------------
  // has_key
  //----------------------------------------------------------------------

  template <typename K, typename D>
  bool HashMap<K,D>::has_key( const HashMap<K,D>::key_type& key ) const
  {
    return ( m_map.find(key) != m_map.end() );
  }

  //----------------------------------------------------------------------
  // find
  //----------------------------------------------------------------------

  template <typename K, typename D>
  typename HashMap<K,D>::iterator
  HashMap<K,D>::find( const HashMap<K,D>::key_type& key )
  {
    return m_map.find(key);
  }

  template <typename K, typename D>
  typename HashMap<K,D>::const_iterator
  HashMap<K,D>::find( const HashMap<K,D>::key_type& key ) const
  {
    return m_map.find(key);
  }

  //----------------------------------------------------------------------
  // force_find
  //----------------------------------------------------------------------

  template <typename K, typename D>
  typename HashMap<K,D>::data_type&
  HashMap<K,D>::force_find( const HashMap<K,D>::key_type& key )
  {
    typename InternalMap::iterator itr = m_map.find(key);
    if ( itr == m_map.end() )
      STDX_M_THROW( EKeyNotFound, "Could not find key: " << key );

    return itr->second;
  }

  template <typename K, typename D>
  const typename HashMap<K,D>::data_type&
  HashMap<K,D>::force_find( const HashMap<K,D>::key_type& key ) const
  {
    typename InternalMap::const_iterator itr = m_map.find(key);
    if ( itr == m_map.end() )
      STDX_M_THROW( EKeyNotFound, "Could not find key: " << key );

    return itr->second;
  }

  //----------------------------------------------------------------------
  // operator[]
  //----------------------------------------------------------------------

  template <typename K, typename D>
  typename HashMap<K,D>::data_type&
  HashMap<K,D>::operator[]( const HashMap<K,D>::key_type& key )
  {
    return m_map[key];
  }

  //----------------------------------------------------------------------
  // force_insert
  //----------------------------------------------------------------------

  template <typename K, typename D>
  void HashMap<K,D>::force_insert( const HashMap<K,D>::key_type& key,
                                   const data_type& val )
  {
    typename InternalMap::iterator itr = m_map.find(key);
    if ( itr != m_map.end() )
      STDX_THROW( EKeyAlreadyPresent, "Key already present: " << key );

    m_map.insert( std::make_pair(key,val) );
  }

  //----------------------------------------------------------------------
  // erase
  //----------------------------------------------------------------------

  template <typename K, typename D>
  void HashMap<K,D>::erase( const HashMap<K,D>::key_type& key )
  {
    m_map.erase( m_map.find(key) );
  }

  template <typename K, typename D>
  void HashMap<K,D>::erase( HashMap<K,D>::iterator itr )
  {
    m_map.erase(itr);
  }

  template <typename K, typename D>
  void HashMap<K,D>::erase( HashMap<K,D>::iterator first,
                            HashMap<K,D>::iterator last )
  {
    m_map.erase(first,last);
  }

  //----------------------------------------------------------------------
  // clear
  //----------------------------------------------------------------------

  template <typename K, typename D>
  void HashMap<K,D>::clear()
  {
    m_map.clear();
  }

}

