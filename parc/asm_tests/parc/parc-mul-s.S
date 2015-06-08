//=========================================================================
// parcv3-mul-s.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Arithmetic tests
        //-----------------------------------------------------------------

        TEST_RR_OP( mul.s, 0x3f800000, 0x3f800000, 0x3f800000 )
        TEST_RR_OP( mul.s, 0x40000000, 0x40000000, 0x40800000 )
        TEST_RR_OP( mul.s, 0x43050800, 0x43030800, 0x46882e80 )
        TEST_RR_OP( mul.s, 0x40003450, 0x40002340, 0x4080579e )
        TEST_RR_OP( mul.s, 0xdeadbeef, 0xcafebabe, 0x6a2ce22f )
        TEST_RR_OP( mul.s, 0xdeadbeef, 0xdeadbeef, 0x7debd73b )
        TEST_RR_OP( mul.s, 0xfafafafa, 0xfbfbfbfb, 0x7f800000 )

        //-----------------------------------------------------------------
        // Source/Destination tests
        //-----------------------------------------------------------------

        TEST_RR_SRC0_EQ_DEST( mul.s, 0x40003450, 0x40002340, 0x4080579e )
        TEST_RR_SRC1_EQ_DEST( mul.s, 0xdeadbeef, 0xcafebabe, 0x6a2ce22f )
        TEST_RR_SRCS_EQ_DEST( mul.s, 0xdeadbeef, 0x7debd73b )

        //-----------------------------------------------------------------
        // Bypassing tests
        //-----------------------------------------------------------------

        TEST_RR_DEST_BYP( 0, mul.s, 0x40000000, 0x40000000, 0x40800000 )
        TEST_RR_DEST_BYP( 1, mul.s, 0x43050800, 0x43030800, 0x46882e80 )
        TEST_RR_DEST_BYP( 2, mul.s, 0x40003450, 0x40002340, 0x4080579e )

        TEST_RR_SRC01_BYP( 0, 0, mul.s, 0x43050800, 0x43030800, 0x46882e80 )
        TEST_RR_SRC01_BYP( 0, 1, mul.s, 0x40003450, 0x40002340, 0x4080579e )
        TEST_RR_SRC01_BYP( 0, 2, mul.s, 0xdeadbeef, 0xcafebabe, 0x6a2ce22f )
        TEST_RR_SRC01_BYP( 1, 0, mul.s, 0xdeadbeef, 0xdeadbeef, 0x7debd73b )
        TEST_RR_SRC01_BYP( 1, 1, mul.s, 0xfafafafa, 0xfbfbfbfb, 0x7f800000 )
        TEST_RR_SRC01_BYP( 2, 0, mul.s, 0xfafafafa, 0xfbfbfbfb, 0x7f800000 )

        TEST_RR_SRC10_BYP( 0, 0, mul.s, 0x43050800, 0x43030800, 0x46882e80 )
        TEST_RR_SRC10_BYP( 0, 1, mul.s, 0x40003450, 0x40002340, 0x4080579e )
        TEST_RR_SRC10_BYP( 0, 2, mul.s, 0xdeadbeef, 0xcafebabe, 0x6a2ce22f )
        TEST_RR_SRC10_BYP( 1, 0, mul.s, 0xdeadbeef, 0xdeadbeef, 0x7debd73b )
        TEST_RR_SRC10_BYP( 1, 1, mul.s, 0xfafafafa, 0xfbfbfbfb, 0x7f800000 )
        TEST_RR_SRC10_BYP( 2, 0, mul.s, 0xfafafafa, 0xfbfbfbfb, 0x7f800000 )

        //--------------------------------------------------------------------
        // Arithmetic tests
        //--------------------------------------------------------------------
        // randomly generated set of test vectors
        
        TEST_RR_OP( mul.s, 0x48ba39c0, 0xc8d7154f, 0xd21c7600 )
        TEST_RR_OP( mul.s, 0xc923b079, 0xc901052f, 0x52a4fe7b )
        TEST_RR_OP( mul.s, 0xc7684fff, 0x480dc4aa, 0xd000a687 )
        TEST_RR_OP( mul.s, 0xc845a6d3, 0x483e7522, 0xd1130c40 )
        TEST_RR_OP( mul.s, 0xc93222a3, 0xc8843fe9, 0x52380ca9 )
        TEST_RR_OP( mul.s, 0x48eeadf3, 0xc8fb32c6, 0xd26a33e4 )
        TEST_RR_OP( mul.s, 0xc920a6ea, 0xc89c90d4, 0x52448133 )
        TEST_RR_OP( mul.s, 0xc90dbdf3, 0xc825507b, 0x51b70ffa )
        TEST_RR_OP( mul.s, 0xc84ca8b2, 0xc962aae8, 0x5235358f )
        TEST_RR_OP( mul.s, 0x4904143b, 0xc93a5830, 0xd2c04865 )
        TEST_RR_OP( mul.s, 0xc782960f, 0x49590a5d, 0xd15d6cf8 )
        TEST_RR_OP( mul.s, 0x4914f7ad, 0x4924984a, 0x52bf8e92 )
        TEST_RR_OP( mul.s, 0xc9106ccf, 0x49652367, 0xd301454e )
        TEST_RR_OP( mul.s, 0x487263ba, 0xc96322e1, 0xd2570f74 )
        TEST_RR_OP( mul.s, 0x48c12c74, 0xc91b4f0c, 0xd26a6320 )
        TEST_RR_OP( mul.s, 0xc971d060, 0x49650aff, 0xd35859c9 )

        TEST_PARC_END

