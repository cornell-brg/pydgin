#=======================================================================
# polyhs_types.py
#=======================================================================
# Implementation details for the polyhs project

VECTOR = 0
LIST   = 1

def iterator_fields( val ):
  ds_id     = ( val >> 24 ) & 0xff
  iter_bits = ( val & 0xffffff )
  return [ds_id, iter_bits]

def dt_desc_fields( val ):
  offset = ( val >> 24 ) & 0xff
  size_  = ( val >> 16 ) & 0xff
  type_  = ( val >> 8  ) & 0xff
  fields = ( val & 0xff )
  return [ offset, size_, type_, fields ]
