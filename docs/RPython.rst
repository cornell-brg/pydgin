========================================================================
RPython Resources
========================================================================

Pydgin is built on the RPython translation toolchain to enable to
generation of high-performance, tracing-JIT DBT ISS from succinct ISA
descriptions in Python.

Recently the PyPy developers released dedicated documentation for the
RPython translation toolchain. This documentation is a good starting
point for anyone interested in using RPython:

- https://rpython.readthedocs.org/en/latest/

Before the above documentation was available, we used a number of
sources to learn about how to build interpreters using the RPython
toolchain and how to add JIT annotations to improve the performance of
the RPython-generated tracing-JIT. These references are listed below.

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

