#=======================================================================
# misc.py
#=======================================================================

import re
import elf
from jit import elidable

try:
  import py
  Source = py.code.Source
except ImportError:
  class Source:
    def __init__( self, src ):
      self.src = src
    def compile( self ):
      return self.src

#-----------------------------------------------------------------------
# FatalError
#-----------------------------------------------------------------------
# We use our own exception class to terminate execution on a fatal error.

class FatalError( Exception ):

  def __init__( self, msg ):
    self.msg = msg

#-----------------------------------------------------------------------
# load_program
#-----------------------------------------------------------------------
# hacky: do_no_load flag supresses loading the program (useful for
# physical memory provided by gem5)
def load_program( fp, mem, alignment=0, do_not_load=False ):

  mem_image  = elf.elf_reader( fp )
  sections   = mem_image.get_sections()
  entrypoint = -1

  for section in sections:
    start_addr = section.addr
    for i, data in enumerate( section.data ):
      if not do_not_load:
        mem.write( start_addr+i, 1, ord( data ) )

    # TODO: HACK should really have elf_reader return the entry point
    #       address in the elf header!
    if section.name == '.text':
      entrypoint = section.addr
    if section.name == '.data':
      mem.data_section = section.addr

  assert entrypoint >= 0

  last_sec   = sections[-1]
  breakpoint = last_sec.addr + len( last_sec.data )

  if alignment > 0:
    def round_up( val, alignment ):
      return (val + alignment - 1) & ~(alignment - 1)
    breakpoint = round_up( breakpoint, alignment )

  return entrypoint, breakpoint

#-----------------------------------------------------------------------
# create_risc_decoder
#-----------------------------------------------------------------------
def create_risc_decoder( encodings, isa_globals, debug=False ):

  # removes all characters other than '0', '1', and 'x'
  def remove_ignored_chars( enc ):
    return [ enc[0], re.sub( '[^01x]', '', enc[1] ) ]

  encodings = map( remove_ignored_chars, encodings )

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
    if debug:
      decoder += '    return "{0}", execute_{0}\n'.format( encodings[i][0] )
    else:
      decoder += '    return execute_{}\n'.format( encodings[i][0] )

  source = Source('''
@elidable
def decode( inst ):
  {decoder_tree}
  else:
    raise FatalError('Invalid instruction 0x%x!' % inst )
  '''.format( decoder_tree = decoder ))

  #print source
  environment = dict(globals().items() + isa_globals.items())
  exec source.compile() in environment

  return environment['decode']
