//========================================================================
// stdx-BoundedQueue Unit Tests
//========================================================================

#include "stdx-BoundedQueue.h"
#include "utst.h"

//------------------------------------------------------------------------
// TestBasic
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestBasic )
{
  stdx::BoundedQueue<int> queue(3);

  UTST_CHECK_EQ( queue.get_max_size(), 3 );
  UTST_CHECK_EQ( queue.size(),  0 );
  UTST_CHECK( queue.empty() );
  UTST_CHECK( !queue.full() );

  queue.push( 1 );
  UTST_CHECK_EQ( queue.size(),  1 );
  UTST_CHECK_EQ( queue.back(),  1 );
  UTST_CHECK_EQ( queue.front(), 1 );
  UTST_CHECK( !queue.empty() );
  UTST_CHECK( !queue.full() );

  queue.push( 2 );
  UTST_CHECK_EQ( queue.size(),  2 );
  UTST_CHECK_EQ( queue.back(),  2 );
  UTST_CHECK_EQ( queue.front(), 1 );
  UTST_CHECK( !queue.empty() );
  UTST_CHECK( !queue.full() );

  queue.push( 3 );
  UTST_CHECK_EQ( queue.size(),  3 );
  UTST_CHECK_EQ( queue.back(),  3 );
  UTST_CHECK_EQ( queue.front(), 1 );
  UTST_CHECK( !queue.empty() );
  UTST_CHECK( queue.full() );

  queue.pop();
  UTST_CHECK_EQ( queue.size(),  2 );
  UTST_CHECK_EQ( queue.back(),  3 );
  UTST_CHECK_EQ( queue.front(), 2 );
  UTST_CHECK( !queue.empty() );
  UTST_CHECK( !queue.full() );

  queue.pop();
  UTST_CHECK_EQ( queue.size(),  1 );
  UTST_CHECK_EQ( queue.back(),  3 );
  UTST_CHECK_EQ( queue.front(), 3 );
  UTST_CHECK( !queue.empty() );
  UTST_CHECK( !queue.full() );

  queue.pop();
  UTST_CHECK_EQ( queue.size(),  0 );
  UTST_CHECK( queue.empty() );
  UTST_CHECK( !queue.full() );
}

//------------------------------------------------------------------------
// TestWrapAround
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestWrapAround )
{
  stdx::BoundedQueue<int> queue;
  queue.set_max_size(3);

  UTST_CHECK_EQ( queue.get_max_size(), 3 );
  UTST_CHECK_EQ( queue.size(),  0 );
  UTST_CHECK( queue.empty() );
  UTST_CHECK( !queue.full() );

  queue.push( 1 );
  UTST_CHECK_EQ( queue.size(),  1 );
  UTST_CHECK_EQ( queue.back(),  1 );
  UTST_CHECK_EQ( queue.front(), 1 );
  UTST_CHECK( !queue.empty() );
  UTST_CHECK( !queue.full() );

  queue.pop();
  UTST_CHECK_EQ( queue.size(),  0 );
  UTST_CHECK( queue.empty() );
  UTST_CHECK( !queue.full() );

  queue.push( 2 );
  UTST_CHECK_EQ( queue.size(),  1 );
  UTST_CHECK_EQ( queue.back(),  2 );
  UTST_CHECK_EQ( queue.front(), 2 );
  UTST_CHECK( !queue.empty() );
  UTST_CHECK( !queue.full() );

  queue.push( 3 );
  UTST_CHECK_EQ( queue.size(),  2 );
  UTST_CHECK_EQ( queue.back(),  3 );
  UTST_CHECK_EQ( queue.front(), 2 );
  UTST_CHECK( !queue.empty() );
  UTST_CHECK( !queue.full() );

  queue.pop();
  UTST_CHECK_EQ( queue.size(),  1 );
  UTST_CHECK_EQ( queue.back(),  3 );
  UTST_CHECK_EQ( queue.front(), 3 );
  UTST_CHECK( !queue.empty() );
  UTST_CHECK( !queue.full() );

  queue.pop();
  UTST_CHECK_EQ( queue.size(),  0 );
  UTST_CHECK( queue.empty() );
  UTST_CHECK( !queue.full() );
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv );
}

