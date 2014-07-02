=========================================================================
RPython Tutorial
=========================================================================

Beginner References
-------------------

- http://www.wilfred.me.uk/blog/2014/05/24/r-python-for-fun-and-profit/
- http://morepypy.blogspot.com/2011/04/tutorial-writing-interpreter-with-pypy.html
- http://morepypy.blogspot.co.uk/2011/04/tutorial-part-2-adding-jit.html
- https://bitbucket.org/brownan/pypy-tutorial/

Quick Start
-----------

Running a brainf*ck interpreter in CPython::

  $ python tutorial_bf_part1.py tutorial_99.b

Creating a C interpreter for brainf*ck using RPython
(requires that pypy source is installed):: 

  $ PYTHONPATH='/Users/dmlockhart/vc/hg-opensource/pypy' python \
    ~/vc/hg-opensource/pypy/rpython/translator/goal/translate.py \
    tutorial_bf_part1.py

Running a brainf*ck interpreter translated to C via RPython::

  $ ./tutorial_bf_part1-c tutorial_99.b

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


Advanced References
-------------------

- http://morepypy.blogspot.com/2011/03/controlling-tracing-of-interpreter-with.html
- http://morepypy.blogspot.com/2011/03/controlling-tracing-of-interpreter-with_15.html
- http://morepypy.blogspot.com/2011/03/controlling-tracing-of-interpreter-with_21.html
- http://morepypy.blogspot.com/2011/03/controlling-tracing-of-interpreter-with_26.html
- http://bitbucket.org/pypy/extradoc/raw/extradoc/talk/icooolps2011/bolz-hints.pdf

