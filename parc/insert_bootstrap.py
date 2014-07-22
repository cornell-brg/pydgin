#=======================================================================
# insert_bootstrap.py
#=======================================================================
# Script to take a pisa ELF binary and insert bootstrap code needed by
# our research processor.
#
# Usage:
#
#   python insert_bootstrap <elf_file>
#

import sys
import os
sys.path.append('/Users/dmlockhart/vc/git-brg/parc/pymtl')
import pisa.elf           as elf
import pisa.pisa_encoding as pisa_encoding

# Load the elf file

source_elf  = sys.argv[1]
path, file_ = os.path.split( source_elf )
dest_elf    = file_+'-new'
mem_image   = None

with open(source_elf,'rb') as file_obj:
  mem_image = elf.elf_reader( file_obj )

# Add a bootstrap section at address 0x400

bootstrap_asm = """
  lui r29, 0x0007
  ori r29, r0, 0xfffc
  j   0x1000
"""

bootstrap_mem_image = pisa_encoding.assemble( bootstrap_asm )
bootstrap_bytes = bootstrap_mem_image.get_section(".text").data
mem_image.add_section( ".bootstrap", 0x400, bootstrap_bytes )

import struct
print len( bootstrap_bytes  )
for i in [0, 4, 8]:
  print '{:08x}'.format( struct.unpack('<I', bootstrap_bytes[i:i+4])[0] )

# Apparently we also need to binary rewrite the jump at 0x1008. This is
# super hacky for now -- this relies on the fact that the binrewrite
# section will be loaded _after_ the primary .text section so that we
# can essentially use the loader to do the binary rewrite.

binrewrite_asm = """
  j   0x1020
"""

binrewrite_mem_image = pisa_encoding.assemble( binrewrite_asm )
binrewrite_bytes = binrewrite_mem_image.get_section(".text").data
mem_image.add_section( ".binrewrite", 0x1008, binrewrite_bytes )

print '... {:08x}'.format( struct.unpack('<I', binrewrite_bytes[0:4])[0] )
raise Exception()

# Write the elf file back

with open(dest_elf,'wb') as file_obj:
  elf.elf_writer( mem_image, file_obj )
