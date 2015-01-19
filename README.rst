========================================================================
README: Pydgin
========================================================================

Pydgin: a (Py)thon (D)SL for (G)enerating (In)struction set simulators.

------------------------------------------------------------------------
Introduction
------------------------------------------------------------------------

Pydgin provides a collection of classes and functions which act as an
embedded architectural description language (embedded-ADL) for concisely
describing the behavior of instruction set simulators (ISS). An ISS
described in Pydgin can be directly executed in a Python interpreter for
rapid prototyping and debugging, or alternatively can be used to
automatically generate a performant, JIT-optimizing C executable more
suitable for application development.

Automatic generation of JIT-enabled ISS from Pydgin is enabled by the
RPython Translation Toolchain, an open-source tool used by developers of
the PyPy JIT-optimizing Python interpreter. [1]

An ISS described in Pydgin implements an *interpretive* simulator which
can be directly executed in a Python interpreter for rapid prototyping
and debugging. However, Pydgin ISS can also be automatically translated
into a C executable implementing a *JIT-enabled interpretive* simulator,
providing a high-performance implementation suitable for application
development. Generated Pydgin executables provide significant
performance benefits in two ways. First, the compiled C implementation
enables much more efficient execution of instruction-by-instruction
interpretive simulation than the original Python implementation. Second,
the generated executable provides a just-in-time optimizer, which h

------------------------------------------------------------------------
Project Subdirectories
------------------------------------------------------------------------

The following directories Pydgin libraries and simulator implementations
for executing ELF binaries compiled with a cross-compiler.

- pydgin:  Library for describing instruction set simulators (ISS).
- arm:     Pydgin ISS for executing ARMv5 binaries.
- parc:    Pydgin ISS for executing PARC binaries.

The following directories contain experimental interpreters for
executing textual files. They serve no purpose other than to learn more
about the capabilities of the RPython translation toolchain.

- parc_interp: An interpreter for the complete PARC ISA.
- asm_toy_2:   A toy interpreter for (less) simple PARC assembly files.
- asm_toy_1:   A toy interpreter for (very) simple PARC assembly files.
- bf:          A simple interpreter for a toy language.


Please see the README files in each subdirectory for more information.

------------------------------------------------------------------------
Beginner RPython References
------------------------------------------------------------------------

- http://www.wilfred.me.uk/blog/2014/05/24/r-python-for-fun-and-profit/
- http://morepypy.blogspot.com/2011/04/tutorial-writing-interpreter-with-pypy.html
- http://morepypy.blogspot.co.uk/2011/04/tutorial-part-2-adding-jit.html
- https://bitbucket.org/brownan/pypy-tutorial/
- http://pie-interpreter.blogspot.com/2012/12/how-to-make-new-interpreter-with-pypy.html
- http://indefinitestudies.org/2010/02/08/creating-a-toy-virtual-machine-with-pypy

------------------------------------------------------------------------
Advanced RPython References
------------------------------------------------------------------------

- http://morepypy.blogspot.com/2011/03/controlling-tracing-of-interpreter-with.html
- http://morepypy.blogspot.com/2011/03/controlling-tracing-of-interpreter-with_15.html
- http://morepypy.blogspot.com/2011/03/controlling-tracing-of-interpreter-with_21.html
- http://morepypy.blogspot.com/2011/03/controlling-tracing-of-interpreter-with_26.html
- http://bitbucket.org/pypy/extradoc/raw/extradoc/talk/icooolps2011/bolz-hints.pdf
- http://pypy.readthedocs.org/en/latest/jit/pyjitpl5.html
- http://morepypy.blogspot.com/2010/06/jit-for-regular-expression-matching.html
- https://github.com/samgiles/naulang/blob/master/naulang/compiler/parser.py
- https://github.com/alex/rply

------------------------------------------------------------------------
Untranslatable Python Code and RPython Alternatives
------------------------------------------------------------------------

Fails::
  int( some_str, base=16 )
Translates, but fails during execution::
  int( some_str, 16 )
Works::
  rpython.rlib.rarithmetic.string_to_int( some_str, base=16 )

Fails::
  line.split()
Works::
  line.split(' ', 3)

Fails::
  with open( filename, 'rb' ) as file_obj: ...
Works::
  file_obj = open( filename, 'rb )
  file_obj.close()

Fails::
  string = string.ljust( nchars, '0' )
Works::
  string = '0'*( nchars - len(string) ) + string

Fails::
  my_array[start_idx:]
Works::
  assert start_idx >= 0
  my_array[start_idx:]

Fails::
  assert obj.attr >= 0
  my_array[obj.attr:]
Works::
  start_idx = obj.attr
  assert start_idx >= 0
  my_array[start_idx:]

Fails::
  section_name = start.partition('\0')[0]
Works::
  section_name = start.split( '\0', 1 )[0]

Fails::
  if my_str != None: do_something()
Works::
  if my_str != '': do_something()

Fails::
  raise Exception( 'Error %08x!' % my_value )
Works::
  raise Exception( 'Error %x!' % my_value )

