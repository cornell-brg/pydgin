#=======================================================================
# misc.py
#=======================================================================

import re
import elf
import py
import rpython

#-----------------------------------------------------------------------
# load_program
#-----------------------------------------------------------------------
def load_program( fp, mem, alignment=0 ):

  mem_image  = elf.elf_reader( fp )
  sections   = mem_image.get_sections()
  entrypoint = -1

  for section in sections:
    start_addr = section.addr
    for i, data in enumerate( section.data ):
      mem[start_addr+i] = data

    # TODO: HACK should really have elf_reader return the entry point
    #       address in the elf header!
    if section.name == '.text':
      entrypoint = section.addr

  assert entrypoint >= 0
  assert sections[-1].name == '.bss'

  bss        = sections[-1]
  breakpoint = bss.addr + len( bss.data )

  if alignment > 0:
    def round_up( val, alignment ):
      return (val + alignment - 1) & ~(alignment - 1)
    breakpoint = round_up( breakpoint, alignment )

  return mem, entrypoint, breakpoint

#-----------------------------------------------------------------------
# create_risc_decoder
#-----------------------------------------------------------------------
def create_risc_decoder( encodings, isa_globals ):

  inst_nbits = len( encodings[0][1] )

  def split_encodings( enc ):
    return [x for x in re.split( '(x*)', enc ) if x]

  bit_fields = [ split_encodings( x[1] ) for x in encodings ]

  decoder = ''
  for i, inst in enumerate( bit_fields ):
    #print i, encodings[i][0], inst
    bit = 0
    conditions = []
    for field in reversed( inst ):
      nbits = len( field )
      if field[0] != 'x':
        mask = (1 << nbits) - 1
        cond = '(inst >> {}) & 0x{:X} == 0b{}'.format( bit, mask, field )
        conditions.append( cond )
      bit += nbits
    decoder += 'if   ' if i == 0 else '  elif '
    decoder += ' and '.join( reversed(conditions) ) + ':\n'
    decoder += '    return execute_{}\n'.format( encodings[i][0] )

  source = py.code.Source('''
@rpython.rlib.jit.elidable
def decode( inst ):
  {decoder_tree}
  else:
    raise Exception('Invalid instruction 0x%x!' % inst )
  '''.format( decoder_tree = decoder ))
  #print source
  environment = dict(globals().items() + isa_globals.items())
  exec source.compile() in environment

  return environment['decode']
