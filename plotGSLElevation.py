# -*- coding: utf-8 -*-
"""
Created on Sat Jul 24 10:21:06 2021

@author: cariefrantz

Updates the HTML page of historical lake elevation at from USGS data.
Data from 1847-2022 is from Saltair site 10010000, which went dry in 09-2022,
    then re-submerged in 12-2022
Data from 2019-     is from Lakeside causeway site 10010024

"""

####################
# IMPORTS
####################

import ResearchModules
import os
import pandas as pd
import numpy as np

# from bokeh.io import show
from bokeh.layouts import column
from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource, Div, HoverTool

from datetime import date
from pandas.tseries.offsets import DateOffset
import matplotlib.pyplot as plt


####################
# VARIABLES
####################
directory = os.getcwd()     # Directory for saving the page

# Download URLs
olddata_html = 'https://faculty.weber.edu/cariefrantz/GSL/LakeElevationSaltair.csv'
USGS_sites = {
    'Saltair'   : {
        'station_id'    : 10010000,
        'date_start'    : '2022-12-15',
        'row_head'      : 29
        },
    'Causeway'  : {
        'station_id'    : 10010024,
        'date_start'    : '2019-10-03',
        'row_head'      : 28
        }
    }

# Data parsing
datefmt = '%Y-%m-%d'
col_date = '20d'            # Header row value for the date column in dataset
col_elev = '14n'            # Header row value for the elevation colum
col_dtype = '10s'           # Header row value for the data type/status

# Data analysis
rec_first = '1847-10-18'    # Date of first measurement in the historic dataset
pi_start = '1850'           # Designate start of 'pre-industrial' period
pi_end = '1900'             # Designate end of 'pre-industrial' period
hist_start = '1900'         # Designate start of 'historical' period
hist_end = '2000'           # Designate end of 'historical' period
hist_range = hist_start + '-' + hist_end
cw_first = '2019-10-03'     # Date of first measurement at Causeway site

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
<h1>Great Salt Lake South Arm Elevation</h1>
<p>Daily mean lake water surface elevation above ngvd 1929 from the USGS
National Water Information System / USGS Utah Water Science Center
<br /><b>Saltair:</b> Elevation measured at Saltair Boat Harbor, 
<a href="https://waterdata.usgs.gov/monitoring-location/10010000/">
Station 10010000</a>
<br /><b>Causeway:</b> Elevation measured near Lakeside on the south side of the Union
Pacific Rail Causeway, 
<a href="https://waterdata.usgs.gov/monitoring-location/10010024/">
Station 10010024</a></p>
<p>Plot by Dr. Carie Frantz,
<a href="https://www.weber.edu/ees">Department of Earth and Environmental 
Sciences</a>, Weber State University, using Python script
<a href="https://github.com/cmfrantz/GSL">plotGSLElevation.py</a></p>
<p>Definitions: Pre-industrial is defined as '''
 + pi_start + '–' + pi_end + '.'
 + ' Historical is defined as '
 + hist_start + '–' + hist_end + '.</p>'
 #+ '''
 #<p>Data type key (display using the Hover tool):
 #<ul>
 #<li>A &emsp; Approved for publication — Processing and review completed.
 #</li>
 #<li>P &emsp; Provisional data subject to revision.</li>
 #<li>e &emsp; Value has been estimated.</li>
 #<li>Eqp &emsp; Value affected by equipment malfunction.</li>
 #</ul>
 #</p>
#'''
)
HTML_newmin_head = '<h2>New minimum: '
HTML_newmin_mid = ' ft reached on '
HTML_newmin_end = '''
    </h2>
    <h3>As of 9/29/2022, lake levels dropped below where the Saltair station
could measure.</h3>
    <p><b>Use the toolbars to the right of the plot to scroll/zoom and display
    daily mean values.</b></p>
    <p>Plot last updated 
    '''
    
    
    
####################
# FUNCTIONS
####################    

def prepElevationData(elev_data):
    
    # Convert elevation data to numeric
    elev_data[col_elev] = pd.to_numeric(elev_data[col_elev], errors='coerce')
    
    # Resample to daily
    elev_data_daily = elev_data.resample('D').mean()
    elev_data_daily[col_date] = [str(dt)[:10] for dt in elev_data_daily.index.values]
    
    # Interpolate & calculate time-weighted average
    interp = elev_data_daily.interpolate()
    interp = interp.resample('W').mean()
    interp.index = interp.index + DateOffset(days=-3)
    
    # Prep the data
    source = ColumnDataSource(data={
        'dt'      : elev_data_daily.index,
        'date'    : elev_data_daily[col_date],
        'elev'    : elev_data_daily[col_elev],
        #'dtype'   : elev_data[col_dtype]
        })
    
    return elev_data_daily, interp, source
    
#%%

####################
# CODE
####################

# Download the historical elevation data at Saltair
print('\nDownloading historical lake elevation data...')
elev_data_Saltair = pd.read_csv(olddata_html, sep = ',', header = 0)
elev_data_Saltair['date'] = pd.to_datetime(elev_data_Saltair['20d'])
elev_data_Saltair['20d'] = elev_data_Saltair['date'].dt.strftime('%Y-%m-%d')
elev_data_Saltair.set_index('date', drop=True, inplace=True)

# Download and add the recent elevation data from the Saltair station
print('\nDownloading Saltair elevation data...')
elev_data_Saltair2 = ResearchModules.download_lake_elevation_data(
    USGS_sites['Saltair']['date_start'], date.today().strftime(datefmt),
    USGS_sites['Saltair']['station_id'], USGS_sites['Saltair']['row_head'])

# Download the elevation data for the new Lakeside station
print('\nDownloading Causeway elevation data...')
elev_data_Causeway = ResearchModules.download_lake_elevation_data(
    USGS_sites['Causeway']['date_start'], date.today().strftime(datefmt),
    USGS_sites['Causeway']['station_id'], USGS_sites['Causeway']['row_head'])

#%%

print('\nParsing data...')

# Saltair data
daily_elev_data_Saltair, Saltair_interp, Saltair_source = prepElevationData(
    elev_data_Saltair)
# Pre-industrial
pi_mean = Saltair_interp[col_elev][pi_start : pi_end].mean()
# Historical
hist_mean = Saltair_interp[col_elev][hist_start : hist_end].mean()

# Modern (Causeway) data
daily_elev_data_Causeway, Causeway_interp, Causeway_source = prepElevationData(
    elev_data_Causeway)

# Calculate historical min/max
hist_min = elev_data_Saltair[hist_start : hist_end][col_elev].min(skipna=True)
hist_max = elev_data_Saltair[hist_start : hist_end][col_elev].max(skipna=True)

# Find min & date
elev_min_Saltair = np.nanmin(daily_elev_data_Saltair[col_elev])
elev_min_Causeway = np.nanmin(daily_elev_data_Causeway[col_elev])
elev_min = min(elev_min_Saltair, elev_min_Causeway)
if elev_min_Causeway < elev_min_Saltair:
    elev_min_date = daily_elev_data_Causeway[
        daily_elev_data_Causeway[col_elev]==elev_min][col_date][0]
else:
    elev_min_date = Saltair_interp[
        Saltair_interp[col_elev]==elev_min][col_date][0]
elev_min = round(elev_min,1)

# Update HTML header
HTML_head = (HTML_head + HTML_newmin_head + str(elev_min) + HTML_newmin_mid
             + elev_min_date + HTML_newmin_end)

# Build the bokeh figure
print('\nBuilding the figure...')
fig = figure(height = plt_ht*100, width = plt_w*100,
             tools = toolset,
             x_axis_type = 'datetime',
             active_drag = active_drag, active_scroll=active_scroll,
             active_tap = active_tap,
             title = 'Great Salt Lake elevation measured at Saltair')
fig.xaxis.axis_label = 'Date'
fig.yaxis.axis_label = 'Lake elevation (ft)'

# Add the historical min, average, max lines
fig.line(
    [elev_data_Saltair.index.min(), elev_data_Causeway.index.max()],
    [pi_mean, pi_mean], color='lightgrey', line_width=linew, alpha=alpha,
    legend_label = str(round(pi_mean,1)) + ' ft (pre-industrial mean)')
fig.line(
    [elev_data_Saltair.index.min(), elev_data_Causeway.index.max()],
    [hist_mean, hist_mean], color='grey', line_width=linew, alpha=alpha,
    legend_label = str(round(hist_mean,1)) + ' ft (historical mean)')
fig.line(
    [elev_data_Saltair.index.min(), elev_data_Causeway.index.max()],
    [hist_max, hist_max], color='steelblue', line_width=linew, alpha=alpha,
    legend_label = str(round(hist_max,1)) + ' ft (historical maximum)')
fig.line(
    [elev_data_Saltair.index.min(), elev_data_Causeway.index.max()],
    [hist_min, hist_min], color='crimson', line_width=linew, alpha=alpha,
    legend_label = str(round(hist_min,1)) + ' ft (historical minimum)')

# Add the station measurements
meas = fig.circle(
    x='dt', y='elev', source=Saltair_source, size=mkrsize,
    color='lightblue', legend_label = 'Station measurements: Saltair'
    )
meas = fig.circle(
    x='dt', y='elev', source=Causeway_source, size=mkrsize,
    color='thistle', legend_label = 'Station measurements: Causeway'
    )

# Add the interpolated weekly mean
fig.line(
    Saltair_interp.index, Saltair_interp[col_elev].values, color='darkblue',
    alpha=alpha, legend_label='Interpolated weekly mean: Saltair')
fig.line(
    Causeway_interp.index, Causeway_interp[col_elev].values, color='indigo',
    alpha=alpha, legend_label='Interpolated weekly mean: Causeway')

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

#%%

# Save editable figures

# Plot parameters
convert_to_m = False
figsize = [8,4]
date_start = date(2018,1,1)
date_end = date(2023,8,30)
plot_points = False
svd = col_elev
ylim = [4188,4196]

if convert_to_m:
    # Convert ft to m
    for dset in [elev_data_Causeway, elev_data_Saltair, Causeway_interp,
                 Saltair_interp]:
        dset['m']=ResearchModules.ft_to_m(dset[col_elev])
    # Use meters
    col_elev='m'

# Build plots
fig = plt.figure(figsize=figsize)

if plot_points:
    plt.scatter(elev_data_Saltair.index, elev_data_Saltair[col_elev],
                c='lightgray', s=mkrsize)
    plt.scatter(elev_data_Causeway.index, elev_data_Causeway[col_elev],
                c='gray', s=mkrsize)

plt.plot(
    Saltair_interp.index, Saltair_interp[col_elev].values, c='midnightblue')
plt.plot(
    Causeway_interp.index, Causeway_interp[col_elev].values, c='skyblue')

col_elev = svd

# Add horizontal marker lines
hlines = [4195.5, 4193, 4191.5]
#for l in hlines:
#    if convert_to_m:
#        l = ResearchModules.ft_to_m(l)
#    plt.plot([date_start, date_end],[l, l])

plt.xlim(date_start, date_end)
plt.ylim(ylim)
plt.xlabel('Year')
if convert_to_m:
    plt.ylabel('Elevation (m)')
else:
    plt.ylabel('Elevation (ft)')
plt.rcParams['svg.fonttype'] = 'none'
fig.savefig('GSL_Elevation.svg', format='svg')
fig.savefig('GSL_Elevation.png', format='png')

