# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 14:30:35 2023

@author: cariefrantz

Calculates pearson correlation statistics for microscopy and extract results
of biological samples in the GSL microbialite desiccation project.

"""

####################
# IMPORTS
####################

import ResearchModules
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr


####################
# VARIABLES
####################
directory = os.getcwd()     # Directory for saving the page
measurements = [
    'Calc. Chl a in sample (mg/g)','Avg. % green in random images',
    'Avg. % DAPI fluorescence', 'Avg. % Chl fluorescence',
    'Avg. % Calcein fluorescence','Conc. Extractable DNA (ng/g)']


####################
# FUNCTIONS
####################

def importData():
    '''
    Imports the spreadsheet, returns pandas.DataFrame containing the core data.
    '''
    # Import spreadsheet
    filename, dirpath, data = ResearchModules.fileGet(
        'Bio-meas file', file_type = 'excel', directory=directory,
        header_row = 1, index_col=0, sheet_name = 'bio_results_compiled')
    
    # Delete any rows not containing samples
    data = data[data.index.notnull()]
    data = data.loc[data.index.str.contains('-')]
    
    return data, dirpath

def Pearson(data, dirpath):
    '''
    Pearson correlation coefficients for different measurements

    '''
    # Set up grid
    header = pd.MultiIndex.from_product(
        [measurements,['c','p']], names=['meas','stat'])
    statgrid = pd.DataFrame(index = measurements, columns = header)
    # Loop through each measurement each way
    for meas1 in measurements:
        for meas2 in measurements:
            if meas1 != meas2:
                meastable = data[[meas1,meas2]].copy()
                # Get rid of non-numeric values
                meastable = meastable[pd.to_numeric(data[meas1],errors='coerce').notnull()]
                meastable = meastable[pd.to_numeric(data[meas2],errors='coerce').notnull()]
                
                # Calculate pearson correlation
                c,p = pearsonr(meastable[meas1],meastable[meas2])
                statgrid.loc[meas1][meas2,'c'] = c
                statgrid.loc[meas1][meas2,'p'] = p
                
    statgrid.to_excel(dirpath + '/pearson_stats.xlsx')
            
    return statgrid
            
            #%%
            ####################
            # CODE
            ####################
            if __name__ == '__main__': 
                data, dirpath = importData()
                
