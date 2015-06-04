//=========================================================================
// parcv3-c-eq-s.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Arithmetic tests
        //-----------------------------------------------------------------

        TEST_RR_OP( c.eq.s, 0x3f800000, 0x3f800000, 0x00000001 )
        TEST_RR_OP( c.eq.s, 0x40000000, 0x40000000, 0x00000001 )
        TEST_RR_OP( c.eq.s, 0x43050800, 0x43030800, 0x00000000 )
        TEST_RR_OP( c.eq.s, 0x40003450, 0x40002340, 0x00000000 )
        TEST_RR_OP( c.eq.s, 0xdeadbeef, 0xcafebabe, 0x00000000 )
        TEST_RR_OP( c.eq.s, 0xdeadbeef, 0xdeadbeef, 0x00000001 )
        TEST_RR_OP( c.eq.s, 0xfafafafa, 0xfbfbfbfb, 0x00000000 )

        //-----------------------------------------------------------------
        // Source/Destination tests
        //-----------------------------------------------------------------

        TEST_RR_SRC0_EQ_DEST( c.eq.s, 0x40003450, 0x40003450, 0x00000001 )
        TEST_RR_SRC1_EQ_DEST( c.eq.s, 0xdeadbeef, 0xcafebabe, 0x00000000 )
        TEST_RR_SRCS_EQ_DEST( c.eq.s, 0xdeadbeef, 0x00000001 )

        //-----------------------------------------------------------------
        // Bypassing tests
        //-----------------------------------------------------------------

        TEST_RR_DEST_BYP( 0, c.eq.s, 0x43050800, 0x43030800, 0x00000000 )
        TEST_RR_DEST_BYP( 1, c.eq.s, 0x40003450, 0x40003450, 0x00000001 )
        TEST_RR_DEST_BYP( 2, c.eq.s, 0xdeadbeef, 0xcafebabe, 0x00000000 )

        TEST_RR_SRC01_BYP( 0, 0, c.eq.s, 0x3f800000, 0x3f800000, 0x00000001 )
        TEST_RR_SRC01_BYP( 0, 1, c.eq.s, 0x40000000, 0x40000000, 0x00000001 )
        TEST_RR_SRC01_BYP( 0, 2, c.eq.s, 0x43050800, 0x43030800, 0x00000000 )
        TEST_RR_SRC01_BYP( 1, 0, c.eq.s, 0x40003450, 0x40002340, 0x00000000 )
        TEST_RR_SRC01_BYP( 1, 1, c.eq.s, 0xdeadbeef, 0xcafebabe, 0x00000000 )
        TEST_RR_SRC01_BYP( 2, 0, c.eq.s, 0xdeadbeef, 0xdeadbeef, 0x00000001 )

        TEST_RR_SRC10_BYP( 0, 0, c.eq.s, 0x3f800000, 0x3f800000, 0x00000001 )
        TEST_RR_SRC10_BYP( 0, 1, c.eq.s, 0x40000000, 0x40000000, 0x00000001 )
        TEST_RR_SRC10_BYP( 0, 2, c.eq.s, 0x43050800, 0x43030800, 0x00000000 )
        TEST_RR_SRC10_BYP( 1, 0, c.eq.s, 0x40003450, 0x40002340, 0x00000000 )
        TEST_RR_SRC10_BYP( 1, 1, c.eq.s, 0xdeadbeef, 0xcafebabe, 0x00000000 )
        TEST_RR_SRC10_BYP( 2, 0, c.eq.s, 0xdeadbeef, 0xdeadbeef, 0x00000001 )

        TEST_PARC_END

