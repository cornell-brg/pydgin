//========================================================================
// utst::ITestCase_BasicImpl<T> : Implementation helper for test cases
//========================================================================
// Please read the documentation in utst-uguide.txt for more information
// on how this class fits into the overall unit test framework.
//
// This is an implementation helper base class which means it implements
// some of the virtual functions in the abstract ITestCase base class
// but leaves others to be implemented by a concrete subclass. A
// developer can write a test case which inherits from this base class
// and only needs to implement a constructor and overload the protected
// the_test member function. Developers should make sure they set the
// name of the test case to something descriptive (the name of the
// subclass is usually appropriate).
//
// The reason this class is templated by the type of the subclass, is so
// that it can implement the clone member function. See the
// implementation if you are interested. The reason that subclasses
// should implemented the_test function instead of directly implementing
// the run function is because this helper class inserts some code
// before and after it calls the_test(). This extra code logs the start
// and end of the test case with the TestLog and also catches unexpected
// exceptions.
//
// There is a helper macro called UTST_TEST_CASE which makes it easier
// to create test cases. Here is a simple example of a test case which
// checks some basic functionality of the standard STL vector class.
//
//  UTST_AUTO_TEST_CASE( TestBasic )
//  {
//    std::vector<int> vec;
//
//    UTST_CHECK( vec.empty() );
//    UTST_CHECK_EQ( vec.size(), 0u );
//
//    vec.resize(3);
//    vec.at(0) = 0;
//    vec.at(1) = 1;
//    vec.at(2) = 2;
//
//    UTST_CHECK( !vec.empty() );
//    UTST_CHECK_EQ( vec.size(), 3u );
//    UTST_CHECK_EQ( vec.at(0), 0 );
//    UTST_CHECK_EQ( vec.at(1), 1 );
//    UTST_CHECK_EQ( vec.at(2), 2 );
//  }
//

#ifndef UTST_ITEST_CASE_BASIC_IMPL_H
#define UTST_ITEST_CASE_BASIC_IMPL_H

#include "utst-ITestCase.h"
#include <string>

namespace utst {

  template < typename T >
  class ITestCase_BasicImpl : public ITestCase
  {

   public:

    //--------------------------------------------------------------------
    // Constructors/Destructors
    //--------------------------------------------------------------------

    // Default constructor
    ITestCase_BasicImpl();

    // Virtual default destructor
    virtual ~ITestCase_BasicImpl();

    //--------------------------------------------------------------------
    // Test case name
    //--------------------------------------------------------------------

    // Set the name of this test case
    virtual void set_name( const std::string& name );

    // Return the name of this test case
    virtual std::string get_name() const;

    //--------------------------------------------------------------------
    // Other public member functions
    //--------------------------------------------------------------------

    // Return a dynamically allocated clone of this object
    virtual ITestCase* clone() const;

    // Run the test case and output results to the the TestLog
    virtual void run();

   protected:

    //--------------------------------------------------------------------
    // Protected member functions
    //--------------------------------------------------------------------

    // Subclasses should overload this function with actual test code
    virtual void the_test() = 0;

   private:

    std::string m_name;

  };

}

//------------------------------------------------------------------------
// UTST_TEST_CASE
//------------------------------------------------------------------------
// Macro to make creating simple test cases easier. Requires a code
// block (ie. wrapped in curly braces) after the macro. One can use the
// UTST_CHECK macros in the code block. The macro creates a new class
// with the given name and this class can be instantiated with a default
// constructor.
//
//  UTST_TEST_CASE( TestAddition )
//  {
//    UTST_CHECK( 1 + 1 == 2 );
//    UTST_CHECK_EQ( 1, 1 );
//  }
//

#define UTST_TEST_CASE( name_ ) \
  UTST_TEST_CASE_( name_ )

#include "utst-ITestCase_BasicImpl.inl"
#endif /* UTST_ITEST_CASE_BASIC_IMPL_H */

