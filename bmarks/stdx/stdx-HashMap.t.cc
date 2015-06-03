//========================================================================
// stdx-HashMap Unit Tests
//========================================================================

#include "stdx-HashMap.h"
#include "utst.h"
#include <string>

//------------------------------------------------------------------------
// TestBasic
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestBasic )
{
  stdx::HashMap<std::string,int> hmap;
  UTST_CHECK( hmap.empty() );
  UTST_CHECK_EQ( hmap.size(), 0u );

  hmap["one"]   = 1;
  hmap["two"]   = 2;
  hmap["three"] = 3;
  hmap["four"]  = 4;
  hmap["five"]  = 5;

  UTST_CHECK( !hmap.empty() );
  UTST_CHECK_EQ( hmap.size(), 5u );

  UTST_CHECK( hmap.has_key("one") );
  UTST_CHECK( !hmap.has_key("zero") );

  UTST_CHECK_EQ( hmap["one"],   1 );
  UTST_CHECK_EQ( hmap["two"],   2 );
  UTST_CHECK_EQ( hmap["three"], 3 );
  UTST_CHECK_EQ( hmap["four"],  4 );
  UTST_CHECK_EQ( hmap["five"],  5 );
}

//------------------------------------------------------------------------
// TestIterators
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestIterators )
{
  stdx::HashMap<std::string,int> hmap1;
  hmap1["one"]   = 1;
  hmap1["two"]   = 2;
  hmap1["three"] = 3;
  hmap1["four"]  = 4;
  hmap1["five"]  = 5;

  stdx::HashMap<std::string,int> hmap2;
  hmap2["one"]   = 1;
  hmap2["two"]   = 2;
  hmap2["three"] = 3;
  hmap2["four"]  = 4;
  hmap2["five"]  = 5;

  stdx::HashMap<std::string,int>::iterator hitr1 = hmap1.begin();
  stdx::HashMap<std::string,int>::iterator hitr2 = hmap2.begin();
  while ( hitr1 != hmap1.end() ) {
    UTST_CHECK_EQ( hitr1->first, hitr2->first );
    UTST_CHECK_EQ( hitr1->second, hitr2->second );
    hitr1++;
    hitr2++;
  }
}

//------------------------------------------------------------------------
// TestForceFunctions
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestForceFunctions )
{
  stdx::HashMap<std::string,int> hmap;
  UTST_CHECK( hmap.empty() );
  UTST_CHECK_EQ( hmap.size(), 0u );

  hmap["one"] = 1;

  // Test force_insert

  hmap.force_insert("two",2);
  UTST_CHECK_THROW( stdx::EKeyAlreadyPresent, hmap.force_insert("two",2) );

  // Test force_find

  UTST_CHECK_EQ( hmap.force_find("two"), 2 );
  UTST_CHECK_THROW( stdx::EKeyNotFound, hmap.force_find("three") );
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv );
}

