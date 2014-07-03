"""
PyPy tutorial by Andrew Brown
example1.py - Python BF interpreter

"""

import sys
import os

#-----------------------------------------------------------------------
# mainloop
#-----------------------------------------------------------------------
def mainloop(program, bracket_map):
  pc = 0
  tape = Tape()

  while pc < len(program):

    code = program[pc]

    if code == ">":
      tape.advance()

    elif code == "<":
      tape.devance()

    elif code == "+":
      tape.inc()

    elif code == "-":
      tape.dec()

    elif code == ".":
      # print
      #sys.stdout.write(chr(tape.get())) # EXAMPLE 1
      os.write(1, chr(tape.get()))

    elif code == ",":
      # read from stdin
      #tape.set(ord(sys.stdin.read(1)))  # EXAMPLE 1
      tape.set(ord(os.read(0, 1)[0]))

    elif code == "[" and tape.get() == 0:
      # Skip forward to the matching ]
      pc = bracket_map[pc]

    elif code == "]" and tape.get() != 0:
      # Skip back to the matching [
      pc = bracket_map[pc]

    pc += 1

#-----------------------------------------------------------------------
# Tape
#-----------------------------------------------------------------------
class Tape(object):
  def __init__(self):
    self.thetape = [0]
    self.position = 0

  def get(self):
    return self.thetape[self.position]
  def set(self, val):
    self.thetape[self.position] = val
  def inc(self):
    self.thetape[self.position] += 1
  def dec(self):
    self.thetape[self.position] -= 1
  def advance(self):
    self.position += 1
    if len(self.thetape) <= self.position:
      self.thetape.append(0)
  def devance(self):
    self.position -= 1

#-----------------------------------------------------------------------
# parse
#-----------------------------------------------------------------------
def parse(program):
  parsed = []
  bracket_map = {}
  leftstack = []

  pc = 0
  for char in program:
    if char in ('[', ']', '<', '>', '+', '-', ',', '.'):
      parsed.append(char)

      if char == '[':
        leftstack.append(pc)
      elif char == ']':
        left = leftstack.pop()
        right = pc
        bracket_map[left] = right
        bracket_map[right] = left
      pc += 1

  return "".join(parsed), bracket_map

#=======================================================================
# EXAMPLE 1
#=======================================================================
#
#def run(input):
#  program, map = parse(input.read())
#  mainloop(program, map)
#
#if __name__ == "__main__":
#  run(open(sys.argv[1], 'r'))

#=======================================================================
# EXAMPLE 2
#=======================================================================

#-----------------------------------------------------------------------
# run
#-----------------------------------------------------------------------
def run(fp):
  program, bm = parse(fp.read())
  mainloop(program, bm)

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
def target(*args):
  return entry_point, None

#-----------------------------------------------------------------------
# main
#-----------------------------------------------------------------------
if __name__ == "__main__":
  entry_point(sys.argv)

