# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 17:23:01 2022

@author: cariefrantz
@project: GSLMO

Script compiles and summarizes GSL timeseries data, including elevation data
and HOBO logger data. The script requires files for all of the combined HOBO
logger data, plus Saltair & Causeway elevation files.

Elevation files need to have the header text removed, with header columns
    '20d' (timestamp in form %m/%d/%Y %H:%M)
    '14f' (elevation in ft asl)
HOBO files need to have columns renamed to
    'Datetime' (timestamp)
    T_F (temperature in degF)
    lumen_sqft (light in lumens per sqft)
    in_Hg (pressure in inches Hg)

"""

####################
# IMPORTS
####################
import ResearchModules
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

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

# Datasets to plot
dset_groups = {
    'elev' : {
        'ytitle' : 'Lake elevation (m asl)',
        'datasets' : {
            'elevation_Saltair' : {
                'file' : 'elevation_Saltair',
                'ycol' : '14n',
                'conv' : 'ft_to_m'
                },
            'elevation_Causeway' : {
                'file'  : 'elevation_Causeway',
                'ycol'  : '14n',
                'conv'  : 'ft_to_m'
                }
        }
    },
    'temp' : {
        'ytitle' : 'Temperature (' + chr(176) + 'C)',
        'datasets' : {
            'Site A Pendant' : {
                'file' : 'site_A_pend',
                'ycol' : 'T_C',
                'conv' : ''
                },
            'Site A Button A (top)' : {
                'file' : 'site_A_butt_A',
                'ycol' : 'T_F',
                'conv' : 'F_to_C'
                },
            'Site B Pendant' : {
                'file' : 'site_B_pend',
                'ycol' : 'T_C',
                'conv' : ''
                },
            'Site B Button B (top)' : {
                'file' : 'site_B_butt_B',
                'ycol' : 'T_F',
                'conv' : 'F_to_C'
                },
            'Site B Button C (side)' : {
                'file' : 'site_B_butt_C',
                'ycol' : 'T_F',
                'conv' : 'F_to_C'
                }
            }
        },
    'light' : {
            'ytitle' : 'Light intensity (lumen/ft2)',
            'datasets' : {
                'Site A Button A (top)' : {
                    'file' : 'site_A_butt_A',
                    'ycol' : 'lumen_sqft',
                    'conv' : 'lumsqft_to_lux'
                    },
                'Site B Button B (top)' : {
                    'file' : 'site_B_butt_B',
                    'ycol' : 'lumen_sqft',
                    'conv' : 'lumsqft_to_lux'
                    },
                'Site B Button C (side)' : {
                    'file' : 'site_B_butt_C',
                    'ycol' : 'lumen_sqft',
                    'conv' : 'lumsqft_to_lux'
                    }
                }
            },
    'pressure' : {
        'ytitle' : 'Absolute pressure (in Hg)',
        'datasets' : {
            'Site A Pendant' : {
                'file' : 'site_A_pend',
                'ycol' : 'P_abs',
                'conv' : ''
                },
            'Site B Pendant' : {
                'file' : 'site_B_pend',
                'ycol' : 'P_abs',
                'conv' : ''
                },
            }
        }
    }

# Files to draw from
files = {
    'elevation_Saltair' : {
        'title' : 'Elevation at Saltair (USGS)',
        'xcol'  : '20d',
        'datefmt' : '%m/%d/%Y %H:%M'
        },
    'elevation_Causeway' : {
        'title' : 'Elevation at Causeway (USGS)',
        'xcol'  : '20d',
        'datefmt'   : '%m/%d/%Y %H:%M'
        },
    'site_A_pend' : {
        'title' : 'Site A Pendant',
        'xcol'  : 'Datetime',
        'datefmt' : '%m/%d/%Y %H:%M'
        },
    'site_A_butt_A' : {
        'title' : 'Site A Button A (top)',
        'xcol'  : 'Datetime',
        'datefmt' : '%m/%d/%Y %H:%M'
        },
    'site_B_pend' : {
        'title' : 'Site B Pendant',
        'xcol'  : 'Datetime',
        'datefmt' : '%m/%d/%Y %H:%M'
        },
    'site_B_butt_B' : {
        'title' : 'Site B Button B (top)',
        'xcol'  : 'Datetime',
        'datefmt' : '%m/%d/%Y %H:%M'
        },
    'site_B_butt_C' : {
        'title' : 'Site B Button C (side)',
        'xcol'  : 'Datetime',
        'datefmt' : '%m/%d/%Y %H:%M'
        }
    }


####################
# SCRIPTS
####################
'''
def compileData(data):
    # Smooth to hourly if more frequent, else daily
    return compiled_data

def summarizeData(data, date_start, date_end):
    # Calculate min, max, avg with dates
    return data_summary

def plotData(data):
    # Build a timeseries plot

'''
def summarize_data(data, dt_range='all', time_col='index', ycol='ydata'):
    '''
    Summarizes timeseries data, determining:
        min & max values and dates they occurred
        median, average, and stdev
    
    Parameters
    ----------
    data : pandas.DataFrame
        Dataframe containing the data.
    dt_range : list, optional
        List containing two timestamps: [start, end]. The default is 'all',
        which analyzes all timestamps.
    time_col : string, optional
        Name of the column containing the timestamps.
        The default is 'index'
    ycol : string, optional
        Name of the column containing the y data. The default is 'ydata'.

    Returns
    -------
    data_summary : list
        List containing the following summary statistics
            1. min value
            2. date(s) when minimum was reached
            3. max value
            4. date(s) when max was reached
            5. median value
            6. average value
            7. standard deviation

    '''
    # Format the data
    if time_col=='index':
        df = pd.DataFrame(data[ycol])
    else:
        df = data[[time_col, ycol]].copy()
        df.set_index(time_col, inplace=True)
    
    # Calculate summary stats
    min_val = min(df[ycol])
    min_date = str(list(set([n.strftime('%Y-%m-%d')
                for n in list(df[df[ycol]==min_val].index)])))
    max_val = max(df[ycol])
    max_date = str(list(set([n.strftime('%Y-%m-%d')
                for n in list(df[df[ycol]==max_val].index)])))
    median = np.nanmedian(data[ycol])
    average = np.nanmean(data[ycol])
    stdev = np.std(data[ycol])
    
    return [min_val, min_date, max_val, max_date, median, average, stdev]

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
            'Select file with data for ' + files[file]['title'], directory=dirpath)
        files[file]['raw_data'] = data
        
    # Set up the summary
    data_summary = pd.DataFrame(
        columns=['Dataset','min_val','min_date','max_val','max_date','median',
                 'avg','stdev'])
    data_summary.set_index('Dataset',inplace=True)
    
    # Go through data groups and plot figures, generate summaries
    for dset in dset_groups:
        print('Building ' + dset + ' figure...')
        
        # Create a new figure
        fig, ax = plt.subplots(figsize=plotsize_default)
        legend=[]
        
        # Plot each line
        for var in dset_groups[dset]['datasets']:
            print ('   Processing ' + var + '...')
            # Get the data
            file = dset_groups[dset]['datasets'][var]['file']
            xcol = files[file]['xcol']
            ycol = dset_groups[dset]['datasets'][var]['ycol']
            data = files[file]['raw_data'][[xcol,ycol]].copy()
            convert = dset_groups[dset]['datasets'][var]['conv']
            
            # Format the data
            data.columns = ['Timestamp','ydata']
            print('      Converting timestamps for ' + var + '...')
            data['Timestamp'] = pd.to_datetime(data['Timestamp'])
            data['ydata'] = pd.to_numeric(data['ydata'], errors='coerce')
            data.set_index('Timestamp', inplace=True)
            
            # Resample the data to hourly values
            smoothed_hourly = data.resample('1H').mean()
            
            # Convert units if needed
            if convert:
                fctn = getattr(ResearchModules, convert)
                smoothed_hourly['ydata'] = [fctn(x)
                                            for x in smoothed_hourly['ydata']]
            
            # Summarize data
            smoothed_hourly.to_csv(dirpath + var + '_smoothed-hourly.csv')
            data_summary.loc[var] = summarize_data(smoothed_hourly)

            # Plot the data
            ResearchModules.plotData(smoothed_hourly, 'index', 'ydata',
                                     'Date', dset_groups[dset]['ytitle'], var,
                                     ax=ax, plotsize=plotsize_default,
                                     smooth=True, xtype='datetime',
                                     datefmt=files[file]['datefmt'])
            
            # Add to legend
            legend.append(var)
            
        # Add the legend
        if len(legend)>1:
            ax.legend(legend)
        
        # Show and save the figure
        fig.show()
        fig.savefig(dirpath + '/' + dset + '.png')
        fig.savefig(dirpath + '/' + dset + '.svg')
        
    # Save the data summary
    data_summary.to_csv(dirpath + '/' + 'timeseries_data_summary.csv')
