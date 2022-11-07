# -*- coding: utf-8 -*-
"""
Created on Sun Nov  6 21:37:48 2022

@author: cariefrantz
"""
import ResearchModules
import os

stations = ['KUTSYRAC22','KUTSYRAC27']

####################
# MAIN FUNCTION
####################
if __name__ == '__main__':
    
    # Read in & process files
    
    dirpath = os.getcwd()
    for station in stations:
        filename, dirpath, data = ResearchModules.fileGet(
            'Select file with weather data for station ' + station,
            directory=dirpath)
    
    
        # Smooth station's data to 15 mins
    
    # Average both when both available

