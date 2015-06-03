//========================================================================
// stdx-ImplPtr.inl
//========================================================================

#include "stdx-Exception.h"

namespace stdx {

  //----------------------------------------------------------------------
  // DefaultAllocationPolicy
  //----------------------------------------------------------------------

  template < typename Impl >
  Impl* DefaultAllocationPolicy<Impl>::create() const
  {
    return new Impl();
  }

  template < typename Impl >
  Impl* DefaultAllocationPolicy<Impl>::copy( Impl* t ) const
  {
    STDX_ASSERT( t != 0 );
    return new Impl(*t);
  }

  template < typename Impl >
  void DefaultAllocationPolicy<Impl>::destroy( Impl* t ) const
  {
    delete t;
  }

  template < typename Impl >
  DefaultAllocationPolicy<Impl>&
  DefaultAllocationPolicy<Impl>::instance()
  {
    static DefaultAllocationPolicy traits;
    return traits;
  }

  //----------------------------------------------------------------------
  // NoCreateAllocationPolicy
  //----------------------------------------------------------------------

  template < typename Impl >
  Impl* NoCreateAllocationPolicy<Impl>::create() const
  {
    STDX_ASSERT( false );
    return 0;
  }

  template < typename Impl >
  Impl* NoCreateAllocationPolicy<Impl>::copy( Impl* t ) const
  {
    STDX_ASSERT( t != 0 );
    return new Impl(*t);
  }

  template < typename Impl >
  void NoCreateAllocationPolicy<Impl>::destroy( Impl* t ) const
  {
    delete t;
  }

  template < typename Impl >
  NoCreateAllocationPolicy<Impl>&
  NoCreateAllocationPolicy<Impl>::instance()
  {
    static NoCreateAllocationPolicy traits;
    return traits;
  }

  //----------------------------------------------------------------------
  // ImplPtr : Constructors/Destructors
  //----------------------------------------------------------------------

  template < typename Impl >
  ImplPtr<Impl>::ImplPtr( IDynamicAllocationPolicy<Impl>* alloc_policy )
  {
    m_alloc_policy = alloc_policy;
    m_ptr          = m_alloc_policy->create();
  }

  template < typename Impl >
  ImplPtr<Impl>::ImplPtr( Impl* ptr,
                          IDynamicAllocationPolicy<Impl>* alloc_policy )
  {
    m_alloc_policy = alloc_policy;
    m_ptr          = ptr;
  }

  template < typename Impl >
  ImplPtr<Impl>::ImplPtr( const ImplPtr& ptr )
  {
    m_alloc_policy = ptr.m_alloc_policy;
    m_ptr          = ptr.m_alloc_policy->copy( ptr.m_ptr );
  }

  template < typename Impl >
  ImplPtr<Impl>::~ImplPtr()
  {
    m_alloc_policy->destroy( m_ptr );
  }

  //----------------------------------------------------------------------
  // ImplPtr : Copy/Assignment operators
  //----------------------------------------------------------------------

  template < typename Impl >
  ImplPtr<Impl>& ImplPtr<Impl>::operator=( const ImplPtr& ptr )
  {
    Impl* tmp_ptr = ptr.m_alloc_policy->copy( ptr.m_ptr );
    m_alloc_policy->destroy( m_ptr );
    m_ptr = tmp_ptr;
    m_alloc_policy = ptr.m_alloc_policy;
    return *this;
  }

}

