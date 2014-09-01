#!/usr/bin/env python
#=========================================================================
# gen_timing_table.py
#=========================================================================
# Generates a table using the output of run_gem5_and_pigeon.sh. Example
# usage:
#
# % ./run_gem5_and_pigeon.sh &> out.sh
# % ./gen_timing_table.py out.sh > timing.rst

import sys, re

all_impls = []
all_bmarks = []
results = {}


def main():
  if len( sys.argv ) <= 1:
    print "Usage: ./gen_timing_table.py <file>"
    return

  # open file

  filename = sys.argv[1]
  f = open( filename )

  experiment = {}

  # loop line by line

  for l in f:

    # split the line and match for keywords

    toks = l.split()

    if len( toks ) == 0:
      continue

    elif toks[0] == "timing":
      experiment["stats_cycle"] = int( toks[2] )

    elif toks[0] == "total":
      experiment["total_cycle"] = int( toks[2] )

    elif toks[0] == "DONE!":

      # this is to make sure the program ran correctly
      status = int( toks[3] )
      if status != 1:
        sys.stderr.write( "Status not 1! ({})\n".format( status ) )

    elif toks[0] == "real":
      # this is the timing info, in a format like 0m0.008s. so we use
      # a simple regex to get the fields

      r = re.compile( "[ms]" )
      time_fields = r.split( toks[1] )

      experiment["time"] = 60 * int( time_fields[0] ) + \
                           float( time_fields[1] )

    elif toks[0] == "FINISHED":
      # this marks that the experiment is finished

      _, impl, bmark = toks

      # we check the global benchmark and impl lists to see if these have
      # been added there

      if impl not in all_impls:
        all_impls.append( impl )

      if bmark not in all_bmarks:
        all_bmarks.append( bmark )

      if bmark not in results:
        result = experiment
        results[bmark] = result
      else:
        result = results[ bmark ]

      if impl not in result:
        result[ impl ] = ( experiment[ "time" ], 1 )
      else:
        old_time, num_trials = result[ impl ]

        # we calculate a new average time
        new_time = ( (old_time * num_trials) + experiment["time"] ) / \
                   ( num_trials + 1 )

        result[ impl ] = ( new_time, num_trials + 1 )

      experiment = {}

  line_templ = "{:<20} {:<10} {:<10}"
  header_templ = line_templ
  extra_header_templ = " {:<8}"
  extra_templ = " {:<8.2f}"

  line_templ += len( all_impls ) * extra_templ * 2
  header_templ += len( all_impls ) * extra_header_templ * 2

  # print header

  header_fields = [ "benchmark", "stats ins", "total ins"]

  for impl in all_impls:
    header_fields.extend( [impl, "mips"] )

  print header_templ.format( *header_fields )

  for bmark in all_bmarks:
    result = results[ bmark ]

    def lookup( f ):
      if f not in result:
        return ""
      else:
        return result[ f ]

    fields = [ bmark, lookup( "stats_cycle" ), lookup( "total_cycle" ) ]
    for impl in all_impls:
      time = result[impl][0] if impl in result else 0.0
      tot_ins = lookup( "total_cycle" )

      mips = 0.0
      if tot_ins != "":
        mips = float( tot_ins ) / time / 1000000.0

      fields.extend( [ time, mips ] )

    print line_templ.format( *fields )

main()
