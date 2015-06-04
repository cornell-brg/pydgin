//=========================================================================
// parcv3-sub-s.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Arithmetic tests
        //-----------------------------------------------------------------

        TEST_RR_OP( sub.s, 0x43050800, 0x43030800, 0x40000000 )
        TEST_RR_OP( sub.s, 0x40003450, 0x40002340, 0x3a888000 )
        TEST_RR_OP( sub.s, 0xdeadbeef, 0xdeadbeef, 0x00000000 )
        TEST_RR_OP( sub.s, 0xfafafafa, 0xfbfbfbfb, 0x7bbd3d3c )

        //-----------------------------------------------------------------
        // Source/Destination tests
        //-----------------------------------------------------------------

        TEST_RR_SRC0_EQ_DEST( sub.s, 0x40003450, 0x40002340, 0x3a888000 )
        TEST_RR_SRC1_EQ_DEST( sub.s, 0x43050800, 0x43030800, 0x40000000 )
        TEST_RR_SRCS_EQ_DEST( sub.s, 0xdeadbeef, 0x00000000 )

        //-----------------------------------------------------------------
        // Bypassing tests
        //-----------------------------------------------------------------

        TEST_RR_DEST_BYP( 0, sub.s, 0x40003450, 0x40002340, 0x3a888000 )
        TEST_RR_DEST_BYP( 1, sub.s, 0xdeadbeef, 0xdeadbeef, 0x00000000 )
        TEST_RR_DEST_BYP( 2, sub.s, 0xfafafafa, 0xfbfbfbfb, 0x7bbd3d3c )

        TEST_RR_SRC01_BYP( 0, 0, sub.s, 0x43050800, 0x43030800, 0x40000000 )
        TEST_RR_SRC01_BYP( 0, 1, sub.s, 0x40003450, 0x40002340, 0x3a888000 )
        TEST_RR_SRC01_BYP( 0, 2, sub.s, 0xdeadbeef, 0xdeadbeef, 0x00000000 )
        TEST_RR_SRC01_BYP( 1, 0, sub.s, 0xfafafafa, 0xfbfbfbfb, 0x7bbd3d3c )
        TEST_RR_SRC01_BYP( 1, 1, sub.s, 0x43050800, 0x43030800, 0x40000000 )
        TEST_RR_SRC01_BYP( 2, 0, sub.s, 0x40003450, 0x40002340, 0x3a888000 )

        TEST_RR_SRC10_BYP( 0, 0, sub.s, 0x43050800, 0x43030800, 0x40000000 )
        TEST_RR_SRC10_BYP( 0, 1, sub.s, 0x40003450, 0x40002340, 0x3a888000 )
        TEST_RR_SRC10_BYP( 0, 2, sub.s, 0xdeadbeef, 0xdeadbeef, 0x00000000 )
        TEST_RR_SRC10_BYP( 1, 0, sub.s, 0xfafafafa, 0xfbfbfbfb, 0x7bbd3d3c )
        TEST_RR_SRC10_BYP( 1, 1, sub.s, 0x43050800, 0x43030800, 0x40000000 )
        TEST_RR_SRC10_BYP( 2, 0, sub.s, 0x40003450, 0x40002340, 0x3a888000 )

        //--------------------------------------------------------------------
        // Arithmetic tests
        //--------------------------------------------------------------------
        // randomly generated set of test vectors

        TEST_RR_OP( sub.s, 0xc94cbe28, 0x490247ea, 0xc9a78309 )
        TEST_RR_OP( sub.s, 0xc91ab11d, 0x48119bd4, 0xc93f1812 )
        TEST_RR_OP( sub.s, 0x496e81e5, 0xc91ba4bd, 0x49c51351 )
        TEST_RR_OP( sub.s, 0x474028dd, 0x48f97b1d, 0xc8e17601 )
        TEST_RR_OP( sub.s, 0xc9256406, 0x48e6264e, 0xc98c3b96 )
        TEST_RR_OP( sub.s, 0xc921f603, 0x492345ee, 0xc9a29df8 )
        TEST_RR_OP( sub.s, 0x47361db7, 0xc89d7afe, 0x48b43eb5 )
        TEST_RR_OP( sub.s, 0xc7d5e993, 0xc84ce1d3, 0x47c3da13 )
        TEST_RR_OP( sub.s, 0xc8b37140, 0x474846c5, 0xc8cc7a19 )
        TEST_RR_OP( sub.s, 0x490ed735, 0xc8ef9d9b, 0x49835301 )
        TEST_RR_OP( sub.s, 0x484fc447, 0x479f2bd9, 0x48002e5a )
        TEST_RR_OP( sub.s, 0xc85fb086, 0xc907e129, 0x489fea0f )
        TEST_RR_OP( sub.s, 0x4845c87a, 0xc89897c3, 0x48fb7c00 )
        TEST_RR_OP( sub.s, 0xc9542e72, 0xc6fc9761, 0xc94c49b7 )
        TEST_RR_OP( sub.s, 0x48b0583e, 0x48d1101b, 0xc782df74 )
        TEST_RR_OP( sub.s, 0xc78c6254, 0x48cc8156, 0xc8ef99eb )

        TEST_PARC_END


