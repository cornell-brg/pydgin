#=========================================================================
# index-transforms.py
#=========================================================================
# HACKY script for figuring out the right transformations that could aid
# dmem coalescing

import math

if __name__ == "__main__":

  n     = 100  # problem size
  k     = 2    # decomposition factor
  p     = 4    # number of physical cores
  kp    = k*p  # logical cores
  cl_sz = 4    # cache line size

  if n%kp == 0:
    tk_sz = n/kp
  else:
    tk_sz = int(math.ceil(n/kp+1)) # task size

  # cache-layout
  print "Cache Layout"
  num_lines = n/cl_sz if n%cl_sz == 0 else int(math.ceil(n/cl_sz)+1)
  for i in range(num_lines):
    end = (i+1)*cl_sz if (i+1)*cl_sz < n else n
    print ' '.join(['%4d' % i for i in range(i*cl_sz, end)])

  print "Transform to"
  # Check the relationship of
  #  kp, tk_sz, cl_sz
  if kp <= cl_sz and tk_sz >= kp:
    cl_sz = kp

  for i in range(kp):
    beg = i%cl_sz + (i/cl_sz)*(tk_sz*cl_sz)
    end = beg + (tk_sz-1)*cl_sz + 1
    stride = cl_sz

    if end > n:
      end = n

    # NOTE: THIS NEEDS TO BE FIXED
    # eg test: cl_sz=6, kp=8, n=32
    # unequal divisions...
    #if end > n and beg+end > n:
    #  beg = i*tk_sz
    #  end = (i+1)*tk_sz if (i+1)*tk_sz < n else n
    #  stride = 1
    ## cap the end
    #elif end > n:
    #  end = n

    print ' '.join(['%4d' % i for i in range(beg, end, stride)])

