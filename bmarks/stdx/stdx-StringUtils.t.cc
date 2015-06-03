//========================================================================
// stdx-StringUtils Unit Tests
//========================================================================

#include "stdx-StringUtils.h"
#include "utst.h"

//------------------------------------------------------------------------
// TestToStr
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestToStr )
{
  std::string str = "foo";

  UTST_CHECK_EQ( stdx::to_str(42),    "42"    );
  UTST_CHECK_EQ( stdx::to_str(42.42), "42.42" );
  UTST_CHECK_EQ( stdx::to_str(true),  "1"     );

  UTST_CHECK_EQ( stdx::to_str("foo"), "foo" );
  UTST_CHECK_EQ( stdx::to_str(str),   "foo" );

  UTST_CHECK_EQ( stdx::to_str("(",42,",",42,")"),     "(42,42)"     );
  UTST_CHECK_EQ( stdx::to_str("(",42,",",str,")"),    "(42,foo)"    );
  UTST_CHECK_EQ( stdx::to_str("(",42.42,",",str,")"), "(42.42,foo)" );
}

//------------------------------------------------------------------------
// TestFromStr
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestFromStr )
{
  using namespace stdx;

  // Check converting an int into a string

  UTST_CHECK_EQ( from_str<int>("4242"),   4242 );
  UTST_CHECK_EQ( from_str<int>(" 4242 "), 4242 );

  UTST_CHECK_THROW( EInvalidFromString, from_str<int>("42%") );
  UTST_CHECK_THROW( EInvalidFromString, from_str<int>("0b") );
  UTST_CHECK_THROW( EInvalidFromString, from_str<int>("test") );
  UTST_CHECK_THROW( EInvalidFromString, from_str<int>("0xfff") );

  // Check converting other standard types into a string

  UTST_CHECK_EQ( from_str<double>("42.42"),   42.42 );
  UTST_CHECK_EQ( from_str<double>(" 42.42 "), 42.42 );
  UTST_CHECK_EQ( from_str<short>("42"),       42    );
  UTST_CHECK_EQ( from_str<short>(" 42 "),     42    );

  UTST_CHECK_THROW( EInvalidFromString, from_str<double>("42..42") );
  UTST_CHECK_THROW( EInvalidFromString, from_str<short>("9999999999999") );

  // Check converting a string

  UTST_CHECK_EQ( from_str<std::string>("test"), "test" );
  UTST_CHECK_THROW( EInvalidFromString, from_str<std::string>("") );
}

//------------------------------------------------------------------------
// TestLowerUpper
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestLowerUpper )
{
  std::string str       = "Quick brOWn FOX";
  std::string str_lower = "quick brown fox";
  std::string str_upper = "QUICK BROWN FOX";

  UTST_CHECK_EQ( stdx::to_lower(str), str_lower );
  UTST_CHECK_EQ( stdx::to_upper(str), str_upper );

  UTST_CHECK_EQ( stdx::to_lower(stdx::to_upper(str)), str_lower );
  UTST_CHECK_EQ( stdx::to_upper(stdx::to_lower(str)), str_upper );
}

//------------------------------------------------------------------------
// TestPrefixSuffix
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestPrefixSuffix )
{
  UTST_CHECK(  stdx::has_prefix( "foo.bar",   "foo."    ) );
  UTST_CHECK(  stdx::has_prefix( " foo.bar",  " foo."   ) );
  UTST_CHECK( !stdx::has_prefix( "  foo.bar", " foo "   ) );
  UTST_CHECK(  stdx::has_prefix( "foo.bar",   "foo.bar" ) );
  UTST_CHECK(  stdx::has_prefix( "foo.bar",   ""        ) );
  UTST_CHECK( !stdx::has_prefix( "foo.bar",   "none"    ) );

  UTST_CHECK_EQ( stdx::remove_prefix("foo.bar","foo."),    "bar" );
  UTST_CHECK_EQ( stdx::remove_prefix("foo.bar","foo.bar"), ""    );

  UTST_CHECK(  stdx::has_suffix( "foo.bar",   ".bar"    ) );
  UTST_CHECK(  stdx::has_suffix( "foo.bar ",  ".bar "   ) );
  UTST_CHECK( !stdx::has_suffix( "foo.bar  ", " .bar "   ) );
  UTST_CHECK(  stdx::has_suffix( "foo.bar",   "foo.bar" ) );
  UTST_CHECK(  stdx::has_suffix( "foo.bar",   ""        ) );
  UTST_CHECK( !stdx::has_suffix( "foo.bar",   "none"    ) );

  UTST_CHECK_EQ( stdx::remove_suffix("foo.bar",".bar"),    "foo" );
  UTST_CHECK_EQ( stdx::remove_suffix("foo.bar","foo.bar"), ""    );
}

//------------------------------------------------------------------------
// TestTrimLeadingTrailing
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestTrimLeadingTrailing )
{
  std::string str1 = "  \t  foobar  \t\n";
  UTST_CHECK_EQ( stdx::trim_leading(str1),  "foobar  \t\n" );
  UTST_CHECK_EQ( stdx::trim_trailing(str1), "  \t  foobar" );
  UTST_CHECK_EQ( stdx::trim(str1),          "foobar"       );

  std::string str2 = " { foobar } ";
  UTST_CHECK_EQ( stdx::trim_leading(str2," {"),  "foobar } " );
  UTST_CHECK_EQ( stdx::trim_trailing(str2,"} "), " { foobar" );
  UTST_CHECK_EQ( stdx::trim(str2," {","} "),     "foobar"    );

  std::string str3 = " { foobar } ";
  UTST_CHECK_EQ( stdx::trim_leading(str3,""),  str3 );
  UTST_CHECK_EQ( stdx::trim_trailing(str3,""), str3 );
  UTST_CHECK_EQ( stdx::trim(str3,"",""),       str3 );

  std::string str4("");
  UTST_CHECK_EQ( stdx::trim_leading(str4),  str4 );
  UTST_CHECK_EQ( stdx::trim_trailing(str4), str4 );
  UTST_CHECK_EQ( stdx::trim(str4),          str4 );

  std::string str5 = " { x } ";
  UTST_CHECK_EQ( stdx::trim_leading(str5," {x"), "} "   );
  UTST_CHECK_EQ( stdx::trim_trailing(str5," }"), " { x" );
  UTST_CHECK_EQ( stdx::trim(str5," {x"," }"),    ""     );

  std::string str6 = "\"  \"";
  UTST_CHECK_EQ( stdx::trim_leading(str6," \t\""),  "" );
  UTST_CHECK_EQ( stdx::trim_trailing(str6," \t\""), "" );
  UTST_CHECK_EQ( stdx::trim(str6," \t\""," \t\""),  "" );
}

//------------------------------------------------------------------------
// TestSplit
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestSplit )
{
  using namespace stdx;
  using namespace std;

  std::vector<std::string> cvec1(3);
  cvec1.at(0) = "Quick";
  cvec1.at(1) = "brown";
  cvec1.at(2) = "fox";

  // Use spaces as delimiters

  vector<string> tvec1 = split( "Quick brown fox" );
  UTST_CHECK_CONT_EQ( tvec1, cvec1 );

  // Use extra spaces as delimiters

  vector<string> tvec2 = split( " Quick brown    fox  " );
  UTST_CHECK_CONT_EQ( tvec2, cvec1 );

  // Use spaces, newlines, and tabs as delimiters

  vector<string> tvec3 = split( " \t Quick\n  \t\n\t\t brown\n\nfox\n" );
  UTST_CHECK_CONT_EQ( tvec3, cvec1 );

  // Use commas as delimiters

  vector<string> tvec4 = split( "Quick,brown,fox", "," );
  UTST_CHECK_CONT_EQ( tvec4, cvec1 );
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv );
}

