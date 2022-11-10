#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Carie Frantz'
__email__ = 'cariefrantz@weber.edu'
"""merge_depths
Created on Tue Nov  8 22:52:03 2022

@author: cariefrantz
@project: GSLMO

Compares manual measurements to USGS logged lake depth measurements
"""

####################
# IMPORTS
####################

import ResearchModules
import os
import pandas as pd


####################
# VARIABLES
####################
siteB_elev_assumed = 1277.26
siteB3_elev_assumed = 1276.55

files = {
    'Saltair'   : {
        'dt_col'    : '20d',
        'depth_col' : 'm'
        },
    'Causeway'  : {
        'dt_col'    : '20d',
        'depth_col' : 'm'
        },
    'manual'    : {
        'dt_col'    : 'Datetime',
        'depth_col' : 'water_depth_m'
        }
    }

#%%
####################
# MAIN FUNCTION
####################
if __name__ == '__main__': 

    # Load in files
    dirpath = os.getcwd()
    for file in list(files):
        # Load in file
        filename, dirpath, data = ResearchModules.fileGet(
            'Select file with ' + file + ' data (csv)', directory=dirpath)
        # Set index
        data.set_index(files[file]['dt_col'], inplace=True)
        # Format timestamp
        data.index = pd.to_datetime(data.index, errors='coerce')
        # Format the rest
        data = pd.to_numeric(data[files[file]['depth_col']], errors='coerce')
        # Resample to 15 minute intervals
        files[file]['data'] = data.dropna().to_frame().resample('1D').mean()

    # Merge on timeseries and create combined file
    data_merged = files['manual']['data'].copy()
    for ds in ['Saltair','Causeway']:
        data_merged = data_merged.merge(
            files[ds]['data'], left_index=True, right_index=True, how='inner')
    data_merged = data_merged.loc[
        data_merged[files['manual']['depth_col']].dropna().index]
    # Drop Site B3 measurements
    # data_merged = data_merged.iloc[0:-2]
    
    # Do depth comparison to both series
    first_val_manual = data_merged['water_depth_m'].iloc[0]
    first_val_Saltair = data_merged['m_x'].iloc[0]
    first_val_Causeway = data_merged['m_y'].iloc[0]
    
    # Calculate depth from offset
    data_merged['depth_vs_Saltair'] = round(
        data_merged['water_depth_m'] - first_val_manual + first_val_Saltair, 2)
    data_merged['depth_vs_Causeway'] = round(
        data_merged['water_depth_m'] - first_val_manual + first_val_Causeway,
        2)
    
    # Calculate depth from assumed elevation
    data_merged['elev_from_depth'] = (
        data_merged['water_depth_m'] + siteB_elev_assumed)
    
    # Calculate difference
    data_merged['delta_Saltair'] = round(
        data_merged['depth_vs_Saltair'] - data_merged['m_x'], 2)
    data_merged['delta_Causeway'] = round(
        data_merged['depth_vs_Causeway'] - data_merged['m_y'], 2)
    data_merged['abs_delta_Saltair'] = abs(data_merged['delta_Saltair'])
    data_merged['abs_delta_Causeway'] = abs(data_merged['delta_Causeway'])

    # Save file
    data_merged.to_csv(dirpath + '/depth_deltas.csv')
    
    # Merge Saltair & Causeway elevations and estimate site B & B3 water depth
    daily_elev_merged = files['Saltair']['data'].copy()
    daily_elev_merged = daily_elev_merged.merge(
        files['Causeway']['data'], left_index=True, right_index=True,
        how='outer')
    daily_elev_merged['avg'] = daily_elev_merged[['m_x','m_y']].mean(axis=1)
    daily_elev_merged['depth_B'] = round(
        daily_elev_merged['avg'] - siteB_elev_assumed, 3)
    daily_elev_merged['depth_B3'] = round(
        daily_elev_merged['avg'] - siteB3_elev_assumed, 3)
    # Replace negative values with zero
    df = daily_elev_merged[['depth_B', 'depth_B3']].copy()
    df[df<0]=0
    daily_elev_merged[['depth_B', 'depth_B3']] = df.copy()
    
    # Save file
    daily_elev_merged.to_csv(dirpath + '/daily_site_depth_calc.csv')
    