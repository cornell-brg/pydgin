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

from common import *

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

def populate_mimd_configs( basic=True ):
  config_list = []
  for runtime in ['spmd','wsrt']:
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

def populate_ccores_configs( insn_ports, ncores, resources, basic=True ):
  skip_lockstep = False
  if ncores == resources:
    skip_lockstep = True
  config_list = []
  for runtime in ['spmd','wsrt']:
    for smart_sharing in range( 2 ):
      for lockstep in range( 2 ):
        if skip_lockstep and lockstep == 1:
          continue
        for limit_lockstep in range( 2 ):
          if basic and limit_lockstep == 1:
            continue
          elif lockstep == 0 and limit_lockstep == 1:
            continue
          for analysis in [0,1]:
            for barrier_limit in [1,1000]:
              for adaptive_hint in range( 2 ):
                if basic and adaptive_hint == 1:
                  continue
                elif barrier_limit == 1 and adaptive_hint == 1:
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

def populate_simt_configs( frontend, resources, basic=True ):
  config_list = []
  for runtime in ['spmd','wsrt']:
    for limit_lockstep in range( 2 ):
      if basic and limit_lockstep == 1:
        continue
      for analysis in [0,1]:
        for barrier_limit in [1,1000]:
          for adaptive_hint in range( 2 ):
            if basic and adaptive_hint == 1:
              continue
            elif barrier_limit == 1 and adaptive_hint == 1:
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

def populate_mt_configs(  basic=True ):
  config_list = []
  for runtime in ['spmd','wsrt']:
    for analysis in [0,1]:
      for barrier_limit in [1,1000]:
        for adaptive_hint in range( 2 ):
          if basic and adaptive_hint == 1:
            continue
          elif barrier_limit == 1 and adaptive_hint == 1:
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

def populate_configs( basic=True ):
  max_resources = 4
  group_dict = OrderedDict()
  # mimd-static
  for insn_ports in [1,2]:
    group_dict['mimd-static-%d' % insn_ports] = populate_ccores_configs( insn_ports, max_resources, max_resources, basic )
  # simt-static
  for frontend in [1,2]:
    group_dict['simt-static-%d' % frontend] = populate_simt_configs( frontend, max_resources, basic )
  # ccores
  for resources in [1,2]:
    group_dict['ccores-%d' % resources] = populate_ccores_configs( resources, max_resources, resources, basic )
  # simt
  for resources in [1,2]:
    group_dict['simt-%d' % resources ] = populate_simt_configs( resources, resources, basic )
  # mt
  group_dict['mt'] = populate_mt_configs( basic )

  return group_dict

#-------------------------------------------------------------------------
# Clean names for static uarch configs
#-------------------------------------------------------------------------

g_cfg_labels_dict = OrderedDict([
  ('mimd',         'mimd'        ),
  ('mimd-static-1','cl-1i-4f-4l' ),
  ('mimd-static-2','cl-2i-4f-4l' ),
  ('simt-static-1','cl-1i-1f-4l' ),
  ('simt-static-2','cl-2i-2f-4l' ),
  ('ccores-1',     'cl-1i-4f-1l' ),
  ('ccores-2',     'cl-2i-4f-2l' ),
  ('simt-1',       'cl-1i-1f-1l' ),
  ('simt-2',       'cl-2i-2f-2l' ),
  ('mt',           'mt'          ),
])
g_cfg_labels = g_cfg_labels_dict.values()

#-------------------------------------------------------------------------
# format_config_names()
#-------------------------------------------------------------------------

def format_config_names( basic=True ):
  max_resources = 4
  configs_list   = []
  for resources in [1,2]:
    # mimd-static
    configs_list += populate_ccores_configs( resources, max_resources, max_resources, basic )
    # simt-static
    configs_list += populate_simt_configs( resources, max_resources, basic )
    # ccores
    configs_list += populate_ccores_configs( resources, max_resources, resources, basic )
    # simt
    configs_list += populate_simt_configs( resources, resources, basic )
  configs_list += populate_mt_configs( basic )
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

#-------------------------------------------------------------------------
# format work
#-------------------------------------------------------------------------
# NOTE: function fixes the total work columns in the data frame by
# recounting the work components specifically for the dynamic sharing.
# Currently the simulator reports dynamic sharing and this function
# disables it.

def format_work( df ):
  df['total_mem']  = df['total_iaccess'] + df['total_daccess']
  df['unique_mem'] = df['unique_iaccess'] + df['unique_daccess']

  # get all the groups partitioned by the uarchs
  group_dict = populate_configs( basic=False )

  # mimd-static
  work_labels = ['unique_daccess', 'total_execute', 'total_frontend', 'unique_iaccess']
  for insn_ports in [1,2]:
    group_key   = "mimd-static-%d" % insn_ports
    config_list = group_dict[group_key]
    for app in app_list:
      for cfg in config_list:
        try:
          work = 0
          for label in work_labels:
            work += df.loc[(df.app==app) & (df.config == cfg), label].iloc[0]
          df.loc[(df.app==app) & (df.config == cfg), 'unique_work'] = work
          df.loc[(df.app==app) & (df.config == cfg), 'unique_frontend'] = \
            df.loc[(df.app==app) & (df.config == cfg), 'total_frontend']
          df.loc[(df.app==app) & (df.config == cfg), 'unique_execute'] = \
            df.loc[(df.app==app) & (df.config == cfg), 'total_execute']
        except:
          continue

  # ccores
  work_labels = ['unique_daccess', 'total_execute', 'total_frontend', 'unique_iaccess']
  for resources in [1,2]:
    group_key   = "ccores-%d" % resources
    config_list = group_dict[group_key]
    for app in app_list:
      for cfg in config_list:
        try:
          work = 0
          for label in work_labels:
            work += df.loc[(df.app==app) & (df.config == cfg), label].iloc[0]
          df.loc[(df.app==app) & (df.config == cfg), 'unique_work'] = work
          df.loc[(df.app==app) & (df.config == cfg), 'unique_frontend'] = \
            df.loc[(df.app==app) & (df.config == cfg), 'total_frontend']
          df.loc[(df.app==app) & (df.config == cfg), 'unique_execute'] = \
            df.loc[(df.app==app) & (df.config == cfg), 'total_execute']
        except:
          continue

  # simt-static
  work_labels = ['unique_daccess', 'total_execute', 'unique_frontend', 'unique_iaccess']
  for frontend in [1,2]:
    group_key   = "simt-static-%d" % frontend
    config_list = group_dict[group_key]
    for app in app_list:
      for cfg in config_list:
        try:
          work = 0
          for label in work_labels:
            work += df.loc[(df.app==app) & (df.config == cfg), label].iloc[0]
          df.loc[(df.app==app) & (df.config == cfg), 'unique_work'] = work
          df.loc[(df.app==app) & (df.config == cfg), 'unique_execute'] = \
            df.loc[(df.app==app) & (df.config == cfg), 'total_execute']
        except:
          continue

  # simt
  work_labels = ['unique_daccess', 'total_execute', 'unique_frontend', 'unique_iaccess']
  for resources in [1,2]:
    group_key   = "simt-%d" % resources
    config_list = group_dict[group_key]
    for app in app_list:
      for cfg in config_list:
        try:
          work = 0
          for label in work_labels:
            work += df.loc[(df.app==app) & (df.config == cfg), label].iloc[0]
          df.loc[(df.app==app) & (df.config == cfg), 'unique_work'] = work
          df.loc[(df.app==app) & (df.config == cfg), 'unique_execute'] = \
            df.loc[(df.app==app) & (df.config == cfg), 'total_execute']
        except:
          continue

  # mt
  work_labels = ['unique_daccess', 'unique_execute', 'unique_frontend', 'unique_iaccess']
  group_key   = "mt"
  config_list = group_dict[group_key]
  for app in app_list:
    for cfg in config_list:
      try:
        work = 0
        for label in work_labels:
          work += df.loc[(df.app==app) & (df.config == cfg), label].iloc[0]
        df.loc[(df.app==app) & (df.config == cfg), 'unique_work'] = work
      except:
        continue

  return df

#-------------------------------------------------------------------------
# filter configs
#-------------------------------------------------------------------------
# NOTE: there is probably a much better way to this but I'm using what
# works well enough for now

def filter_configs( pattern, configs_list ):
  # list with the pattern
  present_list  = []
  # list without the pattern
  absent_list = []
  for cfg in configs_list:
    if re.search( pattern, cfg ):
      present_list.append( cfg )
    else:
      absent_list.append( cfg )
  return present_list, absent_list
