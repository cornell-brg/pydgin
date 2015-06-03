//========================================================================
// utst::ITestCase : Abstract base class for test cases
//========================================================================
// A test case is a collection of checks which test a specific
// functionality of interest. Organizing checks into test cases helps
// the developer monitor and control the unit test. Please read the
// documentation in utst-uguide.txt for more information on how this
// class fits into the overall unit test framework.

#ifndef UTST_ITEST_CASE_H
#define UTST_ITEST_CASE_H

#include <string>

namespace utst {

  class ITestCase
  {

   public:

    //--------------------------------------------------------------------
    // Constructors/Destructors
    //--------------------------------------------------------------------

    // Virtual default destructor
    virtual ~ITestCase() { };

    //--------------------------------------------------------------------
    // Test case name
    //--------------------------------------------------------------------

    // Set the name of this test case
    virtual void set_name( const std::string& name ) = 0;

    // Return the name of this test case
    virtual std::string get_name() const = 0;

    //--------------------------------------------------------------------
    // Other memmber functions
    //--------------------------------------------------------------------

    // Return a dynamically allocated clone of this object
    virtual ITestCase* clone() const = 0;

    // Run the test case and output results to the test log
    virtual void run() = 0;

  };

}

#endif /* UTST_ITEST_CASE_H */

