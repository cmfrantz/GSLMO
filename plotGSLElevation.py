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
directory = os.getcwd()

plt_ht = 5
plt_w = 10
toolset = 'xwheel_zoom, pan, box_zoom, reset, save'

HTML_head = '''
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
'''
HTML_newmin_head = '<h2>New minimum: '
HTML_newmin_mid = ' ft, reached on '
HTML_newmin_end = '''
</h2>
<p>Data type key:
<ul>
<li>A &emsp; Approved for publication -- Processing and review completed.
</li>
<li>P &emsp; Provisional data subject to revision.</li>
<li>e &emsp; Value has been estimated.</li>
</ul>
</p>
<p><b>Use the toolbars to the right of the plot to scroll/zoom and view
daily mean values.</b></p>
<p>Plot last updated 
'''
#%%

####################
# CODE
####################

print('\nBuilding historical lake elevation plot...')

# Load the elevation data for the entire record
elev_data = ResearchModules.download_lake_elevation_data(
    '1847-10-18', date.today().strftime('%Y-%m-%d'))
source = ColumnDataSource(data={
    'dt'    : elev_data.index,
    'date'  : elev_data['20d'],
    'elev'  : elev_data['14n'],
    'dtype'    : elev_data['10s']
    })

# Calculate historical min/max
hist_min = elev_data['1900':'2000']['14n'].min(skipna=True)
hist_max = elev_data['1900':'2000']['14n'].max(skipna=True)

# Find min & date
elev_min = elev_data['14n'].min(skipna=True)
elev_min_date = elev_data[elev_data['14n']==elev_min]['20d'][0]

# Update HTML header
HTML_head = (HTML_head + HTML_newmin_head + str(elev_min) + HTML_newmin_mid
             + elev_min_date + HTML_newmin_end)

# Interpolate & calculate time-weighted average
interp = elev_data['14n'].resample('D').mean().interpolate()
hist_mean = interp['1900':'2000'].mean()
interp = interp.resample('W').mean()
interp.index = interp.index + DateOffset(days=-3)

# Build the bokeh figure
fig = figure(plot_height = plt_ht*100, plot_width = plt_w*100,
             tools = toolset, x_axis_type = 'datetime',
             title = 'Great Salt Lake elevation measured at Saltair')
fig.xaxis.axis_label = 'Date'
fig.yaxis.axis_label = 'Lake elevation (ft)'

# Add the station measurements
meas = fig.circle(
    x='dt', y='elev', source=source, size=2, color='lightgray',
    legend_label = 'station measurements'
    )
fig.add_tools(HoverTool(
    tooltips=[
        ('date',        '@date'         ),
        ('elevation',   '@elev{0.0}'    ),
        ('data type', '@dtype'       )
        ],
    mode='vline', renderers = [meas]
    ))

# Add the historical min, average, max lines
fig.line(
    interp.index, interp.values, color='midnightblue', alpha=0.5,
    legend_label='interpolated weekly mean')
fig.line(
    [elev_data.index.min(), elev_data.index.max()], [hist_max, hist_max],
    color='steelblue', legend_label='1900-2000 maximum')
fig.line(
    [elev_data.index.min(), elev_data.index.max()], [hist_mean, hist_mean],
    color='grey', legend_label='1900-2000 mean')
fig.line(
    [elev_data.index.min(), elev_data.index.max()], [hist_min, hist_min],
    color='crimson', legend_label='1900-2000 minimum')
#show(fig)

# Save HTML page
GSL_elev_head = HTML_head + date.today().strftime('%Y-%m-%d') + '</p>'
output_file(directory + '\\GSL_elevation.html')
save(column([Div(text = GSL_elev_head),fig]))