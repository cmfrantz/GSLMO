#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Carie Frantz'
__email__ = 'cariefrantz@weber.edu'
"""timeseries_plots
Created on Fri Sep 30 10:12:33 2022

@author: cariefrantz
@project: GSLMO

Script plots compiled GSL timeseries data, including elevation data and
HOBO logger data.

Arguments:  None

Requirements: Need csv files for elevation, temperature, light, and pressure,
    as well as manual field measurements. See the variables 'plots' and 'files'
    in the code for details of formatting, and edit according to how the files
    are formatted.    

Example in command line:
    python timeseries_plots.py

Dependencies Install:
    sudo apt-get install python3-pip python3-dev
    pip install pandas
    pip install matplotlib
    pip install datetime
    
You will also need to have the following files
    in the same directory as this script.
    They contain modules and variables that this script calls.
    ResearchModules.py
If you get an error indicating that one of these modules is not found,
    change the working directory to the directory containing these files.


Copyright (C) 2022  Carie M. Frantz

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>


"""

####################
# TO DO! BEFORE SYNCING
####################
# Delete temp variables with filepaths
# Comment out code to find files from filepaths


####################
# IMPORTS
####################

import ResearchModules
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime



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

# Plots to generate
plots = {
    'elev'  : {
        'ytitle'    : 'Lake elevation (m asl)',
        'ylim'      : [1276, 1279],
        'datasets'  : {
            'elevation at Saltair' : {
                'file'  : 'elevation_Saltair',
                'ycol'  : '14n',
                'conv'  : 'ft_to_m',
                'style' : 'line',
                'axis'  : 1,
                },
            'elevation at Causeway'    : {
                'file'  : 'elevation_Causeway',
                'ycol'  : '14n',
                'conv'  : 'ft_to_m',
                'style' : 'line',
                'axis'  : 1
                },
            'Water depth measured at Site B (m)'  : {
                'file'  : 'manual_data',
                'ycol'  : 'water_depth_m',
                'conv'  : 'none',
                'style' : 'dots',
                'axis'  : 2,
                'ylim'  : [-1.3,1.8]
                }
            }
        },
    'temp'  : {
        'ytitle'    : 'Temperature (' + chr(176) + 'C)',
        'ylim'      : 'auto',
        'datasets'  : {
            'Site A Pendant'   : {
                'file'  : 'site_A_pend',
                'ycol'  : 'T_C',
                'conv'  : 'none',
                'style' : 'line',
                'axis'  : 1
                },
            'Site A Button A (top)'     : {
                'file'  : 'site_A_butt_A',
                'ycol'  : 'T_F',
                'conv'  : 'F_to_C',
                'style' : 'line',
                'axis'  : 1
                },
            'Site B Pendant'   : {
                'file'  : 'site_B_pend',
                'ycol'  : 'T_C',
                'conv'  : 'none',
                'style' : 'line',
                'axis'  : 1
                },
            'Site B Button B (top)'     : {
                'file'  : 'site_B_butt_B',
                'ycol'  : 'T_F',
                'conv'  : 'F_to_C',
                'style' : 'line',
                'axis'  : 1
                },
            'Site B Button C (side)'    : {
                'file'  : 'site_B_butt_C',
                'ycol'  : 'T_F',
                'conv'  : 'F_to_C',
                'style' : 'line',
                'axis'  : 1
                },
            'Manual measurements - top' : {
                'file'  : 'manual_data',
                'ycol'  : 'T_top_C',
                'conv'  : 'none',
                'style' : 'dots',
                'axis'  : 1
                },
            'Manual measurements - mid' : {
                'file'  : 'manual_data',
                'ycol'  : 'T_mid_C',
                'conv'  : 'none',
                'style' : 'dots',
                'axis'  : 1
                },
            'Manual measurements - bott' : {
                'file'  : 'manual_data',
                'ycol'  : 'T_bot_C',
                'conv'  : 'none',
                'style' : 'dots',
                'axis'  : 1
                }
            }
        },
    'light' : {
        'ytitle'    : 'Light intensity (lumen/ft2)',
        'ylim'      : 'auto',
        'datasets'  : {
            'Site A Button A (top)'     : {
                'file'  : 'site_A_butt_A',
                'ycol'  : 'lumen_sqft',
                'conv'  : 'lumft_to_lux',
                'style' : 'line',
                'axis'  : 1
                },
            'Site B Button B (top)'     : {
                'file'  : 'site_B_butt_B',
                'ycol'  : 'lumen_sqft',
                'conv'  : 'lumft_to_lux',
                'style' : 'line',
                'axis'  : 1
                },
            'Site B Button C (side)'     : {
                'file'  : 'site_B_butt_C',
                'ycol'  : 'lumen_sqft',
                'conv'  : 'lumft_to_lux',
                'style' : 'line',
                'axis'  : 1
                }
            }
        },
    'pressure'  : {
        'ytitle'    : 'Absolute pressure (in Hg)',
        'ylim'      : 'auto',
        'datasets'  : {
            'Site A Pendant'   : {
                'file'  : 'site_A_pend',
                'ycol'  : 'P_abs',
                'conv'  : 'none',
                'style' : 'line',
                'axis'  : 1
                },
            'Site B Pendant'   : {
                'file'  : 'site_B_pend',
                'ycol'  : 'P_abs',
                'conv'  : 'none',
                'style' : 'line',
                'axis'  : 1
                },
            }
        }
    }
    
# Datasets to draw from
dirpath = 'C:/Users/cariefrantz/Desktop/GSL Analysis'
files = {
    'elevation_Saltair'     : {
        'title'     : 'Elevation at Saltair (USGS)',
        'xcol'      : '20d',
        'datefmt'   : '%m/%d/%Y %H:%M',
        'fname'     : 'Elev_Saltair_071001-220925.csv'
        },
    'elevation_Causeway'    : {
        'title'     : 'Elevation S of RR causeway near Lakeside (USGS)',
        'xcol'      : '20d',
        'datefmt'   : '%m/%d/%Y %H:%M',
        'fname'     : 'Elev_Causeway_191028-221027.csv'
        },
    'site_A_pend'   : {
        'title'     : 'Site A Pendant',
        'xcol'      : 'Datetime',
        'datefmt'   : '%m/%d/%Y %H:%M',
        'fname'     : 'SiteB_Pendant_combined_QC.csv'
        },
    'site_A_butt_A' : {
        'title'     : 'Site A Button A (top)',
        'xcol'      : 'Datetime',
        'datefmt'   : '%m/%d/%Y %H:%M',
        'fname'     : 'SiteA_ButtonA_combined_QC.csv'
        },
    'site_B_pend'   : {
        'title'     : 'Site B Pendant',
        'xcol'      : 'Datetime',
        'datefmt'   : '%m/%d/%Y %H:%M',
        'fname'     : 'SiteB_Pendant_combined_QC.csv'
        },
    'site_B_butt_B' : {
        'title'     : 'Site B Button B (top)',
        'xcol'      : 'Datetime',
        'datefmt'   : '%m/%d/%Y %H:%M',
        'fname'     : 'SiteB_ButtonB_combined_QC.csv'
        },
    'site_B_butt_C' : {
        'title'     : 'Site B Button C (side)',
        'xcol'      : 'Datetime',
        'datefmt'   : '%m/%d/%Y %H:%M',
        'fname'     : 'SiteB_ButtonC_combined_QC.csv'
        },
    'manual_data'   : {
        'title'     : 'Manual field measurements',
        'xcol'      : 'Datetime',
        'datefmt'   : '%m/%d/%Y %H:%M',
        'fname'     : 'field_monitoring_data_fmttd_B.csv'
        }
    }
   
    
    
#%%
####################
# MAIN FUNCTION
####################
if __name__ == '__main__': 
    
    # Load in files
    dirpath = os.getcwd()
    for file in files:
        # Load in the file
        filename, dirpath, data = ResearchModules.fileGet(
            'Select file with data for ' + files[file]['title'],
            directory=dirpath)
        files[file]['data'] = data
    
    
    '''
    # !! COMMENT THIS PART OUT FOR NORMAL USE
    # Load in files from pre-defined filepaths
    print('Loading files...')
    for file in files:
        # Load in the file
        files[file]['data'] = pd.read_csv(dirpath+'/'+files[file]['fname'])
        
    #######
    '''
    
    # Plot figures
    for plot in plots:
        print('\nCreating ' + plot + ' figure ...')
        # Create a new figure
        fig, ax = plt.subplots(figsize=plotsize_default)
        legend=[]
    
        # Plot each dataset
        for var in plots[plot]['datasets']:
            print(' Plotting ' + var + '...')
            # Get the data
            file = plots[plot]['datasets'][var]['file']
            dset = files[file]['data'].copy()
            dset['ydata']=pd.to_numeric(
                dset[plots[plot]['datasets'][var]['ycol']],
                errors='coerce')
            if plots[plot]['datasets'][var]['conv']!='none':
                conv = getattr(
                    ResearchModules, plots[plot]['datasets'][var]['conv'])
                dset['ydata'] = conv(dset['ydata'])
                
                  
            # Plot the data
            # If specified, plot as a scatterplot
            if plots[plot]['datasets'][var]['style']=='dots':
                # Convert timestamps
                xdata = [
                    datetime.strptime(date, files[file]['datefmt'])
                    for date in dset[files[file]['xcol']]]
                
                # If secondary axis specified, create & plot on secondary axis
                if plots[plot]['datasets'][var]['axis']==2:
                    ax2=ax.twinx()
                    ax2=plt.scatter(xdata, dset['ydata'])
                    ax_sec = plt.gca()
                    ax_sec.set_ylabel(var)
                    ax_sec.set_ylim(plots[plot]['datasets'][var]['ylim'])
                    
                # Otherwise just plot
                else:
                    plt.scatter(xdata, dset['ydata'])
            
            # If scatterplot not specified, assume it's a line plot
            else:
                ResearchModules.plotData(
                    dset, files[file]['xcol'], 'ydata', 'Date',
                    plots[plot]['ytitle'], var, ax=ax,
                    plotsize=plotsize_default, smooth=True, xtype='datetime',
                    datefmt=files[file]['datefmt'])
                
                # Save the axis handle
                if plots[plot]['ylim']!='auto':
                    ax_pri = plt.gca()
            
            # Add to legend
            legend.append(var)
            
        # Add the legend
        if len(legend)>1:
            ax.legend(legend)
            
        # If specified, reset the limits of the y axis
        if plots[plot]['ylim']!='auto':
            ax_pri.set_ylim(plots[plot]['ylim'])
            
        # Show and save the figure          
        fig.show()
        fig.savefig(dirpath + '/' + plot + '.png')
        fig.savefig(dirpath + '/' + plot + '.svg')
        
    
    