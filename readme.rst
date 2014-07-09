=========================================================================
RPython Tutorial
=========================================================================

Beginner References
-------------------

- http://www.wilfred.me.uk/blog/2014/05/24/r-python-for-fun-and-profit/
- http://morepypy.blogspot.com/2011/04/tutorial-writing-interpreter-with-pypy.html
- http://morepypy.blogspot.co.uk/2011/04/tutorial-part-2-adding-jit.html
- https://bitbucket.org/brownan/pypy-tutorial/

- http://pie-interpreter.blogspot.com/2012/12/how-to-make-new-interpreter-with-pypy.html

- http://indefinitestudies.org/2010/02/08/creating-a-toy-virtual-machine-with-pypy

Quick Start
-----------

Running a brainf*ck interpreter in CPython::

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

ISA Sim
-------

CPython::

  $ PYTHONPATH='/Users/dmlockhart/vc/hg-opensource/pypy' python interp_asm.py asm_04.s

RPython::

  $ PYTHONPATH='/Users/dmlockhart/vc/hg-opensource/pypy' python \
    ~/vc/hg-opensource/pypy/rpython/translator/goal/translate.py
    interp_asm.py
  $ ./interp_asm-c asm_04.s



Advanced References
-------------------

- http://morepypy.blogspot.com/2011/03/controlling-tracing-of-interpreter-with.html
- http://morepypy.blogspot.com/2011/03/controlling-tracing-of-interpreter-with_15.html
- http://morepypy.blogspot.com/2011/03/controlling-tracing-of-interpreter-with_21.html
- http://morepypy.blogspot.com/2011/03/controlling-tracing-of-interpreter-with_26.html
- http://bitbucket.org/pypy/extradoc/raw/extradoc/talk/icooolps2011/bolz-hints.pdf
- http://pypy.readthedocs.org/en/latest/jit/pyjitpl5.html
- http://morepypy.blogspot.com/2010/06/jit-for-regular-expression-matching.html
- https://github.com/samgiles/naulang/blob/master/naulang/compiler/parser.py
- https://github.com/alex/rply


Untranslatable
==============

Fails:
  int( some_str, base=16 )
Translates, but fails during execution:
  int( some_str, 16 )
Works:
  rpython.rlib.rarithmetic.string_to_int( some_str, base=16 )

Fails:
  line.split()
Works:
  line.split(' ', 3)

