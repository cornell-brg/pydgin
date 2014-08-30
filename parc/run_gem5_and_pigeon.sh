#! /bin/bash

BMARKS="ubmark-vvadd
ubmark-bin-search
ubmark-masked-filter
dither
rsort
strsearch
viterbi
rgb2cmyk
bfs
mstpbbs
knapsack
bintree
hist
"
#BMARKS="ubmark-cmplx-mult
#kmeans
#bksb
#mriq
#conv
#sgemm
#median
#covariance
#"

NTRIALS=100

for bmark in $BMARKS
do

  cd /work/bits0/dml257/gem5-mcpat/eval
  time ../build/MIPS/gem5.opt --outdir xxx-tmp ../configs/brg/se.py  --cpu-type=atomic --caches \
       -c /work/bits0/dml257/maven-app-misc/build-maven/$bmark -o "--ntrials $NTRIALS"
  echo "FINISHED gem5 $bmark"
  time ../build/MIPS/gem5.opt --outdir xxx-tmp ../configs/brg/se.py  --cpu-type=atomic --caches \
       -c /work/bits0/dml257/maven-app-misc/build-maven/$bmark -o "--ntrials $NTRIALS"
  echo "FINISHED gem5 $bmark"


  cd /work/bits0/dml257/rpython-isa-simulator/parc
  time ./pisa-sim-nojit /work/bits0/dml257/maven-app-misc/build-maven/$bmark --ntrials $NTRIALS
  echo "FINISHED nojit $bmark"
  time ./pisa-sim-nojit /work/bits0/dml257/maven-app-misc/build-maven/$bmark --ntrials $NTRIALS
  echo "FINISHED nojit $bmark"

  time ./pisa-sim-jit /work/bits0/dml257/maven-app-misc/build-maven/$bmark --ntrials $NTRIALS
  echo "FINISHED jit $bmark"
  time ./pisa-sim-jit /work/bits0/dml257/maven-app-misc/build-maven/$bmark --ntrials $NTRIALS
  echo "FINISHED jit $bmark"

done
