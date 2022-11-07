#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Carie Frantz'
__email__ = 'cariefrantz@weber.edu'
"""format_field_data
Created on Sun Nov  6 00:22:20 2022
@author: cariefrantz
@project: GSLMO

Formats downloaded field monitoring data for timeseries plots

This script was created as part of the
Great Salt Lake Microbialite Observatory project

Arguments:  None

Requirements:
    field_monitoring_data.csv
        which should have dates formatted as mm/dd/yyyy and times in 24-hr fmt

Example in command line:
    python format_field_data.py

Dependencies Install:
    sudo apt-get install python3-pip python3-dev
    pip install numpy
    pip install pandas
    
You will also need to have the following files
    in the same directory as this script.
    They contain modules and variables that this script calls.
    ResearchModules.py
If you get an error indicating that one of these modules is not found,
    change the working directory to the directory containing these files.


Copyright (C) 2022  Carie M. Frantz

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
# IMPORTS
####################
import ResearchModules
import pandas as pd

####################
# VARIABLES
####################
file_header_row = 1
date_fmt = '%m/%d/%Y %H:%M'
col_depth = 'Sediment at pipe (to hard ground unless otherwise specified)'
col_T_top = 'Water surface'
col_T_mid = 'Mid (if diff. from max vis).1'
col_T_mvd = 'Max visible depth'
col_T_deep = 'Sed/water interface'

#%%
####################
# MAIN FUNCTION
####################
if __name__ == '__main__': 
      
    # Load in file
    filename, dirpath, data = ResearchModules.fileGet('Select the downloaded field data file', header_row=1)
        
    # Format Datetime
    data['Datetime'] = data['Date'] + ' ' + data['Time']
    
    # Format water depth
    data['water_depth_m'] = data[col_depth]/100
    
    # Format temperatures
    data['T_top_C'] = pd.to_numeric(data[col_T_top], errors='coerce')
    data['T_bot_C'] = pd.to_numeric(data[col_T_deep], errors='coerce')
    data['T_mid_C'] = data[col_T_mid].copy()
    data['T_mid_C'] = pd.to_numeric(
        data['T_mid_C'].combine_first(data[col_T_mvd]), errors='coerce')
    
    # Save file
    data.to_csv(filename[:-4]+'_fmttd.csv')
    
    # Cut down to Site B only
    data_B = data[data['Site'].isin(['B','B3'])]
    data_B.to_csv(filename[:-4]+'_fmttd_B.csv')
    
    
    
    
    
