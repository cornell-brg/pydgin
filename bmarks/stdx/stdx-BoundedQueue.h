//========================================================================
// stdx-BoundedQueue : Queue with run-time defined size
//========================================================================
// There are variety of ways to use queues in our programs. We can
// simply use an STL list or dequeu, but both of these can require
// dynamic memory allocation when pushing and popping elements. This
// bounded queue preallocates a certain amount of space so that no
// dynamic memory allocation is needed when actually pushing and popping
// elements. The implementation then uses a circular buffer to store the
// queue elements. Pushing into a full queue or popping from an empty
// queue will cause an assertion, so a user should use the empty() and
// full() accessor member functions first.

#ifndef STDX_BOUNDED_QUEUE_H
#define STDX_BOUNDED_QUEUE_H

#include <vector>

namespace stdx {

  template < typename T >
  class BoundedQueue {

   public:

    //--------------------------------------------------------------------
    // Constructors/Destructors
    //--------------------------------------------------------------------

    BoundedQueue();
    BoundedQueue( int max_size );

    //--------------------------------------------------------------------
    // max_size
    //--------------------------------------------------------------------
    // The max size is the maximum number of elements this bounded queue
    // can hold. If max size elements are pushed into the queue then it
    // is full and an additional push will throw a debug assertion.

    void set_max_size( int max_size);
    int  get_max_size() const;

    //--------------------------------------------------------------------
    // push/pop
    //--------------------------------------------------------------------
    // Elements are pushed onto the back of the queue and are popped
    // from the front of the queue. A debug assertion is thrown if you
    // push onto a full queue or pop from an empty queue.

    void push( const T& val );
    void pop();

    //--------------------------------------------------------------------
    // front/back
    //--------------------------------------------------------------------

    const T& back() const;
    T& back();

    const T& front() const;
    T& front();

    //--------------------------------------------------------------------
    // Random element access
    //--------------------------------------------------------------------

    T& operator[]( typename std::vector<T>::size_type i );
    const T& operator[]( typename std::vector<T>::size_type i ) const;

    T& at( typename std::vector<T>::size_type i );
    const T& at( typename std::vector<T>::size_type i ) const;

    //--------------------------------------------------------------------
    // size/empty/full
    //--------------------------------------------------------------------

    int  size()  const;
    bool empty() const;
    bool full()  const;

   private:

    int  m_back_idx;
    int  m_front_idx;
    bool m_empty;

    std::vector<T> m_buf;

  };

}

#include "stdx-BoundedQueue.inl"
#endif /* STDX_BOUNDED_QUEUE_H */

