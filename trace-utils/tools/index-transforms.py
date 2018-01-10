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

  # Select the task-size constraint
  tk_sz = int(math.ceil(n/float(kp))) # task size

  # Cache layout
  print "Cache Layout"
  num_lines = int(math.ceil(n/float(cl_sz)))
  for i in range(num_lines):
    end = (i+1)*cl_sz if (i+1)*cl_sz < n else n
    print ' '.join(['%4d' % i for i in range(i*cl_sz, end)])

  print "Transform to"

  # Check the number of available processors and cache-line size
  # NOTE: Assuming that "p" processors execute in space
  if p <= cl_sz:
    cl_sz = p

  # data should be accessed as below:
  #
  #                  <---task-size--->
  #
  #      ^        ^     beg      end
  #      |        |  p0
  #      |        |  p1
  #      | cl_sz  |  p2   Group 0
  #      |        |  p3
  #      |        |  p4
  #      |        v
  #      |          <---task-size--->
  # kp   |
  #      |       ^     beg      end
  #      |       |  p0
  #      |       |  p1
  #      |cl_sz  |  p2   Group 1
  #      |       |  p3
  #      |       |  p4
  #      v       v

  # for each task print the suggested access pattern
  for i in range(kp):

    group_sz  = (tk_sz * cl_sz)
    group_beg = (i/cl_sz)*group_sz

    if (n - group_beg) < group_sz:
      stride = int( math.ceil((n-group_beg)/float(tk_sz)) )
    else:
      stride = cl_sz

    beg = i%cl_sz+ (i/cl_sz)*(tk_sz*cl_sz)
    end = beg + tk_sz*stride

    if end > n:
      end = n

    print ' '.join(['%4d' % i for i in range(beg, end, stride)])
