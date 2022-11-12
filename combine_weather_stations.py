# -*- coding: utf-8 -*-
"""
Created on Sun Nov  6 21:37:48 2022

@author: cariefrantz

Combines weather data from multiple stations by averaging where there is
overlap.

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
stations = ['KUTSYRAC22','KUTSYRAC27']
col_P = 'Pressure (in)'
col_precip = 'Precip. Accum. (in)'
cols = [col_P, col_precip]

#%%
####################
# MAIN FUNCTION
####################
if __name__ == '__main__':
    
    # Read in & process files
    dirpath = os.getcwd()
    stationdata = {}
    col_list=[]
    for station in stations:
        # Read in file
        filename, dirpath, data = ResearchModules.fileGet(
            'Select file with weather data for station ' + station,
            directory=dirpath)
        # Format timestamp
        data.index = pd.to_datetime(data.index, errors='coerce')
        # Format the rest
        for col in cols:
            data[col] = pd.to_numeric(
                data[col], errors='coerce')
        # Resample to 15 minute intervals
        col_list.extend([station + '_' + col for col in cols])
        stationdata[station] = data[cols].dropna().resample('15T').mean()
    
    # Merge both series on timestamp
    stationdata_merged = stationdata[list(stationdata)[0]].merge(
        stationdata[list(stationdata)[1]], on='Time', how='outer')
    stationdata_merged.rename(
        columns=dict(zip(list(stationdata_merged.columns),col_list)),
        inplace=True)
    
    # Average values when both are available
    for n, col in enumerate(cols):
        stationdata_merged['avg_' + col] = stationdata_merged[[col_list[n], col_list[len(cols)+n]]].mean(axis=1)
    
    # Save the dataframe as a new file
    stationdata_merged.to_csv(
        dirpath + '/' + '-'.join(stations) + '_P-precip_data_merged.csv')

