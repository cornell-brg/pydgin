========================================================================
README: PARC Instruction Set Simulator
========================================================================

A Pydgin description of the PARC ISA which implements an ISS capable of
executing ELF binaries.

------------------------------------------------------------------------
Building PARC Applications
------------------------------------------------------------------------

Without System Calls
--------------------

This repository should contain a copy of the simplified ubmarks (without
system calls) used in ECE4750. To compile them for PARC, first ensure
you have the maven cross compiler installed (available on the BRG
servers) and execute the following::

  $ cd ~/vcd/git-brg/pydgin/ubmark-nosyscalls
  $ mkdir build-parc
  $ cd build-parc
  $ ../configure --host=maven
  $ make ubmark-vvadd


With System Calls
------------------

The PARC ISS is also capable of executing more complicated benchmarks
with system calls. To build them, you must checkout and compile the
maven-apps-misc repository from Github::

  $ cd ~/vc/git-brg
  $ git clone git@github.com:cornell-brg/maven-app-misc.git
  $ mkdir ~/vc/git-brg/maven-app-misc/build-parc
  $ cd ~/vc/git-brg/maven-app-misc/build-parc
  $ ../configure --host=maven
  $ make

------------------------------------------------------------------------
Executing the PARC ISS
------------------------------------------------------------------------

With Python
-----------

The PARC ISS can be executed directly with a Python interpreter. While
slow, it provides a faster code-test-debug cycle than the compiled
interpreter. To execute, run::

  $ python pisa-sim.py ../ubmark-nosyscalls/build-parc/ubmark-vvadd

With C and JIT
--------------

Using the RPython translation toolchain, we can convert the PARC ISS
into a C executable with a JIT-optimizing compiler. To perform the
translation (takes ~5 minutes), run::

  $ PYTHONPATH='/work/bits0/dml257/hg-pypy/pypy' python \
    /work/bits0/dml257/hg-pypy/pypy/rpython/translator/goal/translate.py \
    --opt=jit \
    pisa-sim.py

To execute, run::

  $ pisa-sim-c ../ubmark-nosyscalls/build-parc/ubmark-vvadd

We can also generate a C executable *without* the JIT-optimizing
compiler by removing the ``--opt=jit`` flag.  While typically not as
high-performance as the JIT-enabled executable, compilation times are
much faster (30 seconds).

