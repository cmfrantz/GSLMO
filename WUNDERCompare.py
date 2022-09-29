# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 10:57:22 2021

@author: cariefrantz
"""

import ResearchModules
import os
import pandas as pd
import numpy as np
from bokeh.io import show
from bokeh.layouts import column
from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource, Div
from bokeh.palettes import viridis


# Plot formatting
color_list = ['#492365', '#575047', '#aa989c', '#a391b1']
bokeh_head = ResearchModules.GSLMO_html_head + '''
<p><a href="https://faculty.weber.edu/cariefrantz/GSL/GSLMO_plots_bokeh.html">
Link to main GSLMO page</a></p>
<h2>Weather Station Data Comparison</h2>
<p>This tool compares Weather Underground weather station data from personal
weather stations closest to northern Antelope Island, including KUTSYRAC22,
the weather station located on Antelope Island State Park.</p>
<p>Data were downloaded from Weather Underground using the script 
<a href="https://github.com/cmfrantz/GSL/blob/master/WUNDERScrape.py">
WUNDERScrape.py</a>. Plots were built using the script
<a href="https://github.com/cmfrantz/GSL/blob/master/WUNDERCompare.py">
WUNDERCompare.py</a>.</p>
<p><em>Stations: </em> |
'''
station_html = ''

# Unit conversion functions
def f_to_c(temperature_in_F):
    ''' Convert temperature in Farenheit to Celsius '''
    return round((temperature_in_F-32) * 5/9,1)

def mph_to_mps(mph):
    ''' Convert velocity in miles per hour to meters per second '''
    return round(mph*1609.34/60,1)

def in_to_mm(inches):
    ''' Convert inches to mm '''
    return round(inches * 25.4, 0)
    

# Measurement map
measlist = {
    'Temperature'   : {
        'convert'   : f_to_c,
        'title'     : 'Temperature',
        'unit'      : 'C'
        },
    'Humidity'      : {
        'convert'   : False,
        'title'     : 'Humidity',
        'unit'      : '%'
        },
    'Speed'         : {
        'convert'   : mph_to_mps,
        'title'     : 'Wind Speed',
        'unit'      : 'mps'
        },
    'Gust'          : {
        'convert'   : mph_to_mps,
        'title'     : 'Wind Gust',
        'unit'      : 'mps'
        },
    'Pressure'      : {
        'convert'   : in_to_mm,
        'title'     : 'Pressure',
        'unit'      : 'mm'
        },
    'Precip. Rate.' : {
        'convert'   : in_to_mm,
        'title'     : 'Precip. Rate',
        'unit'      : 'mm'
        },
    'Precip. Accum.': {
        'convert'   : in_to_mm,
        'title'     : 'Precip. Accum.',
        'unit'      : 'mm'
        },
    'UV'            : {
        'convert'   : False,
        'title'     : 'UV',
        'unit'      : 'W/m^2'
        },
    'Solar'         : {
        'convert'   : False,
        'title'     : 'Solar Irradiation',
        'unit'      : 'W/m^2'
        }
    }


#%%
        
# MAIN
if __name__ == '__main__': 

    # Load in weather data from the stations, saving the station value
    filelist, dirpath = ResearchModules.getFiles(
        'Select all downloaded Weather Underground weather station files')
    
    stationdata={}
    # Load in data for each file
    for file in filelist:
        # Load the file
        station_name=os.path.splitext(file.rsplit('wu_')[1])[0]
        print('Loading Station ' + station_name + ' data file...')
        data = pd.read_csv(file, sep = ',', header = 0)
        # Determine which measurements are present
        columns = list(data.columns)
        colmap = {}
        for meas in measlist:
            col = [idx for idx, s in enumerate(columns) if meas in s]
            colmap[columns[col[0]]] = meas
        data.rename(columns = colmap, inplace=True)
        # Convert measurement units
        data_converted=pd.DataFrame()
        for measurement in measlist:
            converted = pd.to_numeric(data[measurement], errors='coerce')
            if measlist[measurement]['convert'] != False:
                converted = measlist[measurement]['convert'](converted)
            data_converted[measurement] = converted
        # Convert time
        data_converted['Time'] = pd.to_datetime(data['Time'], format='%Y-%m-%d %I:%M %p')
        # Save data
        stationdata[station_name] = data_converted    
        # Update the station html
        station_html = (
            station_html + ' | '
            + '<a href="https://www.wunderground.com/dashboard/pws/'
            + station_name + '">' + station_name + '</a>')
    
    
    # Create plots of each parameter
    
    # Set up the bokeh page
    figures = []
    toolset = 'xwheel_zoom, pan, box_zoom, reset, save'
    colors = viridis(len(stationdata))
    
    for measurement in measlist:
            
        # Build the bokeh figure for each measurement
        print('Building ' + measurement + ' plot...')
            
        # Create the figure
        fig = figure(plot_height = 500, plot_width = 1000, tools = toolset,
                     x_axis_type = 'datetime',
                     title = measlist[measurement]['title'])
        
        # Gather and plot the raw data for each series
        for i,station in enumerate(stationdata):
            # Get the data for the station
            sdata = stationdata[station][['Time',measurement]].copy()
            sdata.set_index('Time', inplace=True)
            sdata = sdata[~sdata.index.duplicated()]
            # Generate smoothed hourly data
            sdata = sdata.resample('1T').interpolate(
                'index', limit = 20, limit_area = 'inside').resample(
                    'h').asfreq().dropna()
            # Find daily min/max values
            daily_mm = sdata.resample('D')[measurement].agg(['min','max'])        
            
            # Format the data for bokeh glyph render (new)
            groups = ResearchModules.nansplit(daily_mm)
            for group in groups:
                # Format x,y coordinates for each patch
                x = np.hstack((group.index, np.flip(group.index)))
                y = np.hstack((group['min'], np.flip(group['max'])))
                datasource = ColumnDataSource(dict(x=x, y=y))
                # Add patch
                fig.patch('x', 'y', color = colors[i],
                          alpha = 0.6, source = datasource,
                          legend_label = station)
            
        # Label axes and title
        fig.xaxis.axis_label = 'Date'
        fig.yaxis.axis_label = (
            measlist[measurement]['title']
            + ' (' + measlist[measurement]['unit'] + ')')
        
        # Configure legend
        fig.legend.location = 'top_left'
        fig.legend.click_policy = 'hide'
        
        # Link figure axes
        if figures:
            fig.x_range = figures[0].x_range
        
        # Add the figure to the figure list
        figures.append(fig)
    
    # Save HTML page
    print('Saving plots...')
    figures.insert(0, Div(text = bokeh_head + station_html + '</p>'))
    # show(column(figures))
    output_file(dirpath + '\\WUNDERplots.html')
    save(column(figures))
    print('Done! The plot is at ' + dirpath + '\\WUNDERplots.html')
