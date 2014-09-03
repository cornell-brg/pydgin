#=======================================================================
# misc.py
#=======================================================================

import elf

#-----------------------------------------------------------------------
# load_program
#-----------------------------------------------------------------------
def load_program( fp, mem ):

  mem_image = elf.elf_reader( fp )
  sections  = mem_image.get_sections()

  for section in sections:
    start_addr = section.addr
    for i, data in enumerate( section.data ):
      mem[start_addr+i] = data

  bss        = sections[-1]
  breakpoint = bss.addr + len( bss.data )

  return mem, breakpoint

