#=======================================================================
# polyhs_types.py
#=======================================================================
# Data-structure types as in the ISA doc
#
#   +----------+---------------+---------------+
#   | DS       | Obj Type      | immediate_val |
#   +----------+---------------+---------------+
#   | vector   | char          | 0             |
#   |          | int           | 1             |
#   |          | float         | 2             |
#   |          | pointer       | 3             |
#   |          | user-defined  | 4             |
#   --------------------------------------------
#   | list     | char          | 5             |
#   |          | int           | 6             |
#   |          | float         | 7             |
#   |          | pointer       | 8             |
#   |          | user-defined  | 9             |
#   --------------------------------------------

VECTOR_CHAR    = 0
VECTOR_INT     = 1
VECTOR_FLOAT   = 2
VECTOR_POINTER = 3
VECTOR_UTYPE   = 4
LIST_CHAR      = 5
LIST_INT       = 6
LIST_FLOAT     = 7
LIST_POINTER   = 8
LIST_UTYPE     = 9

def sizeof( index ):

  if   index == VECTOR_CHAR   : return 1
  elif index == VECTOR_INT    : return 4
  elif index == VECTOR_FLOAT  : return 4
  elif index == VECTOR_POINTER: return 4
  elif index == VECTOR_UTYPE  : return 4
  elif index == LIST_CHAR     : return 1
  elif index == LIST_INT      : return 4
  elif index == LIST_FLOAT    : return 4
  elif index == LIST_POINTER  : return 4
  elif index == LIST_UTYPE    : return 4
