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
    
    # Average both when both available
    # !! THIS ISN'T WORKING, NOT SURE WHY
    stationdata_merged = pd.merge_asof(
        stationdata[list(stationdata)[0]], stationdata[list(stationdata)[1]], direction='nearest')

