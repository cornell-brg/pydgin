========================================================================
README: Toy Interpreter for Assembly 2
========================================================================

This interpreter is a similar to the asm_toy_1, but includes mtc0 and
mfc0 instructions for testing, as well as demonstrates how a register
map can be used to simplify the interpreter design.

------------------------------------------------------------------------
Quick Start
------------------------------------------------------------------------

Running the simple interpreter in CPython::

  $ PYTHONPATH='/Users/dmlockhart/vc/hg-opensource/pypy' \
    python interp_asm.py asm_04.s

Using RPython to create an interpreter with no JIT::

  $ PYTHONPATH='/Users/dmlockhart/vc/hg-opensource/pypy' python \
    ~/vc/hg-opensource/pypy/rpython/translator/goal/translate.py \
    interp_asm.py
  $ ./interp_asm-c asm_04.s

