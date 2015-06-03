//========================================================================
// stdx-ImplPtr : Smart pointer for handle/body pattern
//========================================================================
// The handle/body pattern is a useful idiom for truly separating a
// class interface from its implementation. With a traditional C++ class
// changes to the private data member type or adding new private members
// will require all users of the class to recompile - even though this
// is strictly an implementation change! The handle/body pattern stores
// just a pointer in an outer (handle) class and this pointer points to
// an inner (body) class. The body class contains all implemenation
// objects. This works well, but a programmer must be careful to
// correctly allocate/deallocate the body class and manage
// copy/assigment operators. The ImplPtr class helps with these issues.
// An example of using the ImplPtr in the header file follows:
//
//  class Foo {
//
//   public:
//    // public members here ...
//
//   private:
//    struct Impl;
//    stdx::ImplPtr<Impl> impl;
//
//  };
//
// The programmer then defines the nested Impl struct in the source
// file. The policy for creating, copying, and destroying the Impl
// struct is set with a dynamic allocation policy class. These policy
// classes implement the IDynamicAllocationPolicy abstract
// base class's three methods:
//
//  - create  : Dynamically allocate new Impl struct
//  - copy    : Copy an Impl struct
//  - destroy : Destroy an Impl struct
//
// As opposed to more static policy classes which are passed as template
// parameters, the dynamic allocation policy class is passed as a
// parameter to the ImplPtr constructor. The policy needs to be dynamic
// so as to avoid creating, copying, or destroying an incomplete type.
// It's the key to the compile time decoupling. See the source file for
// more information.
//
// Currently there are two dynamic allocation polices. The
// DefaultAllocationPolicy creates new Impl objects by dynamically
// allocating them with the default Impl constructor. This policy copies
// Impl objects by dynamically allocating a new Impl struct with the
// default copy constructor, and destroys Impl objects with the delete
// operator. This copy policy means that copying an object which uses an
// ImplPtr (eg. Foo) creates a copy of the ImplPtr and the Impl struct
// as well. The NoCreateAllocationPolicy is the same as the default
// policy, except that the create method does nothing. It assumes that
// Impl structs are created explicitly in the constructor to the the
// ImplPtr. This is useful when the Impl struct contains members which
// do not have default constructors, and thus the Impl struct itself has
// no default constructor.
//
// We can imagine adding more policies in the future. For example, we
// could add a policy which implemets the counted body pattern by
// keeping a single reference count for the implemenation structs
// instead of copying them. Or we could implement a copy-on-write
// pattern.
//
// This class is loosely based on a previously proposed impl_ptr class
// by Peter Dimov on the boost mailing lists. I've simplified things and
// included create functions so that classes which use the pimpl idiom
// do not need to explicitly allocate the impl class.
// http://groups.yahoo.com/group/boost/files/impl_ptr

#ifndef STDX_IMPL_PTR_H
#define STDX_IMPL_PTR_H

namespace stdx {

  //----------------------------------------------------------------------
  // IDynamicAllocationPolicy
  //----------------------------------------------------------------------

  template < typename Impl >
  class IDynamicAllocationPolicy {
   public:

    virtual ~IDynamicAllocationPolicy() { }
    virtual Impl* create() const = 0;
    virtual Impl* copy( Impl* ) const = 0;
    virtual void  destroy( Impl* ) const = 0;

  };

  //----------------------------------------------------------------------
  // DefaultAllocationPolicy
  //----------------------------------------------------------------------
  // The default allocation policy creates new Impl objects by
  // dynamically allocating them with the default Impl constructor. This
  // policy also copies Impl objects by dynamically allocating a new
  // Impl struct with the default copy constructor, and destroys Impl
  // objects with the delete operator. This policy requires that the
  // Impl struct has a default constructor and a copy constructor.

  template < typename Impl >
  class DefaultAllocationPolicy : public IDynamicAllocationPolicy<Impl> {
   public:

    Impl* create() const;
    Impl* copy( Impl* t ) const;
    void  destroy( Impl* t ) const;
    static DefaultAllocationPolicy& instance();

  };

  //----------------------------------------------------------------------
  // NoCreateAllocationPolicy
  //----------------------------------------------------------------------
  // The no create allocation policy cannot create Impl object's itself.
  // It assumes that the Impl objects are created some other way. This
  // policy also copies Impl objects by dynamically allocating a new
  // Impl struct with the default copy constructor, and destroys Impl
  // objects with the delete operator.

  template < typename Impl >
  class NoCreateAllocationPolicy : public IDynamicAllocationPolicy<Impl> {
   public:

    Impl* create() const;
    Impl* copy( Impl* t ) const;
    void  destroy( Impl* t ) const;
    static NoCreateAllocationPolicy& instance();

  };

  //----------------------------------------------------------------------
  // ImplPtr
  //----------------------------------------------------------------------

  template < typename Impl >
  class ImplPtr {

   public:

    // Constructor/Destructors

    ImplPtr( IDynamicAllocationPolicy<Impl>* m_alloc_policy
               = &DefaultAllocationPolicy<Impl>::instance() );

    ImplPtr( Impl* ptr, IDynamicAllocationPolicy<Impl>* m_alloc_policy
                          = &NoCreateAllocationPolicy<Impl>::instance() );

    ImplPtr( const ImplPtr& ptr );

    ~ImplPtr();

    // Copy/assignment

    ImplPtr& operator=( const ImplPtr& ptr );

    // Pointer operators

    Impl* operator->() { return m_ptr; }
    const Impl* operator->() const { return m_ptr; }

    Impl& operator*() { return *m_ptr; }
    const Impl& operator*() const { return *m_ptr; }

   private:

    Impl* m_ptr;
    IDynamicAllocationPolicy<Impl>* m_alloc_policy;

  };

}

#include "stdx-ImplPtr.inl"
#endif /* STDX_IMPL_PTR_H */

