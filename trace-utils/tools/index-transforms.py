#=========================================================================
# index-transforms.py
#=========================================================================
# HACKY script for figuring out the right transformations that could aid
# dmem coalescing

import math

if __name__ == "__main__":

  n     = 100   # problem size
  kp    = 8     # logical cores
  cl_sz = 16    # cache line size
  tk_sz = n/kp  # task size

  # cache-layout
  print "Cache Layout"
  for i in range(int(math.ceil( n/cl_sz ))):
    end = (i+1)*cl_sz if i+cl_sz < n else n
    print ' '.join(['%4d' % i for i in range(i*cl_sz, end)])
  print

  print "Transform to"
  # Check the relationship of
  #  kp, tk_sz, cl_sz
  if kp <= cl_sz and tk_sz >= kp:
    cl_sz = kp
  for i in range(kp):
    beg = i%cl_sz + (i/cl_sz)*(tk_sz*cl_sz)
    end = beg + (tk_sz-1)*cl_sz
    stride = cl_sz
    # cap the end
    if end > n and beg+end < n:
      end = n
    # unequal divisions...
    elif end > n and beg+end > n:
      beg = i*tk_sz
      end = (i+1)*tk_sz-1 if (i+1)*tk_sz-1 < n else n
      stride = 1

    print ' '.join(['%4d' % i for i in range(beg, end+1, stride)])

