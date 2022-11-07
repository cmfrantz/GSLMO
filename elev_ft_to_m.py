# -*- coding: utf-8 -*-
"""
Created on Sun Nov  6 16:23:47 2022

@author: cariefrantz

Converts downloaded USGS lake elevation data from ft to m & saves
"""


####################
# IMPORTS
####################
import ResearchModules
import pandas as pd

####################
# VARIABLES
####################
ft_col = '14n'

#%%
####################
# MAIN FUNCTION
####################
if __name__ == '__main__': 
      
    # Load in file
    filename, dirpath, data = ResearchModules.fileGet('Select elevation file')
    
    # Convert ft to m
    data['m'] = round(pd.to_numeric(data[ft_col], errors='coerce')/3.281,1)
    
    # Save file
    data.to_csv(filename[:-4]+'_m.csv')