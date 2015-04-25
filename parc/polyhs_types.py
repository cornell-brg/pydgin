#=======================================================================
# polyhs_types.py
#=======================================================================
# Implementation details for the polyhs project

VECTOR = 0
LIST   = 1

def iterator_fields( val ):
   return ( val >> 24 ) & 0xf, ( val & 0xffffff )

def size_( val ):
  return ( val >> 16 ) & 0xf
