========================================================================
RPython Tutorial
========================================================================

------------------------------------------------------------------------
Beginner References
------------------------------------------------------------------------

- http://www.wilfred.me.uk/blog/2014/05/24/r-python-for-fun-and-profit/
- http://morepypy.blogspot.com/2011/04/tutorial-writing-interpreter-with-pypy.html
- http://morepypy.blogspot.co.uk/2011/04/tutorial-part-2-adding-jit.html
- https://bitbucket.org/brownan/pypy-tutorial/
- http://pie-interpreter.blogspot.com/2012/12/how-to-make-new-interpreter-with-pypy.html
- http://indefinitestudies.org/2010/02/08/creating-a-toy-virtual-machine-with-pypy

------------------------------------------------------------------------
Advanced References
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
Quick Start: A Very Basic Language Interpreter
------------------------------------------------------------------------

Running a brainf*ck interpreter in CPython::

  $ cd bf
  $ python tutorial_bf.py tutorial_99.b

Creating a C interpreter for brainf*ck using RPython
(requires that pypy source is installed):: 

  $ PYTHONPATH='/Users/dmlockhart/vc/hg-opensource/pypy' python \
    ~/vc/hg-opensource/pypy/rpython/translator/goal/translate.py \
    tutorial_bf.py

Running a brainf*ck interpreter translated to C via RPython::

  $ ./tutorial_bf-c tutorial_99.b

Creating a C interpreter for brainf*ck with tracing-JIT compiler using
RPython (requires that pypy source is installed):: 

  $ PYTHONPATH='/Users/dmlockhart/vc/hg-opensource/pypy' python \
    ~/vc/hg-opensource/pypy/rpython/translator/goal/translate.py \
    --opt=jit tutorial_bf_jit.py

Running::

  $ ./tutorial_bf_jit-c tutorial_99.b

A more optimized version::

  $ PYTHONPATH='/Users/dmlockhart/vc/hg-opensource/pypy' python \
    ~/vc/hg-opensource/pypy/rpython/translator/goal/translate.py \
    --opt=jit tutorial_bf_jit_opt.py
  $ ./tutorial_bf_jit-c tutorial_99.b

------------------------------------------------------------------------
Toy ISA Interpreter 1
------------------------------------------------------------------------

This interpreter is a very basic foundation for an ISA interpreter, it
only includes addiu, addu, and print instructions.  It is useful seeing
the minimal code needed to make a simple ISA interpreting simulator::

  $ cd asm_toy_1

CPython::

  $ PYTHONPATH='/Users/dmlockhart/vc/hg-opensource/pypy' \
    python simple_asm.py asm_00.s

RPython with no JIT::

  $ PYTHONPATH='/Users/dmlockhart/vc/hg-opensource/pypy' python \
    ~/vc/hg-opensource/pypy/rpython/translator/goal/translate.py \
    simple_asm.py
  $ ./simple_asm-c asm_00.s

------------------------------------------------------------------------
Toy ISA Interpreter 2
------------------------------------------------------------------------

This interpreter is a similar to the asm_toy_1, but includes mtc0 and
mfc0 instructions for testing, as well as demonstrates how a register
map can be used to simplify the interpreter design::

  $ cd asm_toy_2

CPython::

  $ PYTHONPATH='/Users/dmlockhart/vc/hg-opensource/pypy' \
    python interp_asm.py asm_04.s

RPython with no JIT::

  $ PYTHONPATH='/Users/dmlockhart/vc/hg-opensource/pypy' python \
    ~/vc/hg-opensource/pypy/rpython/translator/goal/translate.py \
    interp_asm.py
  $ ./interp_asm-c asm_04.s

------------------------------------------------------------------------
PARC ISA Interpreter
------------------------------------------------------------------------

This interpreter is a full interpreter for the PARC ISA! Note that as
an interpreter it expects assembly files, **not** binaries!

It includes a test runner script which can run a full array of PARC
assembly tests, it requires that PyMTL is installed on the local system.
To run the assembly tests with CPython::

  $ cd parc_interpreter
  $ py.test interp_asm_test.py --verbose --cpython

Before running the assembly tests with RPython, first compile the C
implmementation.

The C implementation **without** JIT (should take ~30 seconds)::

  $ PYTHONPATH='/Users/dmlockhart/vc/hg-opensource/pypy' python \
    ~/vc/hg-opensource/pypy/rpython/translator/goal/translate.py \
    interp_asm_jit.py

The C implementation **with** JIT (should take ~500 seconds)::

  $ PYTHONPATH='/Users/dmlockhart/vc/hg-opensource/pypy' python \
    ~/vc/hg-opensource/pypy/rpython/translator/goal/translate.py \
    --opt=jit \
    interp_asm_jit.py

The run the tests::

  $ py.test interp_asm_test.py --verbose

The the interpreter on an assembly file directly::

  $ ./interp_asm_jit-c test.s

------------------------------------------------------------------------
Untranslatable
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

