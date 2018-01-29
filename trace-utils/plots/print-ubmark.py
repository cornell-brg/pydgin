#=========================================================================
# print-ubmark.py
#=========================================================================
# Author : Shreesha Srinath
# Date   : January 29th, 2018
#
# Quick and dirty script to parse ubmark-results

import pandas as pd

if __name__ == "__main__":

  df = pd.read_csv( "sim-results.csv" )

  print "{:^36s}".format("Configuration") + "{:^6s}".format("Redn.") + "{:^6s}".format("Perf.")
  base_str = "ubmark-wsrt-1L0-1F-2R-%dA-%dL-%dS-%d"
  for smart_sharing in range(2):
    for selection in range(2):
      for lockstep in range(2):
        for hint in [1,1000]:
          config = base_str % (
            selection,
            lockstep,
            smart_sharing,
            hint
          )
          print "{:36s}".format(config),
          stats = df.loc[df.config == config,["steps","iredundancy"]]
          print "{:6.2f}".format( float(stats["iredundancy"]) ),
          print "{:6d}".format( int(stats["steps"]) )

