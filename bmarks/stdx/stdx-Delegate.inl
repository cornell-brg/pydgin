//========================================================================
// stdx-Delegate.inl
//========================================================================

namespace stdx {

  //----------------------------------------------------------------------
  // StdDelegate
  //----------------------------------------------------------------------
  // The standard delegate works by saving a pointer to an object and a
  // member function pointer to the member function we want to
  // eventually call. The tricky part is that we don't want the type of
  // the delegate to depend on the type of the object pointer nor the
  // member function pointer. Otherwise the delegate would not be
  // polymorphic and the invoker would need to know type information
  // about the invoked code.
  //
  // To avoid the delegate depending on the type of the object pointer,
  // we cast the object pointer into a void pointer for storage in the
  // delegate. Normally this is a bad thing to do because it can destroy
  // type safety, but as we go through the implementation you will see
  // why the basic delegate is still perfectly typesafe.
  //
  // To avoid the delegate depending on the type of the member function
  // pointer, we store a pointer to a templated stub function instead.
  // The stub function looks like this:
  //
  //  template < typename T, void (T::*method)() >
  //  void stub( void* object_ptr );
  //
  // Although the stub function is templated by both the object type and
  // the member function type, its arguments and return type do _not_
  // depend on the template arguments. This means that the type
  // signature of the stub function also does not depend on the template
  // arguments. The type signature is just a function which takes a void
  // pointer and has no return value:
  //
  //  typedef void (*StubFptr)(void* object_ptr);
  //
  // The stub function implementation casts the void pointer passed in
  // as an argument back to a valid object pointer and then calls the
  // member function. They type information is embedded _inside_ the
  // stub function but it is not visible from the outside which is why
  // we can store it in a delegate in a polymorphic way.

  template < typename T, void (T::*method)() >
  void StdDelegate::bind( T* object_ptr )
  {
    m_object_ptr = object_ptr;
    m_stub_fptr  = &stub<T,method>;
  }

  inline void StdDelegate::invoke() const
  {
    // assert that neither of these are zero!
    (*m_stub_fptr)(m_object_ptr);
  }

  template < typename T, void (T::*method)() >
  void StdDelegate::stub( void* object_ptr )
  {
    T* p = static_cast<T*>(object_ptr);
    (p->*method)();
  }

  template < typename T, void (T::*method)() >
  StdDelegate mk_delegate( T* object_ptr )
  {
    StdDelegate delegate;
    delegate.bind<T,method>( object_ptr );
    return delegate;
  }

  //----------------------------------------------------------------------
  // NonStdDelegate
  //----------------------------------------------------------------------
  // The non-standard delegate uses a reinterpret_cast to first cast the
  // object pointer to a completely unrelated Generic object pointer,
  // and to then cast the member-function-pointer to a completely
  // unrelated Generic member-funcion-pointer. Although we could require
  // that give objects have a common base class, and then we could just
  // static_cast the pointers it is no more standard when we try to call
  // a derived member function through a base member function pointer.
  // Plus this makes the syntax more cumbersome because we have to pass
  // the base class as a template argument.

  template < typename T >
  void NonStdDelegate::bind( T* object_ptr, void (T::*method)() )
  {
    m_object_ptr = reinterpret_cast<Generic*>(object_ptr);
    m_mem_fptr   = reinterpret_cast<GenericMemFuncPtr>(method);
  }

  inline void NonStdDelegate::invoke() const
  {
    // assert that neither of these are zero!
    (m_object_ptr->*m_mem_fptr)();
  }

  template < class T >
  NonStdDelegate mk_delegate( T* object_ptr, void (T::*method)() )
  {
    NonStdDelegate delegate;
    delegate.bind( object_ptr, method );
    return delegate;
  }

}

