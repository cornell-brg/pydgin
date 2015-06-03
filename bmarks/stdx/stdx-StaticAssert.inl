//========================================================================
// stdx-StaticAssert.inl
//========================================================================
// The implementation is pretty tricky and the syntax can be cumbersome
// which is why we provide the simple STDX_STATIC_ASSERT macro. Users
// should never really need to use the classes or macros in this file
// directly.

namespace stdx {

  //----------------------------------------------------------------------
  // StaticAssert
  //----------------------------------------------------------------------
  // We forward declare a new class called StaticAssert which takes one
  // template argument which should be the result from an assertion
  // check. Notice that we do not actually define the class - but
  // instead we only specialize the class when the template argument is
  // true. So although the class is forward declared - there is no
  // definition when the template argument is false.
  //
  // If we try and instantiate (and then use) this class with an
  // expression as the template argument which then evaluates to false
  // we will get an incomplete type error for StaticAssert<false>. If
  // the expression evaulates to true then we will not get an error
  // since a specialization exists for StaticAssert<true>. Here is an
  // example:
  //
  //  stdx::StaticAssert< 1 == 1 > test1; // Will compile
  //  stdx::StaticAssert< 1 == 2 > test2; // Will not compile
  //

  template < bool t_assertion_result >
  struct StaticAssert;

  template <>
  struct StaticAssert<true>
  { };

  //----------------------------------------------------------------------
  // StaticAssertWrapper
  //----------------------------------------------------------------------
  // Although we could just use StaticAssert class as shown above, we
  // don't actually want to instantiate these empty classes because we
  // want to guarantee that our static assertion checks produce no
  // code.
  //
  // So we use two tricks. First we can pass the type as an argument to
  // the built-in sizeof operator - but again we don't actually want to
  // call sizeof at run-time. So the trick we use is to define a typedef
  // for a class called StaticAssertWrapper which takes one integer
  // template argument. We can then call
  // sizeof(StaticAssert<assertion_check>) and the result is used as the
  // tempalte argument to StaticAssertWrapper. The result is that we
  // guarantee that the compiler checks the assertion and also that no
  // code is generated. This also means we can use these types of checks
  // almost anywhere. Here are some examples:
  //
  //  // This test will compile
  //  typedef stdx::StaticAssertWrapper<
  //            sizeof(stdx::StaticAssert< 1 == 1 >) > test1;
  //
  //  // This test will not compile
  //  typedef stdx::StaticAssertWrapper<
  //            sizeof(stdx::StaticAssert< 1 == 2 >) > test2;
  //
  // Note that we need unique typedef names. The STDX_STATIC_ASSERT
  // macro helps simplify the syntax and create unique typedef names.

  template < int x >
  struct StaticAssertWrapper
  { };

}

//------------------------------------------------------------------------
// STDX_STATIC_ASSERT
//------------------------------------------------------------------------
// The syntax using StaticAssertWrapper is pretty cumbersome, and the
// requirement for unique typedefs can be tricky. The STDX_STATIC_ASSERT
// macro simplifies the syntax and generates a typedef with the name
// stdx_static_assert_LINENUM where LINENUM is the line number of the
// assertion in the file. Note that this works fine for checks in
// functions and classes, but for checks at a toplevel namespace scope
// you might need to wrap your tests in a unique namespace to make sure
// that the typedefs are unique across all translation units.
//
// The extra STDX_STATIC_ASSERT_CONCAT macros are need to force the
// preprocessor to evaluate __LINE__ before concatenating the token for
// the typedef name.

#define STDX_STATIC_ASSERT_CONCAT_H1( a_, b_ ) a_##b_
#define STDX_STATIC_ASSERT_CONCAT_H0( a_, b_ ) \
  STDX_STATIC_ASSERT_CONCAT_H1( a_, b_ )

#define STDX_STATIC_ASSERT_( expr_ )                                   \
  typedef stdx::StaticAssertWrapper<                                   \
    sizeof(stdx::StaticAssert<static_cast<bool>((expr_))>) >           \
      STDX_STATIC_ASSERT_CONCAT_H0( stdx_static_assert_, __LINE__ );

