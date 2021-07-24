# -*- coding: utf-8 -*-
"""
Created on Sat Jul 24 10:21:06 2021

@author: cariefrantz

Updates the HTML page of historical lake elevation at Saltair from USGS data

"""

####################
# IMPORTS
####################

import ResearchModules
import os

# from bokeh.io import show
from bokeh.layouts import column
from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource, Div, HoverTool

from datetime import date
from pandas.tseries.offsets import DateOffset


####################
# VARIABLES
####################
directory = os.getcwd()     # Directory for saving the page

# Data parsing
datefmt = '%Y-%m-%d'
col_date = '20d'            # Header row value for the date column in dataset
col_elev = '14n'            # Header row value for the elevation colum
col_dtype = '10s'           # Header row value for the data type/status

# Data analysis
rec_first = '1847-10-18'   # Date of first measurement in the dataset
pi_start = '1850'           # Designate start of 'pre-industrial' period
pi_end = '1900'             # Designate end of 'pre-industrial' period
hist_start = '1900'         # Designate start of 'historical' period
hist_end = '2000'           # Designate end of 'historical' period
hist_range = hist_start + '-' + hist_end

# Plot formatting
plt_ht = 5
plt_w = 10
mkrsize = 5
linew = 4
alpha = 0.5
toolset = 'box_zoom, xwheel_zoom, pan, reset, save'
active_drag = 'box_zoom'
active_inspect = 'auto'
active_scroll = 'xwheel_zoom'
active_tap = 'auto'

# HTML page formatting
HTML_head = ('''
<h1>Great Salt Lake Elevation at Saltair (South Arm)</h1>
<p>Daily mean lake water surface elevation above ngvd 1929 measured at
Saltair Boat Harbor (South Arm)</p>
<p>Data from the USGS National Water Information System / 
USGS Utah Water Science Center,
<a href="https://waterdata.usgs.gov/nwis/inventory?agency_code=USGS&
site_no=10010000">Site 10010000</a>
<br />Plot by Dr. Carie Frantz,
<a href="https://www.weber.edu/ees">Department of Earth and Environmental 
Sciences</a>, Weber State University, using Python script
<a href="https://github.com/cmfrantz/GSL">plotGSLElevation.py</a></p>
</h2>
<p>Definitions: Pre-industrial is defined as '''
 + pi_start + '–' + pi_end + '.'
 + ' Historical is defined as '
 + hist_start + '–' + hist_end + '.'
 + '''
 <p>Data type key (display using the Hover tool):
 <ul>
 <li>A &emsp; Approved for publication — Processing and review completed.
 </li>
 <li>P &emsp; Provisional data subject to revision.</li>
 <li>e &emsp; Value has been estimated.</li>
 </ul>
 </p>
''')
HTML_newmin_head = '<h2>New minimum: '
HTML_newmin_mid = ' ft reached on '
HTML_newmin_end = '''
    </h2>
    <p><b>Use the toolbars to the right of the plot to scroll/zoom and display
    daily mean values.</b></p>
    <p>Plot last updated 
    '''
#%%

####################
# CODE
####################

print('\nBuilding historical lake elevation plot...')

# Download the elevation data for the entire record
elev_data = ResearchModules.download_lake_elevation_data(
    rec_first, date.today().strftime(datefmt))

#%%

# Calculate historical min/max
hist_min = elev_data[hist_start : hist_end][col_elev].min(skipna=True)
hist_max = elev_data[hist_start : hist_end][col_elev].max(skipna=True)

# Find min & date
elev_min = elev_data[col_elev].min(skipna=True)
elev_min_date = elev_data[elev_data[col_elev]==elev_min][col_date][0]

# Update HTML header
HTML_head = (HTML_head + HTML_newmin_head + str(elev_min) + HTML_newmin_mid
             + elev_min_date + HTML_newmin_end)

# Interpolate & calculate time-weighted average
interp = elev_data[col_elev].resample('D').mean().interpolate()
interp = interp.resample('W').mean()
interp.index = interp.index + DateOffset(days=-3)
# Pre-industrial
pi_mean = interp[pi_start : pi_end].mean()
# Historical
hist_mean = interp[hist_start : hist_end].mean()

# Prep the data
source = ColumnDataSource(data={
    'dt'      : elev_data.index,
    'date'    : elev_data[col_date],
    'elev'    : elev_data[col_elev],
    'dtype'   : elev_data[col_dtype]
    })

# Build the bokeh figure
fig = figure(plot_height = plt_ht*100, plot_width = plt_w*100,
             tools = toolset,
             x_axis_type = 'datetime',
             active_drag = active_drag, active_scroll=active_scroll,
             active_tap = active_tap,
             title = 'Great Salt Lake elevation measured at Saltair')
fig.xaxis.axis_label = 'Date'
fig.yaxis.axis_label = 'Lake elevation (ft)'

# Add the historical min, average, max lines
fig.line(
    [elev_data.index.min(), elev_data.index.max()], [pi_mean, pi_mean],
    color='lightgrey', line_width=linew, alpha=alpha,
    legend_label = str(round(pi_mean,1)) + ' ft (pre-industrial mean)')
fig.line(
    [elev_data.index.min(), elev_data.index.max()], [hist_mean, hist_mean],
    color='grey', line_width=linew, alpha=alpha,
    legend_label = str(round(hist_mean,1)) + ' ft (historical mean)')
fig.line(
    [elev_data.index.min(), elev_data.index.max()], [hist_max, hist_max],
    color='steelblue', line_width=linew, alpha=alpha,
    legend_label = str(round(hist_max,1)) + ' ft (historical maximum)')
fig.line(
    [elev_data.index.min(), elev_data.index.max()], [hist_min, hist_min],
    color='crimson', line_width=linew, alpha=alpha,
    legend_label = str(round(hist_min,1)) + ' ft (historical minimum)')

# Add the station measurements
meas = fig.circle(
    x='dt', y='elev', source=source, size=mkrsize, color='lightgray',
    legend_label = 'station measurements'
    )

# Add the interpolated weekly mean
fig.line(
    interp.index, interp.values, color='midnightblue', alpha=alpha,
    legend_label='interpolated weekly mean')

# Configure the toolbar
hover = HoverTool(
    tooltips=[
        ('date',        '@date'         ),
        ('elevation',   '@elev{0.0}'    ),
        ('data type',    '@dtype'       )
        ],
    mode='vline', renderers = [meas]
    )

fig.add_tools(hover)
fig.toolbar.active_inspect = None

#show(fig)

# Save HTML page
GSL_elev_head = HTML_head + date.today().strftime(datefmt) + '</p>'
output_file(directory + '\\GSL_elevation.html')
save(column([Div(text = GSL_elev_head),fig]))