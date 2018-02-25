#! /usr/bin/env python
#=========================================================================
# brg_plot.py
#=========================================================================
# Plot library which is based on TSG plot and the XLOOPS project

"""
Library for plotting.

Classes:
  PlotOptions
    Object passed to plotting function that defines options.

Functions:
  add_plot( opt )
  add_line_plot( ax, opt )
  add_histogram_plot( ax, opt )
  add_boxplot_plot( ax, opt )
  add_heatmap_plot( ax, opt )
  add_scatter_plot( ax, opt )
  add_bar_plot( ax, opt )
  set_legend( ax, opt, legend, legend_labels )
  set_common( ax, opt )
  main()
"""

import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import random
import sys


# This defines various color schemes. These are pulled from colorbrewer2.org
colors = {
    # Sequential PuBuGn
    'pubugn3' : ['#ece2f0', '#a6bddb', '#1c9099'],
    'pubugn4' : ['#f6eff7', '#bdc9e1', '#67a9cf', '#02818a'],
    'pubugn5' : ['#f6eff7', '#bdc9e1', '#67a9cf', '#1c9099', '#016c59'],
    'pubugn6' : ['#f6eff7', '#d0d1e6', '#a6bddb', '#67a9cf', '#1c9099', '#016c59'],
    'pubugn7' : ['#f6eff7', '#d0d1e6', '#a6bddb', '#67a9cf', '#3690c0', '#02818a', '#016450'],
    'pubugn8' : ['#f6eff7', '#d0d1e6', '#a6bddb', '#67a9cf', '#3690c0', '#02818a', '#016450'],
    'pubugn9' : ['#fff7fb', '#ece2f0', '#d0d1e6', '#a6bddb', '#67a9cf', '#3690c0', '#02818a', '#016c59', '#014636'],

    # Sequential Blues
    'blue3' : ['#deebf7', '#9ecae1', '#3182bd'], # 3-class Blues
    'blue4' : ['#eff3ff', '#bdd7e7', '#6baed6', '#2171b5'], # 4-class Blues
    'blue5' : ['#eff3ff', '#bdd7e7', '#6baed6', '#3182bd', '#08519c'], # 5-class Blues

    # Sequential Reds
    'red3' : ['#fee0d2', '#fc9272', '#de2d26'], # 3-class Reds
    'red4' : ['#fee5d9', '#fcae91', '#fb6a4a', '#cb181d'], # 4-class Reds
    'red5' : ['#fee5d9', '#fcae91', '#fb6a5a', '#de2d26', '#a50f15'], # 5-class Reds

    # Sequential Greens
    'green3' : ['#e5f5e0', '#a1d99b', '#31a354'], # 3-class Greens
    'green4' : ['#edf8e9', '#bae4b3', '#74c476', '#238b45'], # 4-class Greens
    'green5' : ['#edf8e9', '#bae4b3', '#74c476', '#31a354', '#006d2c'], # 5-class Greens

    # Sequential Greys
    'grey3' : ['#f0f0f0', '#bdbdbd', '#636363'], # 3-class Greys
    'grey4' : ['#f7f7f7', '#cccccc', '#969696', '#525252'], # 4-class Greys
    'grey5' : ['#f7f7f7', '#cccccc', '#969696', '#636363', '#252525'], # 5-class Greys

    # Sequential Oranges
    'orange3' : ['#fee6ce', '#fdae6b', '#e6550d'], # 3-class Oranges
    'orange4' : ['#feedde', '#fdbe85', '#fd8d3c', '#d94701'], # 4-class Oranges
    'orange5' : ['#feedde', '#fdbe85', '#fd8d3c', '#e6550d', '#a63603'], # 5-class Oranges

    # Sequential Purples
    'purple3' : ['#efedf5', '#bcbddc', '#756bb1'], # 3-class Purples
    'purple4' : ['#f2f0f7', '#cbc9e2', '#9e9ac8', '#6a51a3'], # 4-class Purples
    'purple5' : ['#f2f0f7', '#cbc9e2', '#9e9ac8', '#756bb1', '#54278f'], # 5-class Purples

    # Qualitative (Multi-colored)
    'qualitative' : ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#f77f00',
      '#ffff33', '#a65628', '#f781bf', '#999999'], # 9-class Set 1
    'qualitative_paired' : ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c',
      '#fb9a99', '#e31a1c', '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a',
      '#000000', '#b15928'], # 12-class Paired

    # 20 unique colors
    # picked from here:
    # https://github.com/vega/vega/wiki/Scales#scale-range-literals
    'unique20' : [
      '#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
      '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f', '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5',
    ]
  }

class PlotOptions:

  def __init__( self ):

    # default values
    self.title = None
    self.ylabel = None
    self.xlabel = None
    self.bar_width = 0.70

    self.valid_plot_types = [
        'bar',
        'clustered_stacked_bar',
        'stacked_bar',
        'scatter_bar',
        'scatter',
        'line',
        'histogram',
        'boxplot',
        'heatmap'
        ]
    self.plot_type = 'bar'

    # Can provide multiple file names seperated by spaces
    self.file_name = ""
    # option to rotate labels when there are many of them
    self.rotate_labels = False
    self.rotate_labels_angle = -45

    # option to move lables for clustered stacked plots
    self.label_dist = 0

    # set the font size for the rest of things
    self.fontsize = 12
    # set the font size for the labels
    self.labels_fontsize = 12
    # Marker size
    if self.plot_type == 'scatter':
      self.markersize = 20
    else:
      self.markersize = 6

    # used to override default y range. you can provide the range in the
    # form of [min, max]
    self.yrange = None
    # Override default x range.
    self.xrange = None

    # if not None, normalize line draws a horizontal line at indicated y
    self.normalize_line = None

    self.fig = None
    # this is useful for drawing multiple plots in a page
    self.plot_idx = 1
    self.num_cols = 1
    self.num_rows = 1

    # if non-zero, shares axis with the previous plot. 1 indicates x axis
    # sharing, 2 indicates y axis sharing
    self.share_axis = 0

    # set to true if the y or x axis are log scale
    self.log_yaxis = False
    self.log_xaxis = False

    # if true, just show the plot, don't save
    self.show = True

    self.legend_enabled = True
    # the following are for fine tweaking of legend in paper mode
    self.legend_ncol = 1
    # Position of legend (x, y, width, height)
    self.legend_bbox = (0., 1.05, 1., 0.1)
    # Spacing and sizing of text/handles
    self.legend_columnspacing = None
    self.legend_handlelength = None
    self.legend_handletextpad = None

    self.figsize = (8, 6) # (width, height) in inches

    self.data = [ [1,3], [2,2], [3,1], [4,5], [1,3] ]

    # Individually label each point in scatter plot. Labels are
    # specified in self.labels[0]
    self.labels_enabled = False
    self.labels_x_off = 2
    self.labels_y_off = 2
    self.labels = None

    # Boxplot-specific options
    # Colors for parts of boxplot
    self.boxplot_color_boxes    = 'black'
    self.boxplot_color_medians  = 'black'
    self.boxplot_color_whiskers = 'black'
    self.boxplot_color_caps     = 'black'
    self.boxplot_color_fliers   = 'black'
    # Size of fliers
    self.boxplot_fliers_size = None

    # Histogram-specific options
    # Number of bins to use for histogram
    self.histogram_bins = 25

    # Scatter bar-specific options
    # if true, draws an arrow from the earlier to later
    self.scatter_bar_arrow = False
    # only draw arrow head if the length is this long
    self.scatter_bar_arrow_minlen = 0.2

    # Bar-specific options
    # Error bars, lists of 2 lists. The first contains the minimums to draw and
    # the second contains the maximums to draw.
    self.errorbars = None
    # Annotate bars that exceed max yrange
    self.overflow_labels_enabled = False

    # Heatmap-specific options
    # Colormap
    self.heatmap_cmap = None
    # Show color bar
    self.heatmap_cbar = False
    # Label for color bar
    self.heatmap_cbar_label = None
    # Fraction to shrink color bar height by
    self.heatmap_cbar_shrink = 1

    # Colors selected from colobrewer2.org for 9 categories, qualitative, print friendly
    self.colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#ffff33', '#a65628', '#f781bf', '#999999']
    self.hatch = []
    self.symbols = [ 'o', 'd', '^', 's', '*',
                     'p', '+', 'x', '8', '>',
                     '<', 'v', '2', '3', '4',
                     '1', ',', '.', 'D', 'H',
                   ]
    self.linestyles = []

    # Subplot adjust values
    self.subplots_hspace = 0
    self.subplots_wspace = 0

    # pareto-frontier points
    self.pareto_points = False
    self.pareto_data   = []

    # combined line plots
    self.combined_line_markersz = 8
    self.combined_line_plot     = []
    self.combined_line_ylabel   = ''

    random.seed( 0xdeadbeef )

  def get_color( self, idx ):
    # get a color from colors array if idx is small, otherwise, gets a
    # random color
    if idx < len( self.colors ):
      return self.colors[idx]
    else:
      return "#{:06x}".format( random.randint( 0, 0xffffff ) )
  def get_hatch( self, idx ):
    # get a hatch from hatch array if idx is small, otherwise, gets no hatch
    if idx < len( self.hatch ):
      return self.hatch[idx]
    else:
      return ''
  def get_symbol( self, idx) :
    # get a symbol from symbol array if idx is small, otherwise, default is 'o'
    if idx < len( self.symbols ):
      return self.symbols[idx]
    else:
      return 'o'
  def get_linestyle( self, idx ):
    # get a linestyle from linestyle array if idx is mall, otherwise, default is '-'
    if idx < len( self.linestyles ):
      return self.linestyles[idx]
    else:
      return '-'



def add_plot( opt ):
  """ Function to create a plot. """
  # Check for valid plot type
  if opt.plot_type not in opt.valid_plot_types:
    print "Unrecognized plot type: %s" % opt.plot_type
    sys.exit(1)

  # Set font
  plt.rcParams['font.size'] = opt.fontsize
  plt.rcParams['font.family'] = 'sans-serif'
  plt.rcParams['font.sans-serif'] = ['Arial']

  if opt.fig == None:
    opt.fig = plt.figure( figsize=opt.figsize )

  if opt.share_axis == 1:
    # Share x-axis
    ax = opt.fig.add_subplot( opt.num_rows, opt.num_cols, opt.plot_idx, \
                              sharex=opt.ax )
  elif opt.share_axis == 2:
    # Share y-axis
    ax = opt.fig.add_subplot( opt.num_rows, opt.num_cols, opt.plot_idx, \
                              sharey=opt.ax )
  else:
    ax = opt.fig.add_subplot( opt.num_rows, opt.num_cols, opt.plot_idx )

  if opt.plot_type == "line":
    add_line_plot( ax, opt )
  elif opt.plot_type == "scatter":
    add_scatter_plot( ax, opt )
  elif opt.plot_type == "histogram":
    add_histogram_plot( ax, opt )
  elif opt.plot_type == "boxplot":
    add_boxplot_plot( ax, opt )
  elif opt.plot_type == "heatmap":
    add_heatmap_plot( ax, opt )
  elif opt.plot_type == "clustered_stacked_bar":
    add_clustered_stacked_bar( ax, opt )
  else:
    add_bar_plot( ax, opt )
  opt.plot_idx += 1

  # move gridlines behind plot
  ax.set_axisbelow( True )

  opt.ax = ax

  if opt.pareto_points:
    ax.plot(opt.pareto_data[0],opt.pareto_data[1],'--',color='k',alpha=0.5)

  plt.tight_layout()

  if opt.subplots_hspace:
    plt.subplots_adjust(hspace=opt.subplots_hspace)

  if opt.subplots_wspace:
    plt.subplots_adjust(wspace=opt.subplots_wspace)

  if opt.file_name != None and opt.file_name != "":
    for file in opt.file_name.split():
      print "saving", file
      plt.savefig( file, bbox_inches="tight" )
  elif opt.show:
    plt.show()


def add_line_plot( ax, opt ):

  lines = []
  for i in xrange( len( opt.data ) ):
    c = list(opt.data[ i ])
    # x, y data
    if isinstance(c[0], list):
      line, = ( ax.plot( c[0], c[1], \
                       marker=opt.get_symbol(i), \
                       color=opt.get_color(i), \
                       linestyle=opt.get_linestyle(i), \
                       zorder=5+i,
                       markersize=opt.markersize ) )
    # y-only data
    else:
      line, = ( ax.plot( c, \
                       marker=opt.get_symbol(i), \
                       color=opt.get_color(i), \
                       linestyle=opt.get_linestyle(i), \
                       zorder=5+i,
                       markersize=opt.markersize ) )
    lines.append(line)

  if opt.yrange is not None:
    ax.set_ylim( opt.yrange )
  if opt.xrange is not None:
    ax.set_xlim( opt.xrange )

  if   opt.log_yaxis and not opt.log_xaxis:
    ax.semilogy()
  elif not opt.log_yaxis and opt.log_xaxis:
    ax.semilogx()
  elif opt.log_yaxis and opt.log_xaxis:
    ax.loglog()

  legend = []
  legend_labels = []

  # if no labels specified, create blank entries to generate legend
  if not opt.labels:
    opt.labels = [" "]*len(lines)

  # x tick labels (opt.labels[0]) and legend labels (opt.labels[1])
  if isinstance(opt.labels[0], list):
    # set the xticklabels
    ax.set_xticks( np.arange(len(opt.labels[0])) )
    if opt.rotate_labels:
      ax.set_xticklabels( opt.labels[0],
                          verticalalignment="top",
                          y=0.01,
                          horizontalalignment="left" \
                            if opt.rotate_labels_angle > 0 else "right",
                          fontsize=opt.labels_fontsize,
                          rotation=opt.rotate_labels_angle
                        )
    else:
      ax.set_xticklabels( opt.labels[0],
                          verticalalignment="top",
                          y=0.01,
                          fontsize=opt.labels_fontsize
                        )
    for i in xrange( len( lines ) ):
      if opt.labels[1][i] is not None and opt.labels[1][i] != "":
        legend.append( lines[i] )
        legend_labels.append( opt.labels[1][i] )
  else:
    for i in xrange( len( lines ) ):
      if opt.labels[i] is not None and opt.labels[i] != "":
        legend.append( lines[i] )
        legend_labels.append( opt.labels[i] )

  set_legend( ax, opt, legend, legend_labels )
  set_common( ax, opt )

  ax.xaxis.grid(True,linestyle="--")
  ax.yaxis.grid(True,linestyle="--")


def add_histogram_plot( ax, opt ):

  histograms = []
  for i in xrange( len( opt.data ) ):
    n, bins, patches = ax.hist( opt.data[i], \
                              bins=opt.histogram_bins, \
                              color=opt.get_color(i) )
    histograms.append(patches[0])

  if opt.yrange is not None:
    ax.set_ylim( opt.yrange )
  if opt.xrange is not None:
    ax.set_xlim( opt.xrange )

  set_legend( ax, opt, histograms, opt.labels )
  set_common( ax, opt )

  ax.xaxis.grid(True)
  ax.yaxis.grid(True)


def add_boxplot_plot( ax, opt ):

  bp = ax.boxplot( opt.data )

  if opt.yrange is not None:
    ax.set_ylim( opt.yrange )
  if opt.xrange is not None:
    ax.set_xlim( opt.xrange )

  # Set colors
  plt.setp( bp['boxes'], color=opt.boxplot_color_boxes )
  plt.setp( bp['medians'], color=opt.boxplot_color_medians )
  plt.setp( bp['whiskers'], color=opt.boxplot_color_whiskers )
  plt.setp( bp['caps'], color=opt.boxplot_color_caps )
  plt.setp( bp['fliers'], marker='x', color=opt.boxplot_color_fliers )
  if opt.boxplot_fliers_size:
    plt.setp( bp['fliers'], markersize=opt.boxplot_fliers_size )

  # Set x tick labels
  ax.tick_params( labelsize=opt.fontsize )
  if opt.labels:
    if opt.rotate_labels:
      ax.set_xticklabels( opt.labels, \
                          verticalalignment="top", \
                          y=0.01, \
                          horizontalalignment="left" \
                                  if opt.rotate_labels_angle > 0 \
                                  else "right", \
                          rotation=-opt.rotate_labels_angle, \
                          fontsize=opt.labels_fontsize )
    else:
      ax.set_xticklabels( opt.labels, \
                          verticalalignment="top", \
                          y=0.01, \
                          fontsize=opt.labels_fontsize )


  set_common( ax, opt )

  ax.xaxis.grid(True)
  ax.yaxis.grid(True)


def add_heatmap_plot( ax, opt ):

  # Plot
  if opt.heatmap_cmap:
    cmap = matplotlib.colors.LinearSegmentedColormap( "custom", opt.heatmap_cmap )
    hm = ax.imshow( opt.data, interpolation='nearest', cmap=cmap )
  else:
    hm = ax.imshow( opt.data, interpolation='nearest' )

  # Color bar
  if opt.heatmap_cbar:
    ax = opt.fig.add_subplot( opt.num_rows, opt.num_cols, opt.plot_idx )
    cbar = plt.colorbar( hm, use_gridspec=True, shrink=opt. heatmap_cbar_shrink )
    if opt.heatmap_cbar_label:
      cbar.set_label( opt.heatmap_cbar_label )

  # x tick labels (opt.labels[0]) and y tick labels (opt.labels[1])
  if opt.labels:
    if opt.rotate_labels:
      ax.set_xticklabels( opt.labels[0], \
                          verticalalignment="top", \
                          y=0.01, \
                          horizontalalignment="left" \
                                  if opt.rotate_labels_angle > 0 \
                                  else "right", \
                          rotation=-opt.rotate_labels_angle, \
                          fontsize=opt.labels_fontsize )
      ax.set_yticklabels( opt.labels[1], \
                          verticalalignment="top", \
                          y=0.01, \
                          horizontalalignment="left" \
                                  if opt.rotate_labels_angle > 0 \
                                  else "right", \
                          rotation=-opt.rotate_labels_angle, \
                          fontsize=opt.labels_fontsize )

    else:
      ax.set_xticklabels( opt.labels[0], \
                          verticalalignment="top", \
                          y=0.01, \
                          fontsize=opt.labels_fontsize )
      ax.set_yticklabels( opt.labels[1], \
                          verticalalignment="center", \
                          y=0.01, \
                          fontsize=opt.labels_fontsize )

  if opt.yrange is not None:
    ax.set_ylim( opt.yrange )
  if opt.xrange is not None:
    ax.set_xlim( opt.xrange )

  set_common( ax, opt )


def add_scatter_plot( ax, opt ):

  # for scatter plots, the normalize lines are a tuple for x, y
  if opt.normalize_line is not None:
    x, y = opt.normalize_line[:2]
    if x is not None:
      ax.axvline( x=x, zorder=1, color='k' )
    if y is not None:
      ax.axhline( y=y, zorder=1, color='k' )

    # more args to normalize line are arbitrary lines of format
    # (x1, y1, x2, y2)
    for line in opt.normalize_line[2:]:
      x1, y1, x2, y2 = line
      ax.plot( [x1, x2], [y1, y2], 'k-', lw=0.5, zorder=1 )

  scatters = []
  for i in xrange( len( opt.data ) ):
    c = opt.data[ i ]
    # we get x's and y's
    x, y = zip( *c )

    # zorder specifies the ordering of elements, the higher the more
    # visible
    scatters.append( ax.scatter( x, y, \
                               marker=opt.get_symbol(i), \
                               color=opt.get_color(i), \
                               zorder=5+i,
                               s=opt.markersize ) )

    # NB: REVISIT THE COMMENTED LINE BELOW
    # if opt.scatter_bar_arrow and i > 1:
    if opt.scatter_bar_arrow and i > 0:
      for j in xrange( len( x ) ):
        start = ( opt.data[i-1][j][0], opt.data[i-1][j][1] )
        diff =  ( x[j] - start[0], y[j] - start[1] )

        # temporarily disabling arrow head
        # we only draw arrow if the diff is above minlen
        #if abs( ( diff[0]**2 + diff[1]**2 )**0.5 ) \
        #                        > opt.scatter_bar_arrow_minlen:
        #  #head_width = 0.06
        #  #head_length = 0.06
        #  head_width = 0.00
        #  head_length = 0.00
        #else:
        head_width = 0.0
        head_length = 0.0

        # draw the arrow only if the difference is greater than zero
        if ( diff[0]**2 + diff[1]**2 ) > 0:
          ax.arrow( start[0], start[1], \
                    diff[0], diff[1], shape="full", length_includes_head=True, \
                    head_width=head_width, head_length=head_length, \
                    lw=0.5, overhang=0.0, zorder=2, \
                    color="#808080")

    if opt.labels_enabled: #and i > 0:
      for j in xrange( len( x ) ):
        label = opt.labels[0][i][j]
        ax.annotate( label, xy=(x[j], y[j]), \
                     xytext=( opt.labels_x_off, opt.labels_y_off ), \
                     textcoords='offset points', \
                     #arrowprops=dict(arrowstyle="->", \
                     #                connectionstyle="arc3,rad=.2")
                   )

  if opt.yrange is not None:
    ax.set_ylim( opt.yrange )
  if opt.xrange is not None:
    ax.set_xlim( opt.xrange )

  legend = []
  legend_labels = []

  # if no labels specified, create blank entries to generate legend
  if not opt.labels:
    opt.labels = [[], [" "]*len(scatters)]
  for i in xrange( len( scatters ) ):
    if opt.labels[1][i] is not None and opt.labels[1][i] != "":
      legend.append( scatters[i] )
      legend_labels.append( opt.labels[1][i] )

  set_legend( ax, opt, legend, legend_labels )
  set_common( ax, opt )

  ax.xaxis.grid(True)
  ax.yaxis.grid(True)

def add_clustered_stacked_bar( ax, opt ):

  # Determine number of subcategories based on labels
  num_cat = len( opt.labels[0] )
  num_subcat = len( opt.labels[1] )

  # number of stacks in the stacked bar plot
  num_stacks = len( opt.labels[2] )

  # base for all indices
  ind = np.arange( num_cat )
  ind = ind + (1-opt.bar_width)/2

  # width of each bar
  width = opt.bar_width / num_subcat

  indexes = []
  bar_data = []

  for s in xrange( num_subcat ):
    indexes.append( ind + s * width )
    # list of lists
    tmp_list = []
    for c in xrange( num_cat ):
      tmp_list.append( opt.data[s][c] )
    bar_data.append( np.array( tmp_list ) )

  bars = []

  bar_linewidth = 0.5
  for i in xrange( num_subcat ):
    bottom = np.array( [0.0] * num_cat )
    for j in xrange( num_cat ):
      for k in xrange( num_stacks ):
        bars.append( ax.bar( indexes[i][j], bar_data[i][j][k], width, \
                             color=opt.get_color(k), \
                             linewidth=bar_linewidth, \
                             bottom=bottom[j],
                             hatch=opt.get_hatch(k),
                             edgecolor='k'
                            ) )
        bottom[j] += bar_data[i][j][k]

  # we force that there is no empty space to the right
  ax.set_xlim( (0.0, 0.0 + num_cat ) )

  # set the xtick params based on the actual bar positions
  indexes = np.concatenate(indexes).ravel()
  ax.set_xticks( indexes )

  ax.tick_params( labelsize=opt.labels_fontsize )

  # duplicate the label for each configuration
  xlabels = []
  for label in opt.labels[1]:
    xlabels += [label] * len(opt.labels[0])

  ax.tick_params( labelsize=opt.labels_fontsize )
  if opt.labels:
    if opt.rotate_labels:
      ax.set_xticklabels( xlabels, \
                          verticalalignment="top", \
                          y=0.01, \
                          horizontalalignment="center" \
                                  if opt.rotate_labels_angle >= 0 \
                                  else "right", \
                          rotation=-opt.rotate_labels_angle, \
                          fontsize=opt.labels_fontsize )
    else:
      ax.set_xticklabels( xlabels, \
                          verticalalignment="top", \
                          y=0.01, \
                          fontsize=opt.labels_fontsize )


  # if yrange is specified, we set the value
  if opt.yrange is not None:
    ax.set_ylim( opt.yrange )

  # draw the normalization line
  if opt.normalize_line is not None:
    ax.axhline( y=opt.normalize_line, color='k' )

  # Add the legend stuff.
  if num_subcat > 1:
    legend_labels = opt.labels[2]
    # bars use the first element
    legend_bars   = map( lambda x: x[0], bars )
    set_legend( ax, opt, legend_bars, legend_labels )

  # add the group labels now
  ind = ind + (num_subcat-1)*(width/2)
  for i in range(len(opt.labels[0])):
    ax.text( ind[i], opt.label_dist, opt.labels[0][i],
             fontsize=opt.fontsize, ha="center" )

  set_common( ax, opt )
  ax.yaxis.grid(True)

def add_bar_plot( ax, opt ):

  # Determine number of categories based on labels
  num_cat = len(opt.data)
  num_subcat = len(opt.data[0])

  ind = np.arange( num_cat )
  if opt.plot_type == "stacked_bar":
    width = opt.bar_width
  else:
    width = opt.bar_width / num_subcat
  ind = ind + (1-opt.bar_width)/2

  indexes = []
  bar_data = []

  for s in xrange( num_subcat ):
    if opt.plot_type == "stacked_bar":
      # stacked use the same x values
      indexes.append( ind )
    elif opt.plot_type == "scatter_bar":
      # for scatter bar, we need to put the point right at the center
      indexes.append( ind + opt.bar_width/2. )
    else:
      indexes.append( ind + s * width )

    tmp_list = []
    for c in xrange( num_cat ):
      tmp_list.append( opt.data[c][s] )

    bar_data.append( np.array( tmp_list ) )

  bars = []

  bottom = np.array( [0.0] * num_cat )

  bar_linewidth = 0.5
  for i in xrange( num_subcat ):
    if opt.plot_type == "scatter_bar":
      # bars are actually scatters
      bars.append( ax.scatter( indexes[i], bar_data[i], \
                               marker=opt.get_symbol(i), \
                               color=opt.get_color(i), \
                               s=40, zorder=i+5 ) )
      # we draw to this if arrows are allowed and the index is larger than
      # 0
      if opt.scatter_bar_arrow and i > 0:
        for j in xrange( len( indexes[i] ) ):
          start = ( indexes[i-1][j], bar_data[i-1][j] )
          ydiff = bar_data[i][j] - bar_data[i-1][j]
          if ydiff == 0:
            continue

          # we only draw arrow if the diff is above minlen
          if abs(ydiff) > opt.scatter_bar_arrow_minlen:
            # temporarily disabled arrowhead
            #head_width = 0.3
            #head_length = 0.1
            head_width = 0.0
            head_length = 0.0
          else:
            head_width = 0.0
            head_length = 0.0

          ax.arrow( start[0], start[1], \
                    0, ydiff, shape="full", length_includes_head=True, \
                    head_width=head_width, head_length=head_length, \
                    zorder=2, \
                    color='k')

    else:
      bars.append( ax.bar( indexes[i], bar_data[i], width, \
                           color=opt.get_color(i), \
                           linewidth=bar_linewidth, \
                           bottom=bottom,
                           hatch = opt.get_hatch(i),
                           edgecolor='k'
                          ) )
      # Annotate bars that exceed max y-axis value
      if opt.overflow_labels_enabled:
        for j in range(len(indexes[i])):
          if opt.yrange and bar_data[i][j] > opt.yrange[1]:
            ax.annotate("%d" % (bar_data[i][j]), xy=(indexes[i][j], opt.yrange[1]), xytext=(-len(indexes)*5/2 + i*5 + 1, 1), textcoords='offset points')

    if opt.plot_type == "stacked_bar":
      bottom += bar_data[i]

  if opt.errorbars:
    min_errors = np.array(opt.errorbars[0]).transpose()
    max_errors = np.array(opt.errorbars[1]).transpose()
    for i in range(len(indexes)):
      # Calculate center point of error bar
      error_indexes = [x + width/2.0 for x in indexes[i]]
      # Plot error bars
      plt.errorbar(error_indexes, bar_data[i], yerr=[min_errors[i], max_errors[i]], fmt='.', markersize=0, color='k')

  # we force that there is no empty space to the right
  ax.set_xlim( (0.0, 0.0 + num_cat ) )

  # scatter bar requires x axis grids to help viewers
  if opt.plot_type == "scatter_bar":
    ax.xaxis.grid(True)

  if opt.plot_type == "stacked_bar":
    ax.set_xticks( ind )
  else:
    ax.set_xticks( ind + (num_subcat-1)*(width/2) )

  ax.tick_params( labelsize=opt.fontsize )
  if opt.labels:
    if opt.rotate_labels:
      ax.set_xticklabels( opt.labels[0], \
                          verticalalignment="top", \
                          y=0.01, \
                          horizontalalignment="left" \
                                  if opt.rotate_labels_angle > 0 \
                                  else "right", \
                          rotation=-opt.rotate_labels_angle, \
                          fontsize=opt.labels_fontsize )
    else:
      ax.set_xticklabels( opt.labels[0], \
                          verticalalignment="top", \
                          y=0.01, \
                          fontsize=opt.labels_fontsize )

  # if yrange is specified, we set the value
  if opt.yrange is not None:
    ax.set_ylim( opt.yrange )

  # draw the normalization line
  if opt.normalize_line is not None:
    ax.axhline( y=opt.normalize_line, color='k' )

  # Add the legend stuff.
  if opt.labels:
    if num_subcat > 1:
      legend_labels = opt.labels[1]
      if opt.plot_type == "scatter_bar":
        # scatters just use the scatters
        legend_bars   = bars
      else:
        # bars use the first element
        legend_bars   = map( lambda x: x[0], bars )
      set_legend( ax, opt, legend_bars, legend_labels )

  set_common( ax, opt )

  ax.yaxis.grid(True)

  # combined line plots
  if opt.combined_line_plot:
    ax_line = ax.twinx()
    ax_line.plot( ax.get_xticks(), opt.combined_line_plot,
                  marker='.',
                  markersize=opt.combined_line_markersz,
                  color='k',
                  linestyle='--' )
    ax_line.set_ylim( [0.8,1.2] )
    if opt.combined_line_ylabel:
      ax_line.set_ylabel( opt.combined_line_ylabel )

def set_legend( ax, opt, legend, legend_labels ):
  if not opt.legend_enabled:
    return

  leg = ax.legend( legend, \
                   legend_labels, loc=8, \
                   bbox_to_anchor=opt.legend_bbox, \
                   ncol=opt.legend_ncol, \
                   borderaxespad=0., \
                   prop={'size':opt.fontsize} , \
                   columnspacing=opt.legend_columnspacing, \
                   handlelength=opt.legend_handlelength, \
                   handletextpad=opt.legend_handletextpad)
  # we dissappear the box
  leg.get_frame().set_color("white")


def set_common( ax, opt ):
  # Title and Legend stuff.
  if opt.title:
    ax.set_title( opt.title, fontsize=opt.fontsize )

  # Set labels for axes
  if opt.xlabel:
    ax.set_xlabel( opt.xlabel, fontsize=opt.fontsize )
  if opt.ylabel:
    ax.set_ylabel( opt.ylabel, fontsize=opt.fontsize )
  # Set font size for axes
  ax.tick_params( labelsize=opt.fontsize )

  # turn off top and right border
  ax.spines['right'].set_visible(False)
  ax.spines['top'].set_visible(False)
  ax.xaxis.set_ticks_position('bottom')
  ax.yaxis.set_ticks_position('left')

  # when sharing axes, don't display labels
  if opt.share_axis == 1:
    plt.setp( ax.get_xticklabels(), visible=False )
  elif opt.share_axis == 2:
    plt.setp( ax.get_yticklabels(), visible=False )


