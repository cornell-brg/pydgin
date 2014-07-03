import sys
import os

from   rpython.rlib.rarithmetic import string_to_int as stoi

def mainloop( insts ):
  pc = 0
  rf = [0] * 32

  while pc < len( insts ):

    inst, f0, f1, f2 = insts[ pc ]

    if   inst == 'addiu':
      rd, rs, imm = int(f0[1:]), int(f1[1:]), stoi(f2,base=16)
      rf[ rd ] = rf[ rs ] + imm

    elif inst == 'addu':
      rd, rs, rt  = int(f0[1:]), int(f1[1:]), int(f2[1:])
      rf[ rd ] = rf[ rs ] + rf[ rt ]

    elif inst == 'print':
      _, _, rt = f0, f1, int(f2[1:])
      result = f2 + ' = ' + str( rf[rt] ) + '\n'
      os.write( 1, result )

    pc += 1

#-----------------------------------------------------------------------
# RegisterFile
#-----------------------------------------------------------------------
class RegisterFile( object ):
  def __init__( self ):
    self.regs = [0] * 32
  #def __getitem__( self, idx ):
  #  return self.regs[idx]
  #def __setitem__( self, idx, value ):
  #  self.regs[idx] = value
  def rd( self, idx ):
    return self.regs[idx]
  def wr( self, idx, value ):
    self.regs[idx] = value

#-----------------------------------------------------------------------
# parse
#-----------------------------------------------------------------------
def parse( fp ):
  insts = []
  line  = ''
  last  = None

  for char in fp.read():
    if char == '\n' and line:
      inst, f0, f1, f2 = line.split(' ',3 )
      insts.append([inst, f0, f1, f2])
      line = ''
      last = None
    elif char != ',' and not (last == char == ' '):
      line += char
      last  = char

  return insts

#-----------------------------------------------------------------------
# run
#-----------------------------------------------------------------------
def run(fp):
  program = parse( fp )
  mainloop(program)

#-----------------------------------------------------------------------
# entry_point
#-----------------------------------------------------------------------
def entry_point(argv):
  try:
    filename = argv[1]
  except IndexError:
    print "You must supply a filename"
    return 1

  run(open(filename, 'r'))
  return 0

#-----------------------------------------------------------------------
# target
#-----------------------------------------------------------------------
# Enables RPython translation of our interpreter.
def target( *args ):
  return entry_point, None

#-----------------------------------------------------------------------
# main
#-----------------------------------------------------------------------
# Enables CPython simulation of our interpreter.
if __name__ == "__main__":
  entry_point( sys.argv )
