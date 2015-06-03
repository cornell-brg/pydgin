//========================================================================
// pinfo-ProgramInfo Unit Tests
//========================================================================

#include "pinfo-ProgramInfo.h"
#include "utst.h"

//------------------------------------------------------------------------
// TestArgFlag
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestArgFlag )
{
  pinfo::ProgramInfo pi;

  pi.add_arg( "-test-flag", NULL, NULL, "test flag" );
  UTST_CHECK( !pi.get_flag( "-test-flag" ) );

  // I guess you have to set flags to tbe the name of the flag. Weird.
  pi.set_value( "-test-flag", "-test-flag" );
  UTST_CHECK( pi.get_flag( "-test-flag" ) );

  pi.set_value( "-test-flag", "0" );
  UTST_CHECK( !pi.get_flag( "-test-flag" ) );
}

//------------------------------------------------------------------------
// TestArgLong
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestArgLong )
{
  pinfo::ProgramInfo pi;

  pi.add_arg( "-test-long", "long", "-42", "test long" );
  UTST_CHECK_EQ( pi.get_long( "-test-long" ), -42 );

  pi.set_value( "-test-long", "32" );
  UTST_CHECK_EQ( pi.get_long( "-test-long" ), 32 );
}

//------------------------------------------------------------------------
// TestArgUlong
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestArgUlong )
{
  pinfo::ProgramInfo pi;

  pi.add_arg( "-test-ulong", "ulong", "42", "test ulong" );
  UTST_CHECK_EQ( pi.get_ulong( "-test-ulong" ), 42 );

  pi.set_value( "-test-ulong", "32" );
  UTST_CHECK_EQ( pi.get_ulong( "-test-ulong" ), 32 );
}

//------------------------------------------------------------------------
// TestArgString
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestArgString )
{
  pinfo::ProgramInfo pi;

  pi.add_arg( "-test-string", "string", "foo", "test string" );
  UTST_CHECK_EQ( pi.get_string( "-test-string" ), "foo" );

  pi.set_value( "-test-string", "bar" );
  UTST_CHECK_EQ( pi.get_string( "-test-string" ), "bar" );
}

//------------------------------------------------------------------------
// TestParseArgs
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestParseArgs )
{
  pinfo::ProgramInfo pi;

  pi.add_arg( "-test-flag",   NULL,     NULL,  "test flag"   );
  pi.add_arg( "-test-long",   "long",   "-42", "test long"   );
  pi.add_arg( "-test-ulong",  "ulong",  "42",  "test ulong"  );
  pi.add_arg( "-test-string", "string", "foo", "test string" );
  pi.add_arg( "1",            "pos1",   NULL,  "pos1"        );
  pi.add_arg( "2",            "pos2",   NULL,  "pos2"        );

  const char* argv[]
    = { "TestParseArgs",
        "-test-flag",
        "pos1-value",
        "-test-long",   "-32",
        "-test-ulong",  "32",
        "-test-string", "bar",
        "pos2-value" };

  pi.parse_args( 10, const_cast<char**>(argv) );

  UTST_CHECK_EQ( pi.get_flag   ( "-test-flag"   ), 1            );
  UTST_CHECK_EQ( pi.get_long   ( "-test-long"   ), -32          );
  UTST_CHECK_EQ( pi.get_ulong  ( "-test-ulong"  ), 32           );
  UTST_CHECK_EQ( pi.get_string ( "-test-string" ), "bar"        );
  UTST_CHECK_EQ( pi.get_string ( "1" ),            "pos1-value" );
  UTST_CHECK_EQ( pi.get_string ( "2" ),            "pos2-value" );
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv );
}

