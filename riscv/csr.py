#=========================================================================
# csr.py
#=========================================================================
# Models CSRs

from utils        import trim
from pydgin.utils import r_uint
from pydgin.misc  import FatalError

PRV_U = 0
PRV_S = 1
PRV_H = 2
PRV_M = 3

csr_map = {
            "fcsr"      :  0x003,

            "mcpuid"    :  0xf00,
            "mimpid"    :  0xf01,
            "mhartid"   :  0xf10,

            "mstatus"   :  0x300,

            "mepc"      :  0x341,

            "mtohost"   :  0x780,
            "mfromhost" :  0x781,

          }

class Csr( object ):


  def __init__( self, state ):
    self.state = state

  def get_csr( self, csr_id ):
    if   csr_id == csr_map[ "fcsr" ]:
      return self.state.fcsr
    elif csr_id == csr_map[ "mcpuid" ]:
      return self.get_mcpuid()
    elif csr_id == csr_map[ "mstatus" ]:
      return self.get_mstatus()
    elif csr_id == csr_map[ "mhartid" ]:
      return self.get_mhartid()
    elif csr_id == csr_map[ "mepc" ]:
      return self.state.mepc

    else:
      print "WARNING: can't get csr %x" % csr_id
      return 0

  def set_csr( self, csr_id, val ):
    # TODO: permission check
    if   csr_id == csr_map[ "fcsr" ]:
      # only the low 8 bits of fcsr should be non-zero
      self.state.fcsr = trim( val, 8 )
    elif csr_id == csr_map[ "mepc" ]:
      self.state.mepc = val
    elif csr_id == csr_map[ "mtohost" ]:
      if val & 0x1 and self.state.testbin:
        status = val >> 1
        if status:
          print "  [ FAILED ] %s (test #%s)" % (self.state.exe_name, status )
        else:
          print "  [ passed ] %s" % self.state.exe_name
        self.state.running = False

    else:
      print "WARNING: can't set csr %x" % csr_id

  #---------------------------------------------------------------------
  # get_mcpuid
  #---------------------------------------------------------------------
  #
  #  xlen-1  xlen-2 xlen-3  26 25         0
  # +--------------+----------+------------+
  # | Base         |    0     | Extensions |
  # +--------------+----------+------------+
  #
  # Base:
  #  0b00 : RV32I
  #  0b01 : RV32E
  #  0b10 : RV64I
  #  0b11 : RV128I
  #
  # Extensions: alphabetical bitmask (bit 0 == "a", bit 25 == "z")

  def get_mcpuid( self ):
    if self.state.xlen == 32:
      base = 0b00
      # TODO: not currently representing RV32E
    elif self.state.xlen == 64:
      base = 0b10
    elif self.state.xlen == 128:
      base = 0b11
    else:
      raise FatalError( "XLEN=%d not supported" % self.state.xlen )

    extensions = 0
    for e in self.state.extensions:
      extensions |= 1 << ( ord(e) - ord("a") )

    return r_uint( ( base << (self.state.xlen - 2) ) | extensions )

  #-----------------------------------------------------------------------
  # get_mhartid
  #-----------------------------------------------------------------------
  #
  #  xlen-1             0
  # +--------------------+
  # | Hart ID            |
  # +--------------------+
  #
  # Hart ID: Integer ID of the hardware thread running the code.

  def get_mhartid( self ):
    return r_uint( 0 )

  #-----------------------------------------------------------------------
  # get_mstatus
  #-----------------------------------------------------------------------
  #
  #  xlen-1 xlen-2  22 21     17   16   15     14 13     12 11       10
  # +------+----------+---------+------+---------+---------+-----------+-
  # |  SD  |     0    | VM[4:0] | MPRV | XS[1:0] | FS[1:0] | PRV3[1:0] |
  # +------+----------+---------+------+---------+---------+-----------+-
  #
  #     9   8         7   6   5         4   3   2        1  0
  # -+-----+-----------+-----+-----------+-----+----------+----+
  #  | IE3 | PRV2[1:0] | IE2 | PRV1[1:0] | IE1 | PRV[1:0] | IE |
  # -+-----+-----------+-----+-----------+-----+----------+----+
  #
  # PRV: current privilege mode
  #  0b00  : User/Application
  #  0b01  : Supervisor
  #  0b10  : Hypervisor
  #  0b11  : Machine
  #
  # IE: whether interrupts are enabled
  #  1 : enabled
  #  0 : disabled
  #
  # IE{1,2,3}, PRV{1,2,3}: IE and PRV stack for traps
  #
  # VM: virtualization management
  #  0b00000         : Mbare (no translation or protection)
  #  0b00001         : Mbb (single base-and-bound)
  #  0b00010         : Mbbid (separate instruction and data base-and-bound)
  #  0b00011-0b00111 : reserved
  #  0b01000         : Sv32 (page-based 32-bit virtual addressing)
  #  0b01001         : Sv39 (page-based 39-bit virtual addressing)
  #  0b01010         : Sv48 (page-based 48-bit virtual addressing)
  #  0b01011         : Sv57 (page-based 57-bit virtual addressing)
  #  0b01100         : Sv64 (page-based 64-bit virtual addressing)
  #  0b01101-0b11111 : reserved
  #
  # MPRV: modify the privelege level at which loads and stores execute
  #  0 : normal translation and protection
  #  1 : data memory addresses are translated and protected as though PRV
  #      were set to the current value of the PRV1 field
  #
  # FS/XS: current state of floating-point and add'l user-mode extensions
  #  0b00 : off
  #  0b01 : initial
  #  0b10 : clean
  #  0b11 : dirty
  #
  # SD: whether either FS or XS encodes dirty state

  def get_mstatus( self ):

    ie   = r_uint( 0 )
    prv  = r_uint( self.state.prv )
    ie1  = r_uint( 0 )
    prv1 = r_uint( 0 )
    ie2  = r_uint( 0 )
    prv2 = r_uint( 0 )
    ie3  = r_uint( 0 )
    prv3 = r_uint( 0 )
    fs   = r_uint( 0 )
    xs   = r_uint( 0 )
    mprv = r_uint( 0 )
    vm   = r_uint( 0 )
    sd   = r_uint( 0 )

    xlen = self.state.xlen

    return (     ie
             | ( prv  << 1        )
             | ( ie1  << 3        )
             | ( prv1 << 4        )
             | ( ie2  << 6        )
             | ( prv2 << 7        )
             | ( ie3  << 9        )
             | ( prv3 << 10       )
             | ( fs   << 12       )
             | ( xs   << 14       )
             | ( mprv << 16       )
             | ( vm   << 17       )
             | ( sd   << (xlen-1) ) )

