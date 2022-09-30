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
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from datetime import timedelta
from scipy.interpolate import make_interp_spline


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
def smooth_timeseries_data(data, valcol, resample_interval=resample_interval,
                           smooth_interval=smooth_interval):
    
    # Create the trimmed dataframe
    df = pd.DataFrame(data=data[valcol])
    df['Timestamp'] = df.index.to_pydatetime()
    df.set_index('Timestamp', inplace=True)
    
    # Summarize by date
    df_resampled=pd.DataFrame()
    df_resampled['mean'] = df.resample(resample_interval).mean()
    df_resampled['median'] = df.resample(resample_interval).median()
    df_resampled['min'] = df.resample(resample_interval).min()
    df_resampled['max'] = df.resample(resample_interval).max()

    
    # Moving average
    df_resampled['SMA'] = df_resampled['mean'].rolling(smooth_interval).mean()
    
    return df_resampled



def plotData(data, xcol, ycol, xlabel, ylabel, title, ax = [],
             plotsize=plotsize_default, smooth=False, savefig=False,
             xtype='general', datefmt='%m/%d/%y %H:%M'):
    '''
    Plots x,y data as a line plot, saves as png and svg.

    Parameters
    ----------
    data : pd.DataFrame
        Table containing the x and y data
    xcol : str
        Name of the dataframe column containing the x data
    ycol : str
        Name of the dataframe column containing the y data
    xlabel : str
        X axis label for the plot
    ylabel : str
        Y axis label for the plot
    title : str
        Plot title for filename
    ax : matplotlib._subplots.AxesSubplot. The default is []
        Pass a subplot axes handle if a subplot already exists that the plot
        should be added to. The default creates a new plot.
    plotsize : tuple, optional
        Size of the plot (w, ht). The default is (12,6).
    smooth : bool, optional
        Whether or not to perform data smoothing. The default is False.
    xtype : str, optional
        Type of x-axis data. The default is 'general'.
        Options:
            'general'   : For non-timeseries x values
            'datetime'  : For timeseries x values
    datefmt : str, optional
        Datetime format in the table. Required if xtype == datetime.
        The default is '%m/%d/%y %H:%M'.

    Returns
    -------
    None.

    '''
    # Default fig
    fig=[]

    # Select columns
    xdata = data[xcol].values 
    ydata = data[ycol].values
    
    # Convert timeseries data
    if xtype=='datetime':
        xdata = [datetime.strptime(date, datefmt) for date in xdata]
    else:
        xdata = pd.to_numeric(ydata, errors='coerce')
    
    # Format y data
    ydata = pd.to_numeric(ydata, errors='coerce')

    # Perform smoothing    
    if smooth==True:
        if xtype=='general':
            spline = make_interp_spline(xdata, ydata)
            xdata = np.linspace(xdata.min(), xdata.max(), 500)
            ydata = spline(xdata)
        
        # For datetime x, smooth data by moving average    
        if xtype=='datetime':
            df = pd.DataFrame(data=ydata,index=xdata,columns=['y'])
            smoothed = smooth_timeseries_data(df, 'y')
            ydata = smoothed['SMA'].values
            xdata = smoothed.index
            
            #y_df = pd.DataFrame(
            #    data = ydata, index = xdata, columns = ['y'], copy = True)
            #y_df = y_df[~y_df.index.duplicated()]
            #y_df = y_df.resample('1T').interpolate(
            #    'index', limit=20, limit_area = 'inside').resample(
            #        '7d').asfreq().dropna()
            # Determine weekly min/max values
            #minmax = y_df.resample('7d')['y'].agg(['min','max'])
            #ydata = y_df['y'].values
            #xdata = list(y_df.index)
    
    # Build new figure if no subplot exists
    if not ax:
        fig, ax = plt.subplots(figsize=plotsize)
        
    # Build plot
    ax.plot(xdata, ydata)
    ax.set(xlabel=xlabel, ylabel=ylabel)
    
    if xtype=='datetime':
        # Prettify datetime axis
        ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(years_fmt)
        ax.xaxis.set_minor_locator(months)
        
        # Round to nearest years
        datemin = pd.to_datetime(xdata[0].year, format='%Y')
        datemax = pd.to_datetime((xdata[-1] + timedelta(days=365)).year, format='%Y')
        ax.set_xlim(datemin, datemax)
    
    # Export plot
    if savefig:
        if fig:
            fig.show()
            fig.savefig(title + '.png')
            fig.savefig(title + '.svg')
        else:
            print('''Error: Trying to save a partial figure in PlotData.
If your plot has only one line, leave the ax value to default (ax=[]).
If you are plotting multiple lines, you will need to save the figure outside
the PlotData function.''')
    
    
    
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
            plotData(data, datasets[var]['xcol'], datasets[var]['ycol'],
                     'Date', plots[plot]['ytitle'], datasets[var]['title'],
                     ax=ax, plotsize=plotsize_default, smooth=True,
                     xtype='datetime', datefmt=datasets[var]['datefmt'])
            
            # Add to legend
            legend.append(datasets[var]['title'])
            
        # Add the legend
        if len(legend)>1:
            ax.legend(legend)
            
        # Show and save the figure          
        fig.show()
        fig.savefig(plot + '.png')
        fig.savefig(plot + '.svg')
        
    
    