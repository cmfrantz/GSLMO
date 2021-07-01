#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Carie Frantz'
__email__ = 'cariefrantz@weber.edu'
"""DataProcessing
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
    pip install sys
    pip install subprocess
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
DO
    compare the weather data at 3 stations and see what is useable
    compile weather data and replace data in existing files, re-generate plots

FIX
    trimPendantData needs to check for any wacky values mid-log
    use WUScraper instead of station script to load weather data
    
ADD
    lake elevation data to depth plots
    field data plots

'''

####################
# IMPORTS
####################
import ResearchModules

import os
import sys
import subprocess

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from bokeh.io import show
from bokeh.layouts import column
from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource, Div


####################
# GLOBAL VARIABLES
####################

####################
# DATA DOWNLOAD VARIABLES

# URL of remote files
GSLMO_data_URL = 'http://faculty.weber.edu/cariefrantz/GSL/data/'

GSLMO_standard_data_cols = ['datetime','ws_air_temp_C','ws_air_pressure_kPa',
                            'pndt_water_temp_C','pndt_water_pressure_kPa',
                            'dPressure_kPa','calc_water_depth_m']

filelist_remote = {
    'GSLMO Site A'  : {
        'filename'  : 'SiteA_combined.csv',
        'header'    : 0,
        'timecol'   : 'datetime',
        'datacols'  : (GSLMO_standard_data_cols + 
                       ['bttn_top_temp_C', 'bttn_top_light_lumen_ft2',
                        'meas_water_depth_m'])
        },
    'GSLMO Site B'  : {
        'filename'  : 'SiteB_combined.csv',
        'header'    : 0,
        'timecol'   : 'datetime',
        'datacols'  : (GSLMO_standard_data_cols +
                       ['bttn_top_temp_C', 'bttn_top_light_lumen_ft2',
                        'bttn_side_temp_C', 'bttn_side_light_lumen_ft2',
                        'meas_water_depth_m'])
        },
    'Lake Elevation'    : {
        'filename'  : 'LakeElevationSaltair.csv',
        'header'    : 0,
        'timecol'   : '20d',
        'datacols'  : ['source','site','date','elevation_ft','validated']
        }
    }

weather_station_download_columns = ['ws_temp_F', 'ws_rel_pressure_inHg',
                                    'ws_abs_pressure_inHg']

####################
# DATA IMPORT VARIABLES

# Default directory
directory = os.getcwd()

# Types of input files and available variables
filelist_all = {
    'Site A'    : ['HOBO pendant', 'HOBO button top (A)'],
    'Site B'    : ['HOBO pendant', 'HOBO button top (B)',
                   'HOBO button side (C)']
        }
HOBO_data_col_names = {
    'pendant'   : ['pndt_water_pressure_kPa', 'pndt_water_temp_C'],
    'button'    : ['bttn_temp_C', 'bttn_light_lumen_ft2']
    }
button_prefixes = {
    'Site A'    : {
        'bttn_top'    : 'HOBO button top (A)'
        },
    'Site B'    : {
        'bttn_top'    : 'HOBO button top (B)',
        'bttn_side'   : 'HOBO button side (C)'}
    }

# Weather station data import variables
lim_dTemp = 1   # Exclude any lines where the temperature change exceeds this
lim_dDays = 10  # Max number of days to download from remote weater station
                # at a time
AMBIENT_API_KEY = '35c8a71b05324137a0bc3d220d17c6182df7184953d148c4b8fc8cafe6e06192'

# File in which downloaded weather data is archived
DATA_CACHE_FILE = 'weather-data-cache.csv'


####################
# DATA PROCESSING VARIABLES
density = {
    'Site A'    : 1.08,
    'Site B'    : 1.09
    }

date_fmt = '%Y-%m-%d'



####################
# PLOT VARIABLES

# Color Palette
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
            }
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


####################
# BOKEH PAGE VARIABLES
        
plt_ht = 5
plt_w = 10
plt_pfx = 'GSL_plots_'
toolset = 'xwheel_zoom, pan, box_zoom, reset, save'

td_style = ' style = "padding: 5px"'
bokeh_head = ResearchModules.GSLMO_html_head + '''
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


####################
### MASTER SCRIPT TO PROCESS NEW DATA
def processNewHOBOData():
    '''Run this after retrieving new HOBO data from the field in order to
        update files and regenerate plots.'''

    # Download logger data from server
    GSLMO_data = get_files_from_server()
    
    # Get new HOBO files from user
    HOBOfiles, time_min, time_max = load_new_HOBO_files()
    
    # Get weather data
    ws_resampled = load_weather_data(time_min, time_max)
    
    # Merge HOBO data with weather data and add to downloaded data
    for loc in HOBOfiles:
        combined_data = merge_HOBO_data(
            loc, HOBOfiles[loc],
            ws_resampled[['ws_air_pressure_kPa', 'ws_air_temp_C']])
        merged_data = add_new_data(GSLMO_data['GSLMO ' + loc], combined_data)
        # Save to locations
        locations[loc]['HOBO'] = merged_data
        merged_data.to_csv(os.getcwd()+ '/' + loc.replace(' ','')
                           +'_combined.csv', index=False,
                           columns=filelist_remote['GSLMO ' + loc]['datacols'])
        
    # Grab and save latest lake elevation data
    # Find date of last validated elevation value
    ev = GSLMO_data['Lake Elevation']
    sdate_min = pd.Timestamp(ev[ev['10s']=='P'].iloc[0].loc['20d']).strftime(
        '%Y-%m-%d')
    sdate_max = time_max.strftime('%Y-%m-%d')
    # Download new elevation data
    elev_data = download_lake_elevation_data(sdate_min, sdate_max)
    # Append to saved elevation data
    elev_data = ev.append(elev_data)
    elev_data.drop_duplicates(subset='20d', keep='last', inplace=True)
    elev_data.to_csv(os.getcwd()+'/'+'LakeElevationSaltair.csv', index=False)
      
    # Build plots
    print('Data compiled. Building website with updated plots.')
    buildBokehPlots(os.getcwd())

    print(
        '''
        **************************************
        *     WOOHOO! Processing complete.   *
        **************************************
                 *''*            *''*
         *''*   *_\/_*   *''*   *_\/_*   *''*
        *_\/_*  * /\ *  *_\/_*  * /\ *  *_\/_*
        * /\ *   *''*   * /\ *   *''*   * /\ *
         *''*      .     *''*     .      *''*
           .        .     .      .        .
            .        .   .      .        .
        
        **************************************
        *  You should now upload the files   *
        *  generated to the remote server.   *
        **************************************
        ''')


####################
### SCRIPTS TO GET AND PROCESS HOBO LOGGER DATA
    
def trim_HOBO(data, logger_type):
    ''' This script trims HOBO data and removes bad values
    
    Parameters
    ----------
    data : pandas.DataFrame
        raw HOBO input data
    logger_type : str
        options are 'pendant' and 'button'

    Returns
    -------
    pandas.DataFrame
        Trimmed data with datetime as index.
        
    '''

    col_list = list(data.columns)
    
    # Trim logger data
    if logger_type == 'pendant':
        # cols_log = list(data.columns)[3:]
        # Delete anything before and after 'Logged'
        # toprow = list(data[data[cols_log[0]] == 'Logged'].index)[0] + 1
        # botrow = list(data[data[cols_log[1]] == 'Logged'].index)[0]
        # Remove rows containing 'Logged'
        data = data[~data.eq('Logged').any(1)]
        # Reindex with timestamp
        data.set_index(col_list[0], inplace = True)
        col_list = list(data.columns)
    
    toprow = 0
    botrow = len(data)
        
    # Rename columns
    cols_data = HOBO_data_col_names[logger_type]
    col_map = dict(zip(col_list, cols_data))
    data.rename(columns = col_map, inplace = True)
    
    # Trim matrix to get rid of likely out-of-water values
    data[cols_data] = data[cols_data].apply(pd.to_numeric, errors = 'coerce')
    data = find_valid_data_by_temp(
        data, cols_data, row_start = toprow, row_end = botrow)
        
    # Reindex matrix
    data['timestamp'] = pd.to_datetime(data.index.values.tolist())
    data.set_index('timestamp', inplace = True)
    
    return data


def find_valid_data_by_temp(data, cols_data, row_start, row_end,
                            lim_checkrows = 10):
    '''Looks for and trims any data at start or end of logger dataset with
    large temperature swings indicative of subaerial exposure'''
    temp_col_name = [col for col in data.columns if 'temp' in col][0]
    # Delete any top lines above a T change >= lim_dt
    for row in range(row_start + 1, row_start + lim_checkrows):
        if abs(data.iloc[row][temp_col_name] 
               - data.iloc[row-1][temp_col_name]) >= lim_dTemp:
            row_start = row
    # Delete any bottom lines above a T change >= lim_dt
    for row in np.arange(row_end-1, row_end-lim_checkrows-1, -1):
        if abs(data.iloc[row][temp_col_name]
               - data.iloc[row-1][temp_col_name]) >= lim_dTemp:
            row_end = row
    # Trim
    return data.iloc[np.arange(row_start, row_end)][cols_data].copy()      
    

def loadHOBOFiles():
    '''Loads in the combined HOBO logger datasets'''
    directory = os.getcwd()
    for location in locations:
        # Get file and data
        filename, directory, data = ResearchModules.fileGet(
            'Select ' + location + ' combined HOBO file',
            tabletype = 'HOBO_comb', directory = directory)
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

    
def get_files_from_server():
    '''  Loads in existing compiled files from the web server '''
    GSLMO_data = {}
    for file in filelist_remote:
        print('Downloading ' + file + ' data from remote server...')
        file_info = filelist_remote[file]
        GSLMO_data[file] = pd.read_csv(GSLMO_data_URL + file_info['filename'],
                                       header = file_info['header'],
                                       error_bad_lines=False)
        GSLMO_data[file].index = pd.to_datetime(
            GSLMO_data[file][file_info['timecol']])
    return GSLMO_data


def load_new_HOBO_files():
    '''Gets new HOBO files from the user and processes them'''
    directory = os.getcwd()
    HOBOfiles = {}
    # Ask user for each file, load files
    for loc in filelist_all:
        HOBOfiles[loc] = {}
        for file in filelist_all[loc]:
            if input('Load ' + loc + ' ' + file + ' file? Y/N  > ') == 'Y':
                filename, directory, HOBOfiles[loc][file] = (
                    ResearchModules.fileGet(
                        'Select ' + loc + ' ' + file + ' file',
                        tabletype = 'HOBO_raw', directory = directory))
       
    # Grab data from each HOBO dataset
    print('Loading datasets...')
    time_min = ''
    time_max = ''
    for loc in HOBOfiles:
        for file in HOBOfiles[loc]:
            print('Processing ' + loc + ' ' + file + '...')
            # Trim and format the data
            data = HOBOfiles[loc][file].copy()
            if 'pendant' in file: data = trim_HOBO(data, 'pendant')
            elif 'button' in file: data = trim_HOBO(data, 'button')
            HOBOfiles[loc][file] = data.copy()

            # Find start and end dates
            if not time_min or time_min > min(data.index):
                time_min = min(data.index)
            if not time_max or time_max < max(data.index):
                time_max = max(data.index)
                
    return HOBOfiles, time_min, time_max


def merge_HOBO_data(loc, file_set, ws_data):
    ''' Merge HOBO data at each site based on timestamp

    Parameters
    ----------
    loc : str
        Location name (i.e., 'Site A' or 'Site B').
    file_set : dict
        Dict containing all of the HOBO files for the site.
    ws_data : pandas.DataFrame
        DataFrame containing the weather station data to be merged.

    Returns
    -------
    combined_data : pandas.DataFrame
        Merged data.

    '''

    # Grab weather station data
    combined_data = ws_data.copy()
    
    data_cols = []
    
    # Merge pendant data
    if 'HOBO pendant' in list(file_set):
        combined_data = (
            pd.merge_asof(combined_data, file_set['HOBO pendant'],
                          left_index = True, right_index = True,
                          tolerance = pd.Timedelta('15T')))
        data_cols.append(HOBO_data_col_names['pendant'][0])
    else: combined_data = pd.merge(
        combined_data, pd.DataFrame(
            np.nan, index = combined_data.index,
            columns = HOBO_data_col_names['pendant']),
        left_index = True, right_index = True)
    
    # Merge button data
    button_files = [file for file in file_set if 'button' in file]
    buttons = button_prefixes[loc]
    for button in list(buttons):
        if buttons[button] in button_files:
            button_data = file_set[buttons[button]].copy()
            new_col_names = [column.replace('bttn',button) for column in list(button_data.columns)]
            button_data.rename(columns = dict(zip(button_data.columns, new_col_names)), inplace = True)
            combined_data = (
                pd.merge_asof(combined_data,
                              button_data,
                              left_index = True, right_index = True,
                              tolerance = pd.Timedelta('15T')))
            data_cols.append(new_col_names[0])
            
    # Trim any NaN rows at start and end of DataFrame
    idx = combined_data[data_cols].fillna(method='ffill').dropna(
        how='all').index
    res_idx = combined_data[data_cols].loc[idx].fillna(method='bfill').dropna(
        how='all').index
    combined_data = combined_data.loc[res_idx]
    
    
    # Calculate depth
    combined_data['dPressure_kPa'] = (
        combined_data['pndt_water_pressure_kPa'] -
        combined_data['ws_air_pressure_kPa'])
    combined_data['calc_water_depth_m'] = (
        combined_data['dPressure_kPa'] * density[loc] / 
        ResearchModules.gravity_factor)
    
    # Ask user for manual water depth measurement
    meas_water_depth_in = input('Enter the manually-measured water depth'
                               + ' (in inches) at ' + loc + '.'
                               + ' It will be appended to the end of the'
                               + ' HOBO logger dataset.'
                               + ' If no measurement was taken, enter '
                               + ' "na".  > ')  
    try:
        float(meas_water_depth_in)
        # Find the last logger measurement
        last_index = combined_data.index[0]
        for col in data_cols:
            last = combined_data.apply(pd.Series.last_valid_index)[col]
            if last_index < last:
                last_index = last
        # Enter the converted measurement
        meas_water_depth_m = float(meas_water_depth_in) * 0.0254
        combined_data.loc[last_index, 'meas_water_depth_m'] = (
            meas_water_depth_m)
        print('Entering ' + str(meas_water_depth_m) + ' m ('
              + meas_water_depth_in + '").')
    except ValueError:
        print('No manual measurement entered.')
        
    return combined_data


def add_new_data(old_data, new_data):
    '''
    Adds new data to old data for site

    Parameters
    ----------
    old_data : pandas.DataFrame
        DataFrame containing the old data.
    new_data : pandas.DataFrame
        DataFrame containing the new data. Columns should match those in old data that should be overwritten.

    Returns
    -------
    merged_data : pandas.DataFrame
        DataFrame containing the merged data.

    '''
    new_data['datetime'] = new_data.index
    merged_data = old_data.append(new_data)
    merged_data.drop_duplicates(subset='datetime', keep='last', inplace=True)
    return merged_data
       
             

####################
### WORKING SCRIPTS TO DOWNLOAD EXTERNAL DATA

def download_lake_elevation_data(sdate_min, sdate_max):
    """
    This function downloads lake elevation data at Saltair from the USGS
    waterdata web interface

    Parameters
    ----------
    sdate_min : string
        Start date for data download in format 'YYYY-mm-dd'.
        (use date_min.strftime('%Y-%m-%d') to format a timestamp)
    sdate_max : string
        End date for data download in format 'YYYY-mm-dd'.

    Returns
    -------
    elev_data : pandas DataFrame containing five columns:
        agency | site_no | datetime | elevation (ft) | Data qualification
        (A = Approved for publication, P = Provisional)

    """
    site_no = 10010000 # Great Salt Lake at Saltair Boat Harbor, UT
    
    # Generate URL
    data_URL = ("https://waterdata.usgs.gov/nwis/dv?cb_62614=on&format=rdb" +
                 "&site_no=" + str(site_no) + "&referred_module=sw&period=" +
                 "&begin_date=" + sdate_min +
                 "&end_date=" + sdate_max)
    
    # Load in website data
    elev_data = pd.read_csv(data_URL, sep = '\t', header = 29)
    
    # Save timestamps as index and convert date format
    elev_data['date'] = pd.to_datetime(elev_data['20d'])
    elev_data['20d'] = elev_data['date'].dt.strftime(date_fmt)
    elev_data.set_index('date', drop=True, inplace=True)
    
    return elev_data


####################
### WORKING SCRIPTS TO DOWNLOAD AND PROCESS WEATHER STATION DATA

def get_station_data_for_period(date_min, date_max):
    """
    This function gets weather data for a period of time
    Data is downloaded by segments.
    If downloading a file fails, the function continue trying
    """
    print("*** Downloading weather station data ***")
    delta = pd.DateOffset(days = lim_dDays)
    date_curr = date_min  # Start date
    while date_curr < date_max:
        sdate_min = date_curr.strftime(date_fmt)
        # Upper date limit
        if date_curr + delta > date_max:
            sdate_max = date_max.strftime(date_fmt)
        else:
            sdate_max = (date_curr + delta).strftime(date_fmt)
        
        # Try the whole date range first
        allowed_tries = 2
        downloaded = attempt_ws_download(sdate_min, sdate_max, allowed_tries)
        
        # If the download doesn't work for the whole range, try downloading
        # one day at a time
        if not downloaded:
            trydate = date_curr
            for date in range(lim_dDays):
                trydate = date_curr + pd.DateOffset(days = date)
                attempt_ws_download(
                    trydate.strftime(date_fmt),
                    (trydate+pd.DateOffset(days=1)).strftime(date_fmt), 1)            
        # Updating the cache
        update_station_cache(sdate_min, sdate_max)
        # Removing temporary files
        # filename = get_station_data_filename(sdate_min, sdate_max)
        # os.remove(filename)
        # os.remove(filename.replace('.csv', '.txt'))
        # To get the next segment
        date_curr += delta
        

def attempt_ws_download(sdate_min, sdate_max, allowed_tries=3):
    '''
    Attempts to download weather station data from the range specified,
    quits after a max number of allowed tries.
    '''
    print(
        '\nDownloading data for %s to %s...' % (sdate_min, sdate_max),
        end=' ')
    downloaded = False
    for attempt in range(allowed_tries):
        downloaded = get_station_data(sdate_min, sdate_max)
        if downloaded:
            print('  Download successful.')
            break
        else:
            print('  Trying again (' + str(attempt+1)
                  + '/' + str(allowed_tries) + ')...', end=' ')
    if not downloaded:
        print('  Download for range failed.')
    return downloaded
        

def get_station_data(sdate_min, sdate_max, timeout=60):
    '''
    This function runs the external script station_weather.
    Returns true if the data is obtained.
    Data is stored as a csv file in the working directory.
    '''
    success = False
    # Try to run station_weather.py
    try:
        ret = subprocess.run(
            ' '.join(['python', 'StationWeather.py', sdate_min, sdate_max]),
            capture_output=True, timeout=timeout)
    # If the subprocess times out or gives another error, quit
    except:
        success = False
    # If the subprocess runs, determine whether or not it returned good data
    else:
        if ret.returncode != 0:
            # Program execution returns a invalid code
            print('Error: station weather script execution failed')
            print(ret.stdout)
            sys.exit()
        filename = get_station_data_filename(sdate_min, sdate_max)
        data = pd.read_csv(filename)
        if len(data) == 0:
            # Sometimes API requests does not produce any data.
            # If this happens, delete the file.
            os.remove(filename)
            success = False
        else:
            success = True
    return success

    
    
    
    
def combine_weather_files():
    '''
    Function gets and combines all downloaded weather files into a single csv
    '''
    # Get list of files
    weather_file_list, directory = ResearchModules.getFiles(
        'Select weather station data files')
    # Load and combine all files
    combined_weather_data = pd.concat(
        [pd.read_csv(file, header = 0) for file in weather_file_list])
    # Delete replicate rows
    combined_weather_data.drop_duplicates(subset=['DateTime'], inplace = True)
    # Replace index with timestamp and sort
    combined_weather_data['DateTime'] = pd.to_datetime(
        combined_weather_data['DateTime'])
    combined_weather_data.set_index(['DateTime'], drop=True, inplace=True)
    combined_weather_data.sort_index(inplace=True)
    # Find start and end date
    date_min = min(combined_weather_data.index).strftime(date_fmt).replace(
        '-','')
    date_max = max(combined_weather_data.index).strftime(date_fmt).replace(
        '-','')
    # Export as csv
    combined_weather_data.to_csv(date_min + '-' + date_max + '.csv')
    print('Combined weather files.')
    
    return combined_weather_data


def load_weather_data(time_min, time_max):
    '''Gets downloaded weather data from user if user already has weather
    data downloaded somewhere'''
    
    # Ask user for data source
    ws_data_source = input('Download remote weather station data or use'
                           + ' local file? Type "remote" or "local"  > ')
    
    # If remote, try to download data
    i = 0
    max_retries = 5
    if ws_data_source == 'remote':
        for i in range(max_retries):
            try:
                get_station_data_for_period(
                    time_min, time_max + pd.Timedelta(value=1, unit='day'))
                combined_weather_data = combine_weather_files()
                break
            except subprocess.TimeoutExpired:
                print('Trying again to connect to the weather station (Try '
                      + str(i+1) + ')')
                pass
    
    # If local or unable to download data, ask for file and trim to date range
    if ws_data_source == 'local' or i == max_retries-1:
        _, _, combined_weather_data = ResearchModules.fileGet(
            'Select raw weather data file')
    
    # Convert the weather data file
    combined_weather_data = combined_weather_data.astype(float)
    combined_weather_data, ws_resampled = convert_weather_station_data(
        combined_weather_data)
    
    return ws_resampled
   

def convert_weather_station_data(combined_weather_data):
    '''
    Converts raw combined weather station data units, renames columns, and
    resamples to 15 minutes

    Parameters
    ----------
    combined_weather_data : pandas.DataFrame
        Weather data with index = timestamp and columns Temp (degF),
        RelPressure(in), AbsPressure(in).

    Returns
    -------
    combined_weather_data : pandas.DataFrame
        Weather data with index = timestamp and columns .
    ws_resampled : TYPE
        DESCRIPTION.

    '''
    # Replace index with timestamp and sort
    combined_weather_data['DateTime'] = pd.to_datetime(
        combined_weather_data.index)
    combined_weather_data.set_index(['DateTime'], drop=True, inplace=True)
    combined_weather_data.sort_index(inplace=True)
    
    
    # Rename weather station data columns
    combined_weather_data.rename(
        columns = dict(zip(list(
            combined_weather_data.columns),
            weather_station_download_columns)),
        inplace = True)
    
    # Convert weather station data
    combined_weather_data['ws_air_pressure_kPa'] = (
        combined_weather_data['ws_abs_pressure_inHg']*3.386)
    combined_weather_data['ws_air_temp_C'] = (        
        (combined_weather_data['ws_temp_F']-32)*5/9)
    
    # Resample to 15 minute intervals and rename columns
    ws_resampled = combined_weather_data.resample('5T').fillna(
        'nearest').resample('15T').mean()
    
    return combined_weather_data, ws_resampled
       

def update_station_cache(sdate_min, sdate_max):
    """
    This functions updates the cache of weather data.
    That cache is an accumulative local file in which
    every downloaded data is stored.
    """
    filename = get_station_data_filename(sdate_min, sdate_max)
    if not os.path.isfile(filename):
        # A valid file for the given dates does not exist
        print('Warning: station data for the given date range does not exist')
        return
    last_data = pd.read_csv(filename)
    last_data.columns = ['dt', 'temp', 'pressure', 'abs_pressure']
    if not os.path.isfile(DATA_CACHE_FILE):
        # If the cache file does not exists, it is created
        last_data.to_csv(DATA_CACHE_FILE, index=False)
        return
    # Updating the cache file
    cache_data = pd.read_csv(DATA_CACHE_FILE)
    new_cache = pd.concat([last_data, cache_data]).drop_duplicates()
    new_cache.to_csv(DATA_CACHE_FILE, index=False)
    
    
def get_station_data_filename(date_min, date_max):
    """
    Using a minimum and a maximum dates, this function produces a filaname
    for the station downloaded data.
    """
    filename = (date_min.replace('-', '') + '-' + date_max.replace('-', '')
                + '.csv')
    return filename


####################
### WORKING SCRIPTS TO PROCESS AND PLOT DATA
### ONCE IT HAS BEEN IMPORTED, COMBINED, AND CLEANED

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
    # Data is being stored somewhere else... where?
    ds = locations[line_info['location']][line_info['filetype']]
    time_data = list(pd.to_datetime(ds['datetime']))
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
        print('\nBuilding ' + plot + ' plot...')
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
            
            # Format the data for bokeh glyph render (new)
            groups = ResearchModules.nansplit(daily_mm)
            for group in groups:
                # Format x,y coordinates for each patch
                x = np.hstack((group.index, np.flip(group.index)))
                y = np.hstack((group['min'], np.flip(group['max'])))
                datasource = ColumnDataSource(dict(x=x, y=y))
                # Add patch
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
    
    #####
    # Troubleshooting steps
    
    
    
    #####
    # Run this script if new HOBO data needs to be added and plots updated
    processNewHOBOData()
    
    #####
    # Run these scripts if need to update plots from manually-updated files
    
    # Load HOBO files
    # directory, time_min, time_max = loadHOBOFiles()
    
    '''These below are now broken.

    # Build raw data plots and save HTML file
    print('Building basic (static) plots...')
    buildStaticPlots(directory, time_min, time_max)
    
    # Build Bokeh plots
    print('Building Bokeh plots...')
    buildBokehPlots(directory)

    # Tell user to upload everything
    print('Processing complete! Remember to upload the shiny new files.')

    '''
       