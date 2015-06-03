//========================================================================
// utst-AutoUtils.inl
//========================================================================

#include "utst-ITestCase_BasicImpl.h"

//------------------------------------------------------------------------
// UTST_AUTO_TEST_CASE
//------------------------------------------------------------------------

#define UTST_AUTO_TEST_CASE_( name_ )                                   \
  struct name_ : public utst::ITestCase_BasicImpl<name_>                \
  {                                                                     \
    name_() { set_name( #name_ ); }                                     \
    void the_test();                                                    \
  };                                                                    \
  utst::AutoRegister ar_ ## name_( &utst::g_default_suite(), name_() ); \
  void name_::the_test()

//------------------------------------------------------------------------
// UTST_AUTO_EXTRA_TEST_CASE
//------------------------------------------------------------------------

#define UTST_AUTO_EXTRA_TEST_CASE_( suite_, name_ )                     \
  struct name_ : public utst::ITestCase_BasicImpl<name_>                \
  {                                                                     \
    name_() { set_name( #name_ ); }                                     \
    void the_test();                                                    \
  };                                                                    \
  utst::AutoRegister ar_ ## name_( &utst::g_ ## suite_ ## _suite(),     \
                                   name_() );                           \
  void name_::the_test()

