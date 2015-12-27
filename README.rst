===============================================================================
|Pydgin|
===============================================================================

.. image:: https://travis-ci.org/cornell-brg/pydgin.svg
    :target: https://travis-ci.org/cornell-brg/pydgin

Pydgin: a (Py)thon (D)SL for (G)enerating (In)struction set simulators.

-------------------------------------------------------------------------------
Introduction
-------------------------------------------------------------------------------

Pydgin provides a collection of classes and functions which act as an embedded
architectural description language (embedded-ADL) for concisely describing the
behavior of instruction set simulators (ISS). An ISS described in Pydgin can be
directly executed in a Python interpreter for rapid prototyping and debugging,
or alternatively can be used to automatically generate a performant,
JIT-optimizing C executable more suitable for application development.

Automatic generation of JIT-enabled ISS from Pydgin is enabled by the RPython
Translation Toolchain, an open-source tool used by developers of the PyPy
JIT-optimizing Python interpreter.

An ISS described in Pydgin implements an *interpretive* simulator which can be
directly executed in a Python interpreter for rapid prototyping and debugging.
However, Pydgin ISS can also be automatically translated into a C executable
implementing a *JIT-enabled interpretive* simulator, providing a
high-performance implementation suitable for application development. Generated
Pydgin executables provide significant performance benefits in two ways. First,
the compiled C implementation enables much more efficient execution of
instruction-by-instruction interpretive simulation than the original Python
implementation. Second, the generated executable provides a trace-JIT to
dynamically compile frequently interpreted hot loops into optimized assembly.

.. |Pydgin| image:: docs/pydgin_logo.png

-------------------------------------------------------------------------------
License
-------------------------------------------------------------------------------

Pydgin is offered under the terms of the Open Source Initiative BSD
3-Clause License. More information about this license can be found here:

- http://choosealicense.com/licenses/bsd-3-clause
- http://opensource.org/licenses/BSD-3-Clause

-------------------------------------------------------------------------------
Publications
-------------------------------------------------------------------------------

If you end up using Pydgin in your research, please let us know!  We'd love to
hear your feedback. Also, you can cite our paper! ::

  @inproceedings{lockhart-pydgin-ispass2015,
    title     = {Pydgin: Generating Fast Instruction Set Simulators from
                 Simple Architecture Descriptions with Meta-Tracing JIT
                 Compilers},
    author    = {Derek Lockhart and Berkin Ilbeyi and Christopher Batten},
    booktitle = {2015 IEEE Int'l Symp. on Performance Analysis of Systems
                 and Software (ISPASS)},
    month     = {Mar},
    year      = {2015},
  }


-------------------------------------------------------------------------------
Project Subdirectories
-------------------------------------------------------------------------------

The following directories Pydgin libraries and simulator implementations for
executing ELF binaries compiled with a cross-compiler.

- pydgin:  Library for describing instruction set simulators (ISS).
- arm:     Pydgin ISS for executing ARMv5 binaries.
- parc:    Pydgin ISS for executing PARC binaries.

Please see the README files in each subdirectory for more information.

-------------------------------------------------------------------------------
Installing Dependencies
-------------------------------------------------------------------------------

Pydgin depends on the libraries provided by the RPython translation toolchain
for jit annotations and interpreter translation. Before running a Pydgin
simulator, please install the PyPy project source code and specify its location
by creating a PYDGIN_PYPY_SRC_DIR environment variable::

  $ hg clone https://bitbucket.org/pypy/pypy $SOME_DIR
  $ export PYDGIN_PYPY_SRC_DIR=$SOME_DIR/pypy

Pydgin simulator generation also works much faster if you have the PyPy
binary installed. You can either compile this yourself from source, or
download a precompiled version from the PyPy homepage.

- http://pypy.org/download.html

Note that if you download a tarball of the PyPy source instead of cloning it
from BitBucket, it must be version 2.5 or newer.

-------------------------------------------------------------------------------
Running Pydgin Instruction Set Simulators
-------------------------------------------------------------------------------

Now that PyPy dependencies are installed, you can run Pydgin simulators
directly with Python for debug purposes::

  $ cd arm
  $ python arm-sim.py <arm-binary>

Finally, you can translate the Pydgin simulators into JIT-enabled simulator
binaries using the RPython translation toolchain::

  $ cd scripts
  $ ./build.py --help
  $ ./build.py pydgin-arm-jit

The translation process will take several minutes. After it's done, you'll have
a fast simulator to run your binaries::

  $ ./builds/pydgin-arm-jit <arm-binary>

