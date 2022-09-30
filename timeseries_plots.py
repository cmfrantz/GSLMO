# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 10:12:33 2022

@author: cariefrantz
@project: GSLMO

Script plots sets of GSL data. It can also be used to plot timeseries data.

"""

####################
# IMPORTS
####################

import ResearchModules
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates



####################
# VARIABLES
####################

# Plot default variables
plotsize_default = (12,6)
resample_interval = '1d'
smooth_interval = '7d'

# Formatting for datetime axis
years = mdates.YearLocator()
months = mdates.MonthLocator()
years_fmt = mdates.DateFormatter('%Y')


####################
# FUNCTIONS
####################

    
    
    
#%%
####################
# MAIN FUNCTION
####################
if __name__ == '__main__': 
    ###############
    # Variables
    
    # Plots to generate
    plots = {
        'elev'  : {
            'datasets'  : ['elevation_Saltair'],
            'ytitle'    : 'Lake elevation (ft asl)'
            },
        'temp'  : {
            'datasets'  : ['temp_A_pend', 'temp_A_butt_A', 'temp_B_pend',
                           'temp_B_butt_B', 'temp_B_butt_C'],
            'ytitle'    : 'Temperature (' + chr(176) + 'C)'
            }
        }
        
    # Datasets to draw from
    datasets = {
        'elevation_Saltair'   : {
            'title'     : 'Elevation at Saltair (USGS)',
            'xcol'      : '20d',
            'ycol'      : '14n',
            'datefmt'   : '%m/%d/%Y'
            },
        'temp_A_pend'   : {
            'title'     : 'Site A Pendant',
            'xcol'      : 'Datetime',
            'ycol'      : 'T_C',
            'datefmt'   : '%m/%d/%Y %H:%M'
            },
        'temp_A_butt_A' : {
            'title'     : 'Site A Button A (top)',
            'xcol'      : 'Datetime',
            'ycol'      : 'T_C',
            'datefmt'   : '%m/%d/%Y %H:%M'
            },
        'temp_B_pend'   : {
            'title'     : 'Site B Pendant',
            'xcol'      : 'Datetime',
            'ycol'      : 'T_C',
            'datefmt'   : '%m/%d/%Y %H:%M'
            },
        'temp_B_butt_B' : {
            'title'     : 'Site B Button B (top)',
            'xcol'      : 'Datetime',
            'ycol'      : 'T_C',
            'datefmt'   : '%m/%d/%Y %H:%M'
            },
        'temp_B_butt_C' : {
            'title'     : 'Site B Button C (side)',
            'xcol'      : 'Datetime',
            'ycol'      : 'T_C',
            'datefmt'   : '%m/%d/%Y %H:%M'
            },
        }
    
    ###############
    # Plotting code
    
    dirpath = os.getcwd()
    
    for plot in plots:
        # Create a new figure
        fig, ax = plt.subplots(figsize=plotsize_default)
        legend=[]
    
        # Plot each line
        for var in plots[plot]['datasets']:
            # Load in the file
            filename, dirpath, data = ResearchModules.fileGet(
                'Select file with data for ' + datasets[var]['title'],
                directory=dirpath)
                  
            # Plot the data
            ResearchModules.plotData(
                data, datasets[var]['xcol'], datasets[var]['ycol'], 'Date',
                plots[plot]['ytitle'], datasets[var]['title'], ax=ax,
                plotsize=plotsize_default, smooth=True, xtype='datetime',
                datefmt=datasets[var]['datefmt'])
            
            # Add to legend
            legend.append(datasets[var]['title'])
            
        # Add the legend
        if len(legend)>1:
            ax.legend(legend)
            
        # Show and save the figure          
        fig.show()
        fig.savefig(plot + '.png')
        fig.savefig(plot + '.svg')
        
    
    