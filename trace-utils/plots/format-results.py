from common import *
from common_configs import *

import pandas as pd

if __name__ == "__main__":
  df = pd.read_csv( "sim-results.csv" )
  df = format_work( df )
  df.to_csv( "sim-results-formatted.csv", index=False )
