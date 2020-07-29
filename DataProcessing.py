#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Carie Frantz'
__email__ = 'cariefrantz@weber.edu'
"""Title
Created on Mon Jun 29 15:45:09 2020
@author: cariefrantz
@project: GSLMO

Determines relative influence of density assumptions on calculated lake depth
from HOBO logger water pressure data and weather station air pressure data.

This script was created as part of the
Great Salt Lake Microbialite Observatory project

Arguments:  None

Requirements:
    HOBO_SiteA.csv
    HOBO_SiteB.csv

Example in command line:
    python DataProcessing.py

Dependencies Install:
    sudo apt-get install python3-pip python3-dev
    pip install os
    pip install pandas
    pip install numpy
    pip install matplotlib
    pip install bokeh

You will also need to have the following files
    in the same directory as this script.
They contain modules and variables that this script calls.
    ResearchModules.py
If you get an error indicating that one of these modules is not found,
    change the working directory to the directory containing these files.


Copyright (C) 2020  Carie M. Frantz

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>
"""
####################
# TO DO
####################
'''
AUTOMATE PROCESSING SEQUENCE:
    1. Load in logger data
    2. For pendants, run weather station combiner script
    3. Quality control: remove start and end where logger is out of water based on "jumps"
    4. Match button data to combined pendant data by matching closest time
    5. Add combined data to existing dataset
    6. Grab Saltair elevation data from last point with 'A' to present
        https://waterdata.usgs.gov/ut/nwis/dv/?site_no=10010000&agency_cd=USGS&amp;referred_module=sw
        https://waterdata.usgs.gov/ut/nwis/dv?cb_62614=on&format=rdb&site_no=10010000&referred_module=sw&period=&begin_date=2019-11-07&end_date=2020-07-14
    7. Re-build plots
    8. Enter field data
    9. Enter core data
    
LOAD FIELD NOTES AND ADD FIELD-BASED DATA PLOTS
# Get file and data
filename, directory, data = ResearchModules.fileGet(
    'Select field notes file', tabletype = 'field')
'''

####################
# IMPORTS
####################
import ResearchModules

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from bokeh.io import show
from bokeh.layouts import column
from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource, Div

####################
# VARIABLES
####################

# Colors
''' Unused colors
'#565D47' # dark green
'#B49C73' # beige
'#62760C' # green
'#523906' # dark brown
'#888888' # gray
'''
clr_WildcatPurple = '#492365'
clr_UniversityGray = '#575047'
clr_Pantone436 = '#aa989c'
clr_Pantone666 = '#a391b1'

# Plot and dataset info
locations = {
    'Site A'    : {
        'water_density' : 1.07,
        #'color'         : 
        #'color'         : 
        'color'         :  clr_WildcatPurple
        },
    'Site B'    : {
        'water_density' : 1.09,
        #'color'         : 
        #'color'         : 
        'color'         :  clr_UniversityGray
        }
    }

plotlist = {
    'depth'         : {
        'y_axis'        : 'Water depth (m)',
        'range'         : 'Auto',
        
        1   : {
            'location'   : 'Site A',
            'filetype'  : 'HOBO',
            'column'    : 'calc_water_depth_m',
            'title'     : 'Site A (calculated)',
            'color'     : locations['Site A']['color']
            },
        2   : {
            'location'   : 'Site B',
            'filetype'  : 'HOBO',
            'column'    : 'calc_water_depth_m',
            'title'     : 'Site B (calculated)',
            'color'     : locations['Site B']['color']
            },
        },
    
    'temperature'   : {
        'y_axis'        : 'Temperature (\degC)',
        'range'         : (-5,35),
        
        1   : {
            'location'   : 'Site A',
            'filetype'  : 'HOBO',
            'column'    : 'ws_air_temp_C',
            'title'     : 'Antelope Island weater station air temp',
            'color'     : clr_Pantone436
            },
        2   : {
            'location'   : 'Site A',
            'filetype'  : 'HOBO',
            'column'    : 'pndt_water_temp_C',
            'title'     : 'Site A water temp - Pendant',
            'color'     : locations['Site A']['color']
            },
        3   : {
            'location'   : 'Site B',
            'filetype'  : 'HOBO',
            'column'    : 'pndt_water_temp_C',
            'title'     : 'Site B water temp - Pendant',
            'color'     : locations['Site B']['color']
            }
        },
    
    'light'         : {
        'y_axis'        : 'Irradiance (lumen/ft2)',
        'range'         : (0, 7000),
        
        1   : {
            'location'   : 'Site A',
            'filetype'  : 'HOBO',
            'column'    : 'bttn_top_light_lumen_ft2',
            'title'     : 'Site A shuttle top',
            'color'     : locations['Site A']['color']
            },
        2   : {
            'location'   : 'Site B',
            'filetype'  : 'HOBO',
            'column'    : 'bttn_top_light_lumen_ft2',
            'title'     : 'Site B shuttle top',
            'color'     : locations['Site B']['color']
            }
        }
    }

# Types of input files and available variables
filetypes = {
    'HOBO'      : {
        'pressure'      : {
            'pndt_water_pressure_kPa'   : 
                'Water pressure (HOBO pendant, kPa)',
            'ws_air_pressure_kPa'       : 
                'Air pressure (weather station, kPa)',
            'dPressure_kPa'             : 
                '\Deltapressure (water - air; kPa)',
            },
        'temperature'   : {
            'ws_air_temp_C'             : 
                'Air temperature (weather station, \degC)',
            'pndt_water_temp_C'         : 
                'Water temperature (HOBO pendant, \degC)',
            'bttn_side_temp_C'          : 
                'Water temperature (HOBO button side, \degC)',
            'bttn_top_temp_C'           : 
                'Water temperature (HOBO button top, \degC)',
            },
        'light'         : {
            'bttn_top_light_lumen_ft2'  : 
                'Irradiance (HOBO button top, lumen/ft2)',
            'bttn_side_light_lumen_ft2' : 
                'Irradiance (HOBO button side, lumen/ft2)',
            },
        'salinity'      : {
            'field_salinity_pct'        : 
                'Water salinity (%)',
            },
        'density'       : {
            'field_density_spgr'        : 
                'Water density (sp. gr.)',
            },
        'depth'         : {
            'field_water_depth_m'       : 
                'Water depth (field; m)',
            'calc_water_depth_m'        :
                'Water depth (calculated; m)'
            }
        }
    }
        
plt_ht = 5
plt_w = 10
plt_pfx = 'GSL_plots_'
toolset = 'xwheel_zoom, pan, box_zoom, reset, save'

td_style = ' style = "padding: 5px"'
bokeh_head = '''
<h1>Great Salt Lake Microbialite Observatory</h1>
<h2>Weber State University College of Science</h2>

<p>Lead investigator: Dr. Carie Frantz, Department of Earth and Environmental 
Sciences, <a href="mailto:cariefrantz@weber.edu">cariefrantz@weber.edu</a></p>
<p>This project is funded by the National Science Foundation,
<a href="https://www.nsf.gov/awardsearch/showAward?AWD_ID=1801760">
Award #1801760</a></p>

<h2>Instrument Sites</h2>
<p>Both GSLMO instrument sites are located on the Northern shore of Antelope
   Island and are accessed and operated under permits from Antelope Island
   State Park and the State of Utah Division of Forestry, Fire, & State Lands.
   </p>
<table border = "1px" style = "border-collapse: collapse">
<tr style = "background-color: ''' + clr_Pantone666 + ''';
 color : white">
    <th''' + td_style + '''>Site</th>
    <th''' + td_style + '''>Description</th>
    <th''' + td_style + '''>Location</th></tr>
<tr>
    <td''' + td_style + '''>Site A</td>
    <td''' + td_style + '''>Muddy auto causeway site near Farmington Bay
    outlet with high total inorganic carbon.</td>
    <td''' + td_style + '''>41.06646, -112.23129
        <a href="https://goo.gl/maps/66u5BPLuk1ykDvCP8">(map)</a></td>
</tr>
<tr><td''' + td_style + '''>Site B</td>
    <td''' + td_style + '''>Microbialite reef site near Buffalo Point</td>
    <td''' + td_style + '''>41.03811, -112.27889
        <a href="https://goo.gl/maps/AsG9b5yYLwbXYKtA9">(map)</a></td>
</tr>
</table>

<h2>Data Logger Plots</h2>
<p>Plots display the daily minimum and maximum of hourly averages of 
   recorded data. 
   Use the tools in the toolbar to the right of each plot to explore the data.
   Click legend items to turn plotted data on and off.</p>
'''

####################
# FUNCTIONS
####################

def loadHOBOFiles():
    '''Loads in the HOBO logger datasets'''
    directory = os.getcwd()
    for location in locations:
        # Get file and data
        filename, directory, data = ResearchModules.fileGet(
            'Select ' + location + ' combined HOBO file', tabletype = 'HOBO',
            directory = directory)
        # Drop na rows (rows with no values)
        data = data.loc[data.index.dropna()]
        # Convert datetime strings to datetime objects
        data['datetime'] = pd.to_datetime(data.index)
        time_min = str(min(data['datetime']).date())
        time_max = str(max(data['datetime']).date())
        
        # Do depth calculations
        water_density = locations[location]['water_density']
        data['calc_water_depth_m'] = calc_depth(data, water_density)
        
        # Save
        locations[location]['HOBO'] = data
        
    return directory, time_min, time_max


def calc_depth(hobo_location, water_density):
    '''Calculate water depth from pressure data and assumed density'''
    gravity_factor = 9.80665
    depth = ((hobo_location['pndt_water_pressure_kPa']
              - hobo_location['ws_air_pressure_kPa'])
             * water_density / gravity_factor)
    return depth


def getPlotInfo(plot):
    lines = [m for m in plotlist[plot] if type(m) == int]
    measlist = [plotlist[plot][line]['title'] for line in lines]
    return lines, measlist
    
    
def getLineProperties(plot, line):
    line_info = plotlist[plot][line]
    ds = locations[line_info['location']][line_info['filetype']]
    time_data = list(ds['datetime'])
    y_data = list(pd.to_numeric(ds[line_info['column']], errors = 'coerce'))
    return line_info, time_data, y_data


def buildStaticPlots(directory, time_min, time_max):
    '''Builds set of svg plots of timeseries data and HTML file for display'''
    for plot in plotlist:

        '''Builds set of svg plots of timeseries data'''
        fig, ax = plt.subplots(figsize = (plt_w, plt_ht))
        lines, measlist = getPlotInfo(plot)
        
        # Gather and plot the raw data for each line
        for line in lines:
            line_info, time_data, y_data = getLineProperties(plot, line)
            
            ax.plot(time_data, y_data, linewidth = 0.5, color = line_info['color'])
            
        ax.set_xlabel('Date')
        ax.set_ylabel(plotlist[plot]['y_axis'])
        ax.legend(measlist)
        y_range = plotlist[plot]['range']
        if type(y_range) == tuple and len(y_range) == 2:
            ax.set_ylim(y_range)
    
        # Save the plots
        fig.savefig(directory + '\\' + plt_pfx + plot + '.svg',
                    transparent = True)
   
    # Write HTML file
    pageHTML = '''
    <HTML>
    <header>
    <h1>Great Salt Lake Microbialite Observatory</h1>
    <p>Data plotted from ''' + time_min + ' to ' + time_max + '''</p>
    <p>Page last updated ''' + str(pd.datetime.now().date()) + '''
    </header>
    <body>
    <h2>Logger data plots</h2>'''
    for plot in plotlist:
        pageHTML = pageHTML + '''
        <p><img src = "''' + plt_pfx + plot + '.svg" alt = "' + plot + '"></p>'
    pageHTML = pageHTML + '''
    </body>
    </HTML>'''
    # Write HTML String to file.html
    filename = directory + '\\GSLMO_plots.html'
    if os.path.isfile(filename):
        os.remove(filename)
    with open(filename, 'w') as file:
        file.write(pageHTML)  



def buildBokehPlots(directory):
    # Set up the bokeh page
    figures = []
    
    for plot in plotlist:
        lines, measlist = getPlotInfo(plot)
        
        # Build the bokeh figure
        fig = figure(plot_height = plt_ht*100, plot_width = plt_w*100,
                     tools = toolset, x_axis_type = 'datetime',
                     title = plot.title())
        
        # Gather and plot the raw data for each series
        for i,line in enumerate(lines):
            line_info, time_data, y_data = getLineProperties(plot, line)
            
            # Generate smoothed hourly data
            y_df = pd.DataFrame(data = y_data, index = time_data,
                                columns = ['y'], copy = True)
            y_df = y_df[~y_df.index.duplicated()]
            y_df = y_df.resample('1T').interpolate(
                'index', limit = 20, limit_area = 'inside').resample(
                    'h').asfreq().dropna()
            # Find daily min/max values
            daily_mm = y_df.resample('D')['y'].agg(['min','max'])        
            # ax.fill_between(daily_mm.index, daily_mm['min'], daily_mm['max'])
            
            # Format the data for bokeh glyph render
            x = np.hstack((daily_mm.index, np.flip(daily_mm.index)))
            y = np.hstack((daily_mm['min'], np.flip(daily_mm['max'])))
            datasource = ColumnDataSource(dict(x=x, y=y))
            
            # Build the figure
            fig.patch('x', 'y', color = line_info['color'],
                      alpha = 0.6, source = datasource,
                      legend_label = measlist[i])
            
        # Label axes and title
        fig.xaxis.axis_label = 'Date'
        fig.yaxis.axis_label = plotlist[plot]['y_axis']
        
        # Configure legend
        fig.legend.location = 'top_left'
        fig.legend.click_policy = 'hide'

        
        # Link figure axes
        if figures:
            fig.x_range = figures[0].x_range
            
        figures.append(fig)
    
    # Save HTML page
    figures.insert(0, Div(text = bokeh_head))
    # show(column(figures))
    output_file(directory + '\\GSLMO_plots_bokeh.html')
    save(column(figures))
        

#%%
####################
# MAIN FUNCTION
####################
if __name__ == '__main__': 
    
    # Load HOBO files
    directory, time_min, time_max = loadHOBOFiles()

    # Build raw data plots and save HTML file
    buildStaticPlots(directory, time_min, time_max)
    
    # Build Bokeh plots
    buildBokehPlots(directory)


       