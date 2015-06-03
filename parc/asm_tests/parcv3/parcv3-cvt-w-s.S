//=========================================================================
// parcv3-cvt-w-s.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Basic tests
        //-----------------------------------------------------------------

        TEST_RR_OP1( cvt.w.s, 0xceb81b59, 0xa3f25380 )
        TEST_RR_OP1( cvt.w.s, 0x4edbd694, 0x6deb4a00 )
        TEST_RR_OP1( cvt.w.s, 0xcbdcaba4, 0xfe46a8b8 )
        TEST_RR_OP1( cvt.w.s, 0xcef782c3, 0x843e9e80 )
        TEST_RR_OP1( cvt.w.s, 0x4e49a70e, 0x3269c380 )
        TEST_RR_OP1( cvt.w.s, 0x4ec737ee, 0x639bf700 )
        TEST_RR_OP1( cvt.w.s, 0xceeb438e, 0x8a5e3900 )
        TEST_RR_OP1( cvt.w.s, 0x4d702eb0, 0x0f02eb00 )
        TEST_RR_OP1( cvt.w.s, 0x4ed09953, 0x684ca980 )
        TEST_RR_OP1( cvt.w.s, 0xcdd2e959, 0xe5a2d4e0 )
        TEST_RR_OP1( cvt.w.s, 0xce576337, 0xca273240 )
        TEST_RR_OP1( cvt.w.s, 0xce34724e, 0xd2e36c80 )
        TEST_RR_OP1( cvt.w.s, 0xcef29d11, 0x86b17780 )
        TEST_RR_OP1( cvt.w.s, 0xcea9b70b, 0xab247a80 )
        TEST_RR_OP1( cvt.w.s, 0x4ef26b78, 0x7935bc00 )
        TEST_RR_OP1( cvt.w.s, 0xcc30dba0, 0xfd3c9180 )

        TEST_PARC_END
