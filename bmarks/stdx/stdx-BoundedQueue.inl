//========================================================================
// stdx-BoundedQueue.inl
//========================================================================
// To implement a bounded queue with a fixed size circular buffer we can
// use two pointers which denote the front and back of the queue. As we
// push items into the queue we bump the back pointer and as we pop
// items we bump the front pointer. We need to be careful how we
// distinquish between when the queue is full and when the queue is
// empty. Without just the two pointers, these two states will look the
// same (ie. the two pointers will be equal). So we add an extra empty
// bit and manage that along with the pointers to disambiguate between a
// full and an empty queue.

#include "stdx-Exception.h"

namespace stdx {

  //----------------------------------------------------------------------
  // Constructors/Destructors
  //----------------------------------------------------------------------

  template <class T>
  BoundedQueue<T>::BoundedQueue()
  {
    m_back_idx  = 0;
    m_front_idx = 0;
    m_empty     = true;
  }

  template <class T>
  BoundedQueue<T>::BoundedQueue( int max_size )
  {
    m_back_idx  = 0;
    m_front_idx = 0;
    m_empty     = true;
    m_buf.resize(max_size);
  }

  //----------------------------------------------------------------------
  // max_size
  //----------------------------------------------------------------------

  template <class T>
  void BoundedQueue<T>::set_max_size( int max_size )
  {
    return m_buf.resize(max_size);
  }

  template <class T>
  int BoundedQueue<T>::get_max_size() const
  {
    return static_cast<int>(m_buf.size());
  }

  //----------------------------------------------------------------------
  // push/pop
  //----------------------------------------------------------------------

  template <class T>
  void BoundedQueue<T>::push( const T& val )
  {
    STDX_M_ASSERT( !full() );
    m_buf[m_back_idx] = val;
    ++m_back_idx;
    if ( m_back_idx == static_cast<int>(m_buf.size()) )
      m_back_idx = 0;
    m_empty = false;
  }

  template <class T>
  void BoundedQueue<T>::pop()
  {
    STDX_M_ASSERT( !empty() );
    ++m_front_idx;
    if ( m_front_idx == static_cast<int>(m_buf.size()) )
      m_front_idx = 0;
    m_empty = ( m_front_idx == m_back_idx );
  }

  //----------------------------------------------------------------------
  // front/back
  //----------------------------------------------------------------------

  template <class T>
  const T& BoundedQueue<T>::back() const
  {
    STDX_M_ASSERT( !empty() );
    int idx = m_back_idx - 1;
    if ( idx < 0 )
      idx = static_cast<int>(m_buf.size()-1);
    return m_buf[idx];
  }

  template <class T>
  T& BoundedQueue<T>::back()
  {
    STDX_M_ASSERT( !empty() );
    int idx = m_back_idx - 1;
    if ( idx < 0 )
      idx = static_cast<int>(m_buf.size()-1);
    return m_buf[idx];
  }

  template <class T>
  const T& BoundedQueue<T>::front() const
  {
    STDX_M_ASSERT( !empty() );
    return m_buf[m_front_idx];
  }

  template <class T>
  T& BoundedQueue<T>::front()
  {
    STDX_M_ASSERT( !empty() );
    return m_buf[m_front_idx];
  }

  //----------------------------------------------------------------------
  // Random element access
  //----------------------------------------------------------------------

  template <class T>
  T& BoundedQueue<T>::operator[]( typename std::vector<T>::size_type i )
  {
    return m_buf[i];
  }

  template <class T>
  const T& BoundedQueue<T>::operator[]( typename std::vector<T>::size_type i ) const
  {
    return m_buf[i];
  }

  template <class T>
  T& BoundedQueue<T>::at( typename std::vector<T>::size_type i )
  {
    return m_buf.at(i);
  }

  template <class T>
  const T& BoundedQueue<T>::at( typename std::vector<T>::size_type i ) const
  {
    return m_buf.at(i);
  }

  //----------------------------------------------------------------------
  // size/empty/full
  //----------------------------------------------------------------------

  template <class T>
  int BoundedQueue<T>::size() const
  {
    // Obviously when empty the size is zero

    if ( m_empty )
      return 0;

    // When the indices are equal we know the queue is full because we
    // already checked the empty bit, so it can't be empty

    if ( m_back_idx == m_front_idx )
      return static_cast<int>(m_buf.size());

    // If the back index is greater than the front index then the size
    // is just the difference between them

    if ( m_back_idx > m_front_idx )
      return m_back_idx - m_front_idx;

    // Otherwise the queue stradles the end of the buffer so we have to
    // be more careful how we calculate the size

    return ( static_cast<int>(m_buf.size())
               - ( m_front_idx - m_back_idx ) );
  }

  template <class T>
  bool BoundedQueue<T>::empty() const
  {
    return m_empty;
  }

  template <class T>
  bool BoundedQueue<T>::full() const
  {
    return (m_back_idx == m_front_idx) && !m_empty;
  }

}

