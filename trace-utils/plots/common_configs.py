#=========================================================================
# common_configs.py
#=========================================================================
# Lists and dicts that have all the configs used, and their short names
#
# Author : Shreesha Srinath
# Date   : February 25th, 2018
#

import re
from collections import OrderedDict

#-------------------------------------------------------------------------
# Config template strings
#-------------------------------------------------------------------------

# config template strings
g_mimd_base_str     = 'mimd-%s-1-0AH'
g_mimd_config_str   = 'mimd-%s-%d-%dAH'
g_ccores_config_str = 'conj-cores-%s-1L0-%dI-%dF-%dL-%dC-%dTS-%dLO-%d-%dLL-%dAH'
g_simt_config_str   = 'simt-%s-1L0-%dI-%dF-%dL-1C-%dTS-1LO-%d-%dLL-%dAH'
g_mt_config_str     = 'mt-%s-%dTS-%d-%dAH'

#-------------------------------------------------------------------------
# populate_mimd_configs()
#-------------------------------------------------------------------------

def populate_mimd_configs( runtime, basic=True ):
  config_list = []
  for barrier_limit in [1,1000]:
    for adaptive_hint in range( 2 ):
      if basic and adaptive_hint == 1:
        continue
      config_str = g_mimd_config_str % (
        runtime,
        barrier_limit,
        adaptive_hint
      )
      config_list.append( config_str )
  return config_list

#-------------------------------------------------------------------------
# populate_ccores_configs()
#-------------------------------------------------------------------------
# NOTE: based on the inputs generate either mimd-static or ccores cfgs

def populate_ccores_configs( runtime, insn_ports, ncores, resources, basic=True ):
  config_list = []
  for smart_sharing in range( 2 ):
    for lockstep in range( 2 ):
      for limit_lockstep in range( 2 ):
        if basic and limit_lockstep == 1:
          continue
        for analysis in [0,1]:
          for barrier_limit in [1,1000]:
            for adaptive_hint in range( 2 ):
              if basic and adaptive_hint == 1:
                continue
              config_str = g_ccores_config_str % (
                runtime,
                insn_ports,
                ncores,
                resources,
                smart_sharing,
                analysis,
                lockstep,
                barrier_limit,
                limit_lockstep,
                adaptive_hint
              )
              config_list.append( config_str )
  return config_list

#-------------------------------------------------------------------------
# populate_simt_configs()
#-------------------------------------------------------------------------
# NOTE: based on the inputs generate either simt-static or simt cfgs

def populate_simt_configs( runtime, frontend, resources, basic=True ):
  config_list = []
  for limit_lockstep in range( 2 ):
    if basic and limit_lockstep == 1:
      continue
    for analysis in [0,1]:
      for barrier_limit in [1,1000]:
        for adaptive_hint in range( 2 ):
          if basic and adaptive_hint == 1:
            continue
          config_str = g_simt_config_str % (
            runtime,
            frontend,
            frontend,
            resources,
            analysis,
            barrier_limit,
            limit_lockstep,
            adaptive_hint
          )
          config_list.append( config_str )
  return config_list

#-------------------------------------------------------------------------
# populate_mt_configs()
#-------------------------------------------------------------------------

def populate_mt_configs( runtime, basic=True ):
  config_list = []
  for analysis in [0,1]:
    for barrier_limit in [1,1000]:
      for adaptive_hint in range( 2 ):
        if basic and adaptive_hint == 1:
          continue
        config_str = g_mt_config_str % (
          runtime,
          analysis,
          barrier_limit,
          adaptive_hint
        )
        config_list.append( config_str )
  return config_list

#-------------------------------------------------------------------------
# populate configs
#-------------------------------------------------------------------------
# return a dictionary that has grouped various configs indexed by the
# static uarch configuration

def populate_configs( runtime, basic=True ):
  max_resources = 4
  group_dict = OrderedDict()
  # mimd-static
  for insn_ports in [1,2]:
    group_dict['mimd-static-%d' % insn_ports] = populate_ccores_configs( runtime, insn_ports, max_resources, max_resources, basic )
  # simt-static
  for frontend in [1,2]:
    group_dict['simt-static-%d' % frontend] = populate_simt_configs( runtime, frontend, max_resources, basic )
  # ccores
  for resources in [1,2]:
    group_dict['ccores-%d' % resources] = populate_ccores_configs( runtime, resources, max_resources, resources, basic )
  # simt
  for resources in [1,2]:
    group_dict['simt-%d' % resources ] = populate_simt_configs( runtime, resources, resources, basic )
  # mt
  group_dict['mt'] = populate_mt_configs( runtime, basic )

  return group_dict

#-------------------------------------------------------------------------
# Clean names for static uarch configs
#-------------------------------------------------------------------------

g_cfg_labels_dict = OrderedDict([
  ('mimd',         'mimd'        ),
  ('mimd-static-1','cl-1I-4f-4l' ),
  ('mimd-static-2','cl-2I-4f-4l' ),
  ('simt-static-1','cl-1I-1f-4l' ),
  ('simt-static-2','cl-2I-2f-4l' ),
  ('ccores-1',     'cl-4I-4f-1l' ),
  ('ccores-2',     'cl-4I-4f-2l' ),
  ('simt-1',       'cl-1I-1f-1l' ),
  ('simt-2',       'cl-2I-2f-2l' ),
  ('mt',           'mt'          ),
])
g_cfg_labels = g_cfg_labels_dict.values()

#-------------------------------------------------------------------------
# format_config_names()
#-------------------------------------------------------------------------

def format_config_names( basic=True ):
  max_resources = 4
  configs_list   = []
  for runtime in ['spmd','wsrt']:
    for resources in [1,2]:
      # mimd-static
      configs_list += populate_ccores_configs( runtime, resources, max_resources, max_resources )
      # simt-static
      configs_list += populate_simt_configs( runtime, resources, max_resources )
      # ccores
      configs_list += populate_ccores_configs( runtime, resources, max_resources, resources )
      # simt
      configs_list += populate_simt_configs( runtime, resources, resources )
    configs_list += populate_mt_configs( runtime )
  configs_dict = {}
  for cfg in configs_list:
    name = cfg.lower()
    name = re.sub( '-1l0-',            '-',        name )
    name = re.sub( '-(\d)lo-',         '-\g<1>l-', name )
    name = re.sub( '-1-',              '-0h-',     name )
    name = re.sub( '-1000-',           '-1h-',     name )
    name = re.sub( '-0ts-',            '-rr-',     name )
    name = re.sub( '-1ts-',            '-pc-',     name )
    name = re.sub( 'conj-cores-wsrt-', 'cl-',      name )
    name = re.sub( 'conj-cores-spmd-', 'cl-',      name )
    name = re.sub( 'simt-wsrt-',       'cl-',      name )
    name = re.sub( 'simt-spmd-',       'cl-',      name )
    name = re.sub( 'mt-spmd-',         'mt-',      name )
    name = re.sub( 'mt-wsrt-',         'mt-',      name )
    if basic:
      name = re.sub( '-\dll', '', name )
      name = re.sub( '-\dah', '', name )
    configs_dict[cfg] = name
  return configs_dict
