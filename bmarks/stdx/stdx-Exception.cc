//========================================================================
// stdx-Exception.cc
//========================================================================

#include "stdx-Exception.h"
#include <iostream>

namespace stdx {

  //----------------------------------------------------------------------
  // terminate
  //----------------------------------------------------------------------
  // We use this cute trick of using a throw without an operand to
  // rethrow the exception which caused us to call terminate. This
  // allows us to selectively execute code based on the exception type
  // even though the exception was not passed into the terminate
  // function. This also means it is invalid to call terminate except
  // from within a catch block.

  void terminate()
  {
    try { throw; }
    catch ( std::exception& e ) {
      std::cout << " ERROR: Caught unexpected std::exception\n";
      std::cout << e.what();
    }
    catch ( stdx::IException& e ) {
      std::cout << " ERROR: Caught unexpected stdx::IException\n";
      std::cout << e.what();
    }
    catch ( ... ) {
      std::cout << " ERROR: Caught unexpected exception\n";
    }
    std::cout << std::flush;
    std::abort();
  }

  //----------------------------------------------------------------------
  // set_terminate
  //----------------------------------------------------------------------

  void set_terminate( std::terminate_handler handler )
  {
    std::set_terminate( handler );
  }

}

