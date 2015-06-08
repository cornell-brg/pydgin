//=========================================================================
// parcv3-div-s.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Arithmetic tests
        //-----------------------------------------------------------------

        TEST_RR_OP( div.s, 0x3f800000, 0x3f800000, 0x3f800000 )
        TEST_RR_OP( div.s, 0x43050800, 0x43030800, 0x3f81f428 )
        TEST_RR_OP( div.s, 0x40003450, 0x40002340, 0x3f80110b )
        TEST_RR_OP( div.s, 0x40003450, 0x40002340, 0x3f80110b )
        TEST_RR_OP( div.s, 0xdeadbeef, 0xcafebabe, 0x532e9cc9 )
        TEST_RR_OP( div.s, 0xdeadbeef, 0xdeadbeef, 0x3f800000 )
        TEST_RR_OP( div.s, 0xfafafafa, 0xfbfbfbfb, 0x3e7efae7 )

        //-----------------------------------------------------------------
        // Source/Destination tests
        //-----------------------------------------------------------------

        TEST_RR_SRC0_EQ_DEST( div.s, 0x40003450, 0x40002340, 0x3f80110b )
        TEST_RR_SRC1_EQ_DEST( div.s, 0xdeadbeef, 0xcafebabe, 0x532e9cc9 )
        TEST_RR_SRCS_EQ_DEST( div.s, 0xdeadbeef, 0x3f800000 )

        //-----------------------------------------------------------------
        // Bypassing tests
        //-----------------------------------------------------------------

        TEST_RR_DEST_BYP( 0, div.s, 0x43050800, 0x43030800, 0x3f81f428 )
        TEST_RR_DEST_BYP( 1, div.s, 0x40003450, 0x40002340, 0x3f80110b )
        TEST_RR_DEST_BYP( 2, div.s, 0x40003450, 0x40002340, 0x3f80110b )

        TEST_RR_SRC01_BYP( 0, 0, div.s, 0x43050800, 0x43030800, 0x3f81f428 )
        TEST_RR_SRC01_BYP( 0, 1, div.s, 0x40003450, 0x40002340, 0x3f80110b )
        TEST_RR_SRC01_BYP( 0, 2, div.s, 0x40003450, 0x40002340, 0x3f80110b )
        TEST_RR_SRC01_BYP( 1, 0, div.s, 0xdeadbeef, 0xcafebabe, 0x532e9cc9 )
        TEST_RR_SRC01_BYP( 1, 1, div.s, 0xdeadbeef, 0xdeadbeef, 0x3f800000 )
        TEST_RR_SRC01_BYP( 2, 0, div.s, 0xfafafafa, 0xfbfbfbfb, 0x3e7efae7 )

        TEST_RR_SRC10_BYP( 0, 0, div.s, 0x43050800, 0x43030800, 0x3f81f428 )
        TEST_RR_SRC10_BYP( 0, 1, div.s, 0x40003450, 0x40002340, 0x3f80110b )
        TEST_RR_SRC10_BYP( 0, 2, div.s, 0x40003450, 0x40002340, 0x3f80110b )
        TEST_RR_SRC10_BYP( 1, 0, div.s, 0xdeadbeef, 0xcafebabe, 0x532e9cc9 )
        TEST_RR_SRC10_BYP( 1, 1, div.s, 0xdeadbeef, 0xdeadbeef, 0x3f800000 )
        TEST_RR_SRC10_BYP( 2, 0, div.s, 0xfafafafa, 0xfbfbfbfb, 0x3e7efae7 )

        //--------------------------------------------------------------------
        // Arithmetic tests
        //--------------------------------------------------------------------
        // randomly generated set of test vectors
        
        TEST_RR_OP( div.s, 0xc8cabbe2, 0xc79c698f, 0x40a5e842 )
        TEST_RR_OP( div.s, 0xc89df3fc, 0x4907e768, 0xbf14c44d )
        TEST_RR_OP( div.s, 0x49378abd, 0x49210937, 0x3f91e391 )
        TEST_RR_OP( div.s, 0x49015169, 0x492b54bb, 0x3f413993 )
        TEST_RR_OP( div.s, 0xc888237f, 0xc844e803, 0x3fb0fece )
        TEST_RR_OP( div.s, 0x47b64755, 0x48d38d0b, 0x3e5c93c8 )
        TEST_RR_OP( div.s, 0x48bb005b, 0x48e31ea2, 0x3f52c7c3 )
        TEST_RR_OP( div.s, 0x495594bd, 0x490c031a, 0x3fc341d6 )
        TEST_RR_OP( div.s, 0xc883c86e, 0xc870736b, 0x3f8c4e0d )
        TEST_RR_OP( div.s, 0xc8f2a35b, 0x49702af5, 0xbf01510b )
        TEST_RR_OP( div.s, 0xc872b81a, 0xc91516d4, 0x3ed062bd )
        TEST_RR_OP( div.s, 0x496e8dad, 0x495b99a8, 0x3f8b0c22 )
        TEST_RR_OP( div.s, 0x49689bb0, 0x493f2619, 0x3f9bc33c )
        TEST_RR_OP( div.s, 0x4863a22c, 0xc9029fbf, 0xbedf0f8c )
        TEST_RR_OP( div.s, 0x488b7463, 0x49719546, 0x3e93c6df )
        TEST_RR_OP( div.s, 0xc8c502c2, 0xc8dbf33a, 0x3f654d08 )

        TEST_PARC_END

