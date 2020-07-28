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
    python DensityDiff.py

Dependencies Install:
    sudo apt-get install python3-pip python3-dev
    pip install datetime
    pip install numpy
    pip install matplotlib

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
# Format spreadsheet so columns are consistently named
# Each month, automatically import and add new data
# Export each tab as csv






####################
# IMPORTS
####################
import ResearchModules

import os
import pandas as pd
import matplotlib.pyplot as plt

####################
# VARIABLES
####################
datasets = {
    'Site A'    : {
        'water_density' : 1.07
        },
    'Site B'    : {
        'water_density' : 1.09
        }
    }

plotlist = {
    'depth'         : {
        'y_axis'        : 'Water depth (m)',
        'range'         : 'Auto',
        
        1   : {
            'dataset'   : 'Site A',
            'filetype'  : 'HOBO',
            'column'    : 'calc_water_depth_m',
            'title'     : 'Site A (calculated)'
            },
        2   : {
            'dataset'   : 'Site B',
            'filetype'  : 'HOBO',
            'column'    : 'calc_water_depth_m',
            'title'     : 'Site B (calculated)'
            },
        },
    
    'temperature'   : {
        'y_axis'        : 'Temperature (\degC)',
        'range'         : (-5,35),
        
        1   : {
            'dataset'   : 'Site A',
            'filetype'  : 'HOBO',
            'column'    : 'ws_air_temp_C',
            'title'     : 'Antelope Island weater station air temp'
            },
        2   : {
            'dataset'   : 'Site A',
            'filetype'  : 'HOBO',
            'column'    : 'pndt_water_temp_C',
            'title'     : 'Site A water temp - Pendant'
            },
        3   : {
            'dataset'   : 'Site B',
            'filetype'  : 'HOBO',
            'column'    : 'pndt_water_temp_C',
            'title'     : 'Site B water temp - Pendant'
            }
        },
    
    'light'         : {
        'y_axis'        : 'Irradiance (lumen/ft2)',
        'range'         : (0, 7000),
        
        1   : {
            'dataset'   : 'Site A',
            'filetype'  : 'HOBO',
            'column'    : 'bttn_top_light_lumen_ft2',
            'title'     : 'Site A shuttle top'
            },
        2   : {
            'dataset'   : 'Site B',
            'filetype'  : 'HOBO',
            'column'    : 'bttn_top_light_lumen_ft2',
            'title'     : 'Site B shuttle top'
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

####################
# FUNCTIONS
####################

def calc_depth(hobo_dataset, water_density):
    '''Calculate water depth from pressure data and assumed density'''
    gravity_factor = 9.80665
    depth = ((hobo_dataset['pndt_water_pressure_kPa']
              - hobo_dataset['ws_air_pressure_kPa'])
             * water_density / gravity_factor)
    return depth


#%%
####################
# MAIN FUNCTION
####################
if __name__ == '__main__':
    
    
    '''
    PROCESSING SEQUENCE:
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
    '''
    
    
    # Load HOBO files
    directory = os.getcwd()
    for dataset in datasets:
        # Get file and data
        filename, directory, data = ResearchModules.fileGet(
            'Select ' + dataset + ' combined HOBO file', tabletype = 'HOBO',
            directory = directory)
        # Drop na rows (rows with no values)
        data = data.loc[data.index.dropna()]
        # Convert datetime strings to datetime objects
        data['datetime'] = pd.to_datetime(data.index)
        
        # Do depth calculations
        water_density = datasets[dataset]['water_density']
        data['calc_water_depth_m'] = calc_depth(data, water_density)
        
        # Save
        datasets[dataset]['HOBO'] = data

    # Build plots
    fig, axs = plt.subplots(len(plotlist), 1, sharex = True,
                            figsize = (plt_w, plt_ht * len(plotlist)))
    for i, plot in enumerate(plotlist):
        lines = [m for m in plotlist[plot] if type(m) == int]
        measlist = [plotlist[plot][line]['title'] for line in lines]
        time_data = []
        y_data = []
        # Gather the data
        for line in lines:
            # Add dataset (time values and y) to DataFrame
            line_info = plotlist[plot][line]
            ds = datasets[line_info['dataset']][line_info['filetype']]
            time_data.append(list(ds['datetime']))
            y_data.append(list(
                pd.to_numeric(ds[line_info['column']], errors='coerce')))
            
        # Plot the data
        ResearchModules.plotTimeseries(
            axs[i], time_data, y_data, plotlist[plot]['y_axis'],
            legend = measlist)
        y_range = plotlist[plot]['range']
        if type(y_range) == tuple and len(y_range) == 2:
            axs[i].set_ylim(y_range)
    
    # Save the plots
    fig.savefig(directory + '\\GSL_plots.svg', transparent = True)
            
    # Add plots to html file
    
    
        
    # Load field notes
    # Get file and data
    filename, directory, data = ResearchModules.fileGet(
        'Select field notes file', tabletype = 'field')

       