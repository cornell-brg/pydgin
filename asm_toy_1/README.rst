========================================================================
README: Toy Interpreter for Assembly 2
========================================================================

This interpreter is a very basic foundation for an ISA interpreter, it
only includes addiu, addu, and print instructions.  It is useful seeing
the minimal code needed to make a simple ISA interpreting simulator.

------------------------------------------------------------------------
Quick Start
------------------------------------------------------------------------

Running the simple interpreter in CPython::

  $ PYTHONPATH='/Users/dmlockhart/vc/hg-opensource/pypy' \
    python simple_asm.py asm_00.s

Using RPython to create an interpreter with no JIT::

  $ PYTHONPATH='/Users/dmlockhart/vc/hg-opensource/pypy' python \
    ~/vc/hg-opensource/pypy/rpython/translator/goal/translate.py \
    simple_asm.py
  $ ./simple_asm-c asm_00.s

