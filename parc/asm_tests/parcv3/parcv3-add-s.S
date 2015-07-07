//=========================================================================
// parcv3-add-s.S
//=========================================================================

#include "parc-macros.h"

        TEST_PARC_BEGIN

        //-----------------------------------------------------------------
        // Arithmetic tests
        //-----------------------------------------------------------------

        TEST_RR_OP( add.s, 0x3f800000, 0x3f800000, 0x40000000 )
        TEST_RR_OP( add.s, 0x40000000, 0x40000000, 0x40800000 )
        TEST_RR_OP( add.s, 0x40003450, 0x40002340, 0x40802bc8 )
        TEST_RR_OP( add.s, 0xdeadbeef, 0xcafebabe, 0xdeadbeef )
        TEST_RR_OP( add.s, 0xdeadbeef, 0xdeadbeef, 0xdf2dbeef )

        //-----------------------------------------------------------------
        // Source/Destination tests
        //-----------------------------------------------------------------

        TEST_RR_SRC0_EQ_DEST( add.s, 0x40003450, 0x40002340, 0x40802bc8 )
        TEST_RR_SRC1_EQ_DEST( add.s, 0xdeadbeef, 0xcafebabe, 0xdeadbeef )
        TEST_RR_SRCS_EQ_DEST( add.s, 0x3f800000, 0x40000000 )

        //-----------------------------------------------------------------
        // Bypassing tests
        //-----------------------------------------------------------------

        TEST_RR_DEST_BYP( 0, add.s, 0x3f800000, 0x3f800000, 0x40000000 )
        TEST_RR_DEST_BYP( 1, add.s, 0x40000000, 0x40000000, 0x40800000 )
        TEST_RR_DEST_BYP( 2, add.s, 0x40003450, 0x40002340, 0x40802bc8 )

        TEST_RR_SRC01_BYP( 0, 0, add.s, 0x3f800000, 0x3f800000, 0x40000000 )
        TEST_RR_SRC01_BYP( 0, 1, add.s, 0x40000000, 0x40000000, 0x40800000 )
        TEST_RR_SRC01_BYP( 0, 2, add.s, 0x40003450, 0x40002340, 0x40802bc8 )
        TEST_RR_SRC01_BYP( 1, 0, add.s, 0xdeadbeef, 0xcafebabe, 0xdeadbeef )
        TEST_RR_SRC01_BYP( 1, 1, add.s, 0xdeadbeef, 0xdeadbeef, 0xdf2dbeef )
        TEST_RR_SRC01_BYP( 2, 0, add.s, 0xdeadbeef, 0xcafebabe, 0xdeadbeef )

        TEST_RR_SRC10_BYP( 0, 0, add.s, 0x3f800000, 0x3f800000, 0x40000000 )
        TEST_RR_SRC10_BYP( 0, 1, add.s, 0x40000000, 0x40000000, 0x40800000 )
        TEST_RR_SRC10_BYP( 0, 2, add.s, 0x40003450, 0x40002340, 0x40802bc8 )
        TEST_RR_SRC10_BYP( 1, 0, add.s, 0xdeadbeef, 0xcafebabe, 0xdeadbeef )
        TEST_RR_SRC10_BYP( 1, 1, add.s, 0xdeadbeef, 0xdeadbeef, 0xdf2dbeef )
        TEST_RR_SRC10_BYP( 2, 0, add.s, 0xdeadbeef, 0xcafebabe, 0xdeadbeef )

        //--------------------------------------------------------------------
        // Arithmetic tests
        //--------------------------------------------------------------------
        // randomly generated set of test vectors
        
        TEST_RR_OP( add.s, 0xc90ee55e, 0x47b0a615, 0xc8f1a137 )
        TEST_RR_OP( add.s, 0x4913a464, 0x49318890, 0x49a2967a )
        TEST_RR_OP( add.s, 0xc93ecaf8, 0xc949f822, 0xc9c4618d )
        TEST_RR_OP( add.s, 0x488e8770, 0x48297887, 0x48e343b4 )
        TEST_RR_OP( add.s, 0x48db2d66, 0x47dd5ca9, 0x49094248 )
        TEST_RR_OP( add.s, 0x49635ea3, 0x4968f169, 0x49e62806 )
        TEST_RR_OP( add.s, 0x49026a7e, 0x494c00be, 0x49a7359e )
        TEST_RR_OP( add.s, 0x491f724f, 0x4690d03e, 0x4923f8d1 )
        TEST_RR_OP( add.s, 0x48621b44, 0xc879f7f5, 0xc6bee588 )
        TEST_RR_OP( add.s, 0xc88125d5, 0x489665db, 0x472a0030 )
        TEST_RR_OP( add.s, 0x4950fbf4, 0x4952c2bb, 0x49d1df58 )
        TEST_RR_OP( add.s, 0x4904767c, 0xc8e237b4, 0x479ad510 )
        TEST_RR_OP( add.s, 0xc86fabed, 0x47c1ac2c, 0xc80ed5d7 )
        TEST_RR_OP( add.s, 0x4931dfb5, 0x48b495f7, 0x49861558 )
        TEST_RR_OP( add.s, 0x48f59d2e, 0x492d9c61, 0x4994357c )

        TEST_PARC_END


