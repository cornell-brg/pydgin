import os
import sys

from tutorial_bf_part1 import Tape, parse

#-----------------------------------------------------------------------
# jitdriver
#-----------------------------------------------------------------------
# So that you can still run this module under standard CPython, I add this
# import guard that creates a dummy class instead.
try:
  from rpython.rlib.jit import JitDriver
except ImportError:
  class JitDriver(object):
    def __init__       ( self, **kw ): pass
    def jit_merge_point( self, **kw ): pass
    def can_enter_jit  ( self, **kw ): pass

jitdriver = JitDriver(greens=['pc', 'program', 'bracket_map'], reds=['tape'])

#-----------------------------------------------------------------------
# mainloop
#-----------------------------------------------------------------------
def mainloop(program, bracket_map):
  pc = 0
  tape = Tape()

  while pc < len(program):

    # Annotation needed by jit

    jitdriver.jit_merge_point(
        pc=pc,
        tape=tape,
        program=program,
        bracket_map=bracket_map
    )

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
# jitpolicy
#-----------------------------------------------------------------------
def jitpolicy(driver):
  from rpython.jit.codewriter.policy import JitPolicy
  return JitPolicy()

#-----------------------------------------------------------------------
# run
#-----------------------------------------------------------------------
def run(fp):
  program_contents = ""
  while True:
    read = os.read(fp, 4096)
    if len(read) == 0:
      break
    program_contents += read
  os.close(fp)
  program, bm = parse(program_contents)
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

  run(os.open(filename, os.O_RDONLY, 0777))
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
