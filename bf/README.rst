========================================================================
README: BF Interpreter
========================================================================

BF is a very simple interpreter for the brainf*ck language.

------------------------------------------------------------------------
Quick Start
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
References
------------------------------------------------------------------------

- http://morepypy.blogspot.com/2011/04/tutorial-writing-interpreter-with-pypy.html
- http://morepypy.blogspot.co.uk/2011/04/tutorial-part-2-adding-jit.html

