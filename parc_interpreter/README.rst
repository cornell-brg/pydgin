========================================================================
README: PARC ISA Interpreter
========================================================================

This interpreter is a full interpreter for the PARC ISA! Note that as
an interpreter it expects assembly files, **not** binaries!

------------------------------------------------------------------------
Testing the Interpreter
------------------------------------------------------------------------

Included is a test runner script which can run a full array of PARC
assembly tests. It requires that both PyMTL and the py.test Python
package is installed on the local system. To run the assembly tests with
CPython::

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

