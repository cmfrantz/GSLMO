# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 10:30:32 2023

@author: cariefrantz

Analysis of the microbialite core sampling depths from the
GSL microbialite desiccation biology project

"""

####################
# IMPORTS
####################

import ResearchModules
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import f_oneway


####################
# VARIABLES
####################
directory = os.getcwd()     # Directory for saving the page
samples = ['C1','C2','C3']
sections = {
    'T' : {
        'vals'  : ['T','TM'],
        'fill'  : 'gold',
        'line'  : 'white'
        },
    'M' : {
        'vals'  : ['M','TM','MB'],
        'fill'  : 'darkgreen',
        'line'  : 'darkgreen'
        },
    'B' : {
        'vals'  : ['MB','B'],
        'fill'  : 'black',
        'line'  : 'black'
        }
    }
measurements = [
    'Calc. Chl a in sample (mg/g)','Avg. % green in random images',
    'Avg. % DAPI fluorescence', 'Avg. % Chl fluorescence',
    'Avg. % Calcein fluorescence','Conc. Extractable DNA (ng/g)']
timepoints = [0,7,14,21,72,100]


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
    
    # Delete any rows not containing the samples
    data = data[data['Microbialite / Sample'].isin(samples)]
    
    # Calculate days exposure
    date_min = min(data['Date'])
    data['days_exposure'] = [(date - date_min).days for date in data['Date']]
    
    return data, dirpath


def depthAnalysis(data, dirpath):
    '''
    Plots the core section depths collected at each timepoint
    '''
    
    # Create figure and loop through sections
    fig, ax = plt.subplots(1)
    for section in sections:
        fill_color = sections[section]['fill']
        line_color = sections[section]['line']
        section_vals = data[data['Layer']==section].copy()
        section_vals[['Layer thickness sampled (cm)','Depth from surface - mid (cm)','days_exposure']]=section_vals[['Layer thickness sampled (cm)','Depth from surface - mid (cm)','days_exposure']].astype(float)
        section_vals['min'] = section_vals['Depth from surface - mid (cm)'] - section_vals['Layer thickness sampled (cm)']/2
        section_vals['max'] = section_vals['Depth from surface - mid (cm)'] + section_vals['Layer thickness sampled (cm)']/2
        avg_min = section_vals['min'].mean()
        avg_max = section_vals['max'].mean()
        for sample in samples:
            # Layer on shapes for each layer through time (layer top to layer bottom)
            sample_vals = section_vals[section_vals['Microbialite / Sample']==sample]
            ax.fill_between(
                sample_vals['days_exposure'],
                sample_vals['min'], sample_vals['max'],
                fc = fill_color, alpha = 0.3)
        #ax.plot([0,max(sample_vals['days_exposure'])], [avg_min,avg_min], line_color)
        #ax.plot([0,max(sample_vals['days_exposure'])], [avg_max,avg_max], line_color)
    ax.set_ylabel('Section depth (cm)')
    ax.set_xlabel('Days exposure')
    ax.set_ylim([7,0])
    ax.set_xlim([0,100])
    
    # Save figure
    plt.rcParams['svg.fonttype'] = 'none'
    fig.savefig(dirpath + '/core_depth_analysis.svg', format='svg')
    

def ANOVA(data, dirpath):
    '''
    Conducts an ANOVA testing whether there are significant differences between
    measurements at each timepoint for each core horizon.
    Saves a table with the ANOVA F statistics and p values.
    '''

    # Set up grid for each variable
    header = pd.MultiIndex.from_product(
        [measurements,['F','p']], names=['meas','stat'])
    statgrid_horizon = pd.DataFrame(index = list(sections), columns = header)
    statgrid_time = pd.DataFrame(
        index = list(map(str, timepoints)), columns = header)
    
    # Loop through and calculate ANOVA
    for meas in measurements:
        # Cut the table to only the samples containing the measurement
        meastable = data.loc[data[meas].dropna().index]
        
        # ANOVA by section (comparing timepoints)
        for section in sections:
            # cut table to the section
            valtable = meastable[meastable['Horizon'].isin(sections[section]['vals'])][['days_exposure',meas]]
            # drop nan/dnm
            valtable = valtable[pd.to_numeric(valtable[meas],errors='coerce').notnull()]
            # find unique timepoints
            tp = list(set(valtable['days_exposure']))
            # parse dataset into list of measurements for each timepoint
            dsets = [valtable[valtable['days_exposure']==t][meas] for t in tp]
            # ANOVA calculation
            f,p = f_oneway(*dsets)
            # save calculated ANOVA stats in the dataframe
            statgrid_horizon.loc[section][meas,'F']=f
            statgrid_horizon.loc[section][meas,'p']=p
            
        # ANOVA by timepoint (comparing sections)
        for tp in timepoints:
            # cut table to the timepoint
            valtable = meastable[meastable['days_exposure']==tp][['Horizon',meas]]
            # drop nan/dnm
            valtable = valtable[pd.to_numeric(valtable[meas],errors='coerce').notnull()]
            # if no values for the measurement at the timepoint, skip
            if valtable.empty:
                statgrid_time.loc[str(tp)][meas,'F']=np.nan
                statgrid_time.loc[str(tp)][meas,'p']=np.nan
            # otherwise, calculate ANOVA
            else:
                # parse dataset into list of measurements for each horizon
                dsets = [valtable[valtable['Horizon'].isin(sections[h]['vals'])][meas] for h in sections]
                # ANOVA calculation
                f,p = f_oneway(*dsets)
                # save calculated ANOVA stats in the dataframe
                statgrid_time.loc[str(tp)][meas,'F']=f
                statgrid_time.loc[str(tp)][meas,'p']=p
                
    # Save tables
    statgrid_horizon.to_excel(dirpath+'/core_ANOVA_byHorizon.xlsx')
    statgrid_time.to_excel(dirpath+'/core_ANOVA_byTimepoint.xlsx')
    
#%%
####################
# CODE
####################
if __name__ == '__main__': 
    data, dirpath = importData()
    depthAnalysis(data, dirpath)
    ANOVA(data, dirpath)
    

