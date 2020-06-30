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
import datetime
import ResearchModules

####################
# VARIABLES
####################
datasets = {
    'Site A'    : {
        'var_sets'  : ['HOBO_pendant', 'HOBO_top', 'field_obs']
        },
    'Site B'    : {
        'var_sets'  : ['HOBO_pendant', 'HOBO_side', 'HOBO_top', 'field_obs']
        }
    }

plotlist = ['Depth', 'Temperature', 'Light']

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
        'other'         : {
            'field_salinity_pct'        : 
                'Water salinity (%)',
            'field_density_spgr'        : 
                'Water density (sp. gr.)',
            'field_water_depth_m'       : 
                'Water depth (field; m)',
            }
        }
    }


####################
# FUNCTIONS
####################



#%%
####################
# MAIN FUNCTION
####################
if __name__ == '__main__':
    # Load files
    for dataset in datasets:
        # Get file and data
        filename, directory, data = ResearchModules.fileGet(
            'Select ' + dataset + ' combined HOBO file', tabletype = 'HOBO')
        # Drop na rows (rows with no values)
        data = data.loc[data.index.dropna()]
        # Convert datetime strings to datetime objects
        data['datetime'] = [datetime.strptime(dtime, '%m/%d/%Y %H:%M')
                            for dtime in data.index]
        # Save
        datasets[dataset]['HOBO data'] = data

    # Build plots
    for plot in plotlist:
        