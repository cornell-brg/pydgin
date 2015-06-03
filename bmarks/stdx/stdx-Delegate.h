//========================================================================
// stdx-Delegate : Fast delegation of void member functions
//========================================================================
// The delegation design pattern enables one to choose what they want to
// execute but to defer the actual execution to another entity which
// does not need to know the details of what is actually being executed.
// One common way to implement delegation is with virtual functions. We
// can have an abstract base class with an invoke() method, and we can
// subclass the base class to provide different functionality. Then we
// can instantiate these derived classes and hand them off to another
// entity to actually do the execution (ie. call invoke). By
// representing the functionality as objects we can queue up the work,
// create a log, or even implement rollback.
//
// The biggest problem with using virtual functions to implement
// delegation is the performance overhead of allocating new objects on
// the heap and the extra indirection for virtual function calls. For
// some critical pieces of code this overhead can be unacceptable. This
// file contains delegate implementations, which although less flexible
// than the general dynamic dispatch mechanims, can be significantly
// faster. Note that these fast delegates are still type safe.
//
// The StdDelegate class is standard C++ and it will work for any object
// type but it only works for member functions with no return type and
// no arguments. It stores an object pointer and a pointer to a
// templated stub function. Assume we have some class Foo and we want to
// create a delegate which will call the Foo::bar() method when invoked.
// Here is how we would create the delegate using the mk_delegate helper
// function:
//
//  Foo foo;
//  Delegate delegate = mk_delegate<Foo,&Foo::bar>(&foo);
//  delegate.invoke();
//
// This type of delegate is not that fast because there is an extra
// function call for the templated stub function which cannot be inlined
// because we call it through a function pointer.
//
// This file also provides an even faster delegate named NonStdDelegate
// which uses a pretty weird and non-standard C++ trick. The trick is
// that if you have a pointer to an object of class A and a
// member-function-pointer for class A you can reinterpret_cast this to
// a pointer to an object of class B and a member-function-pointer for
// class B - and then you can actually apply the member-function-pointer
// to the object pointer! Even though the two classes have nothing to do
// with each other. This is still typesafe. You can't create a delegate
// with a member function pointer which doesn't correspond to the object
// pointer. And although using the pointers after they have been casted
// is non-standard it is surprisingly portable. I think it works with
// many compilers. Here is how we would create a non-standard delegate
// using the mk_delegate helper function:
//
//  Foo foo;
//  NonStdDelegate delegate = mk_delegate(&foo,&Foo::bar);
//  delegate.invoke();
//
// This delegate is faster because it is just involves a single member
// function call through a member function pointer. There is no extra
// indirection assuming the invoke method is inlined.

#ifndef STDX_DELEGATE_H
#define STDX_DELEGATE_H

#include <iostream>
#include <string>

namespace stdx {

  //----------------------------------------------------------------------
  // StdDelegate
  //----------------------------------------------------------------------
  // A delegate which conforms to the C++ standard but requires two
  // levels of interdirection and thus is slower.

  class StdDelegate {

   public:

    // Constructor
    StdDelegate() : m_object_ptr(0), m_stub_fptr(0) { }

    // Bind an object pointer and member function to this delegate
    template < typename T, void (T::*method)() >
    void bind( T* object_ptr );

    // Invoke delegate with stored object pointer and stub function
    void invoke() const;

   private:

    // Stub function
    template < typename T, void (T::*method)() >
    static void stub( void* object_ptr );

    // Type of the stub function
    typedef void (*StubFptr)(void* object_ptr);

    void*    m_object_ptr;
    StubFptr m_stub_fptr;

  };

  template < typename T, void (T::*method)() >
  StdDelegate mk_delegate( T* object_ptr );

  //----------------------------------------------------------------------
  // NonStdDelegate
  //----------------------------------------------------------------------
  // A delegate which does not conform to the C++ standard but requires
  // only one level of indirection and thus is faster. Although
  // non-standard I think it is relatively portable and should work with
  // most compilers.

  class NonStdDelegate {

   public:

    // Constructor
    NonStdDelegate() : m_object_ptr(0), m_mem_fptr(0) { }

    // Bind delegate to a object and member fuction
    template < typename T >
    void bind( T* object_ptr, void (T::*method)() );

    // Invoke delegate with stored base pointer and mem function pointer
    void invoke() const;

   private:

    // Generic class to cast all object pointers to
    struct Generic { };
    typedef void (Generic::*GenericMemFuncPtr)();

    Generic*          m_object_ptr;
    GenericMemFuncPtr m_mem_fptr;

  };

  template < typename T >
  NonStdDelegate mk_delegate( T* object_ptr, void (T::*method)() );

}

#include "stdx-Delegate.inl"
#endif /* STDX_DELEGATE_H */

