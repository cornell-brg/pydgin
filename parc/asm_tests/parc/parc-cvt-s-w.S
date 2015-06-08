//=========================================================================
// parcv3-cvt-s-w.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Basic tests
        //-----------------------------------------------------------------

        TEST_RR_OP1( cvt.s.w, 0x4372a3d5, 0x4e86e548 )
        TEST_RR_OP1( cvt.s.w, 0x7474211a, 0x4ee8e842 )
        TEST_RR_OP1( cvt.s.w, 0x712ce9e3, 0x4ee259d4 )
        TEST_RR_OP1( cvt.s.w, 0x6148c087, 0x4ec29181 )
        TEST_RR_OP1( cvt.s.w, 0x1020a2a3, 0x4d810515 )
        TEST_RR_OP1( cvt.s.w, 0x35a8f903, 0x4e56a3e4 )
        TEST_RR_OP1( cvt.s.w, 0x3024509c, 0x4e409142 )
        TEST_RR_OP1( cvt.s.w, 0x34af471f, 0x4e52bd1c )
        TEST_RR_OP1( cvt.s.w, 0x35aec62b, 0x4e56bb19 )
        TEST_RR_OP1( cvt.s.w, 0x2ecd0cab, 0x4e3b3433 )
        TEST_RR_OP1( cvt.s.w, 0x4938474c, 0x4e92708f )
        TEST_RR_OP1( cvt.s.w, 0x6953f15b, 0x4ed2a7e3 )
        TEST_RR_OP1( cvt.s.w, 0x76dde468, 0x4eedbbc9 )
        TEST_RR_OP1( cvt.s.w, 0x02e0e165, 0x4c383859 )
        TEST_RR_OP1( cvt.s.w, 0x3f84ea01, 0x4e7e13a8 )
        TEST_RR_OP1( cvt.s.w, 0x129701ad, 0x4d94b80d )

        TEST_PARC_END
