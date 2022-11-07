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
P_col = 'Pressure (in)'

#%%
####################
# MAIN FUNCTION
####################
if __name__ == '__main__':
    
    # Read in & process files
    dirpath = os.getcwd()
    stationdata = {}
    for station in stations:
        # Read in file
        filename, dirpath, data = ResearchModules.fileGet(
            'Select file with weather data for station ' + station,
            directory=dirpath)
        # Format timestamp
        data.index = pd.to_datetime(data.index, errors='coerce')
        # Format the rest
        data[P_col] = pd.to_numeric(data[P_col], errors='coerce')
        # Resample to 15 minute intervals
        stationdata[station] = data[P_col].dropna().resample('15T').mean()
        stationdata[station] = stationdata[station].to_frame()
    
    # Average both when both available
    stationdata_merged = stationdata[list(stationdata)[0]].merge(
        stationdata[list(stationdata)[1]], on='Time', how='outer')
    stationdata_merged.rename(
        columns=dict(zip(list(stationdata_merged.columns),stations)),
        inplace=True)
    stationdata_merged['P_avg_inHg'] = stationdata_merged.mean(axis=1)
    
    # Save the dataframe as a new file
    stationdata_merged.to_csv(
        dirpath + '/' + '-'.join(stations) + '_Pdata_merged.csv')

