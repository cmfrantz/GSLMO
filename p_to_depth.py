# -*- coding: utf-8 -*-
"""
Created on Sun Nov  6 20:03:48 2022

@author: cariefrantz

Uses air and water pressure data to calculate water depth

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

# Acceleration due to gravity (m/s2)
gravity_factor = 9.80665

# Range of density values (g/cm3)
density_max = 1.17
density_min = 1.08

# File import details
col_air_dt = 'Time'
col_air_pressure_abs_in = 'P_avg_inHg'
col_water_dt = 'Datetime'
col_water_pressure_kPa = 'P_abs'


####################
# FUNCTIONS
####################
    
    
#%%
####################
# MAIN FUNCTION
####################
if __name__ == '__main__':
    # Load in files for air and water pressure
    dirpath = os.getcwd()
    filename, dirpath, air_data = ResearchModules.fileGet(
        'Select file with air pressure data', directory=dirpath)
    filename, dirpath, water_data = ResearchModules.fileGet(
        'Select file with water pressure data (Site B pendant)',
        directory=dirpath)
    
    # Convert indices to timeseries
    air_data.index = pd.to_datetime(air_data.index, errors='coerce')
    water_data.set_index(col_water_dt, inplace=True)
    water_data.index = pd.to_datetime(water_data.index, errors='coerce')
    
    # Get appropriate data
    air_data['P_air_abs_inHg'] = air_data[col_air_pressure_abs_in]
    water_data['P_water_kPa'] = water_data[col_water_pressure_kPa]
    
    # Convert pressure units
    air_data['P_air_abs_Nm2'] = ResearchModules.inHg_to_Nm2(
        air_data['P_air_abs_inHg'])
    water_data['P_water_Nm2'] = ResearchModules.kPa_to_Nm2(
        water_data['P_water_kPa'])
    
    # Resample timeseries to 15 min & combine
    air_data_rs = air_data.resample('15T').mean()
    water_data_rs = water_data.resample('15T').mean()
    data_merged = air_data_rs.merge(
        water_data_rs, left_index=True, right_index=True, how='outer')  
    
    # Calculate depth
    data_merged['depth_min'] = ResearchModules.calcDepth(
        data_merged['P_water_Nm2'], data_merged['P_air_abs_Nm2'], density_max)
    data_merged['depth_max'] = ResearchModules.calcDepth(
        data_merged['P_water_Nm2'], data_merged['P_air_abs_Nm2'], density_min)
    
    # Save combined file with calculated depths
    data_merged.to_csv(dirpath + '/water_air_merged_wDepth.csv')
    
    
    