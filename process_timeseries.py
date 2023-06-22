# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 17:23:01 2022

@author: cariefrantz
@project: GSLMO

Script compiles and summarizes GSL timeseries data, including elevation data
and HOBO logger data. The script requires files for all of the combined HOBO
logger data, plus Saltair & Causeway elevation files.

Builds static plots and interactive (plotly) plots, as well as an HTML
dashboard containing the plotly plots.

Functions are in place to summarize the data, but they are buggy right now.

Elevation files need to have the header text removed, with header columns
    '20d' (timestamp in form %m/%d/%Y %H:%M)
    '14f' (elevation in ft asl)
HOBO files need to have columns renamed to:
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
import plotly.express as px
from datetime import date

####################
# VARIABLES
####################
# Plot default variables
plotsize_default = (12,6)
resample_interval = '1d'
smooth_interval = '7d'
div_pfx = 'plotly_'

# Formatting for datetime axis
years = mdates.YearLocator()
months = mdates.MonthLocator()
years_fmt = mdates.DateFormatter('%Y')

# Datasets to plot
dset_groups = {
    'elev' : {
        'title'     : 'Lake elevation',
        'ytitle'    : 'Lake elevation (m asl)',
        'datasets'  : {
            'elevation_Saltair' : {
                'file' : 'elevation_Saltair',
                'ycol' : '14n',
                'conv' : 'ft_to_m',
                'title': 'Saltair (USGS 1001000)'
                },
            'elevation_Causeway' : {
                'file'  : 'elevation_Causeway',
                'ycol'  : '14n',
                'conv'  : 'ft_to_m',
                'title' : 'Causeway (USGS 10010024)'
                }
        }
    },
    'temp' : {
        'title'     : 'Water temperature',
        'ytitle'    : 'Temperature (' + chr(176) + 'C)',
        'datasets'  : {
            'Site A Pendant' : {
                'file' : 'site_A_pend',
                'ycol' : 'T_C',
                'conv' : '',
                'title': 'Site A Pendant Logger'
                },
            'Site A Button A (top)' : {
                'file' : 'site_A_butt_A',
                'ycol' : 'T_F',
                'conv' : 'F_to_C',
                'title': 'Site A Button Logger - Top'
                },
            'Site B Pendant' : {
                'file' : 'site_B_pend',
                'ycol' : 'T_C',
                'conv' : '',
                'title': 'Site B Pendant Logger'
                },
            'Site B Button B (top)' : {
                'file' : 'site_B_butt_B',
                'ycol' : 'T_F',
                'conv' : 'F_to_C',
                'title': 'Site B Button Logger - Top'
                },
            'Site B Button C (side)' : {
                'file' : 'site_B_butt_C',
                'ycol' : 'T_F',
                'conv' : 'F_to_C',
                'title': 'Site B Button Logger - Side'
                }
            }
        },
    'light' : {
        'title'     : 'Light intensity (lux)',
        'ytitle'    : 'Light intensity (lux)',
        'datasets'  : {
            'Site A Button A (top)' : {
                'file' : 'site_A_butt_A',
                'ycol' : 'lumen_sqft',
                'conv' : 'lumft_to_lux',
                'title': 'Site A Downwelling'
                },
            'Site B Button B (top)' : {
                'file' : 'site_B_butt_B',
                'ycol' : 'lumen_sqft',
                'conv' : 'lumft_to_lux',
                'title': 'Site B Downwelling'
                },
            'Site B Button C (side)' : {
                'file' : 'site_B_butt_C',
                'ycol' : 'lumen_sqft',
                'conv' : 'lumft_to_lux',
                'title': 'Site B Sidewelling'
                }
            }
        },
    'pressure' : {
        'title'     : 'Pressure (proxy for water depth)',
        'ytitle'    : 'Absolute pressure (in Hg)',
        'datasets'  : {
            'Site A Pendant' : {
                'file' : 'site_A_pend',
                'ycol' : 'P_abs',
                'conv' : '',
                'title': 'Site A'
                },
            'Site B Pendant' : {
                'file' : 'site_B_pend',
                'ycol' : 'P_abs',
                'conv' : '',
                'title': 'Site B'
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

def loadFiles():
    '''
    Loads in the files for the dataset
    '''
    # Load in files
    dirpath = os.getcwd()
    for file in files:
        # Load in the file
        filename, dirpath, data = ResearchModules.fileGet(
            'Select file with data for ' + files[file]['title'], directory=dirpath)
        files[file]['raw_data'] = data
    
    return dirpath


def buildPlots(dirpath):
    
    # Build seperate plots for each variable measured
    for dset in dset_groups:
        print('Building plots for ' + dset + '...')
        varset = list(dset_groups[dset]['datasets'])
        # Merge timeseries into a single dataframe
        data = pd.DataFrame()
        for var in varset:
            print ('   Processing ' + var + '...')
            smoothed_hourly = formatConvertSmoothData(
                dset, var, dset_groups[dset]['datasets'][var]['title'])
            data = pd.concat([data, smoothed_hourly], axis = 1, join='outer')
            
        # Build static plot
        print('   Building static plot...')
        fig, ax = plt.subplots(1,1)
        for var in varset:
            ax.plot(
                data.index, data[dset_groups[dset]['datasets'][var]['title']],
                label = dset_groups[dset]['datasets'][var]['title'])
        ax.legend()
        plt.xlabel('Date')
        plt.ylabel(dset_groups[dset]['ytitle'])
        plt.show()
        fig.savefig(dirpath + '/' + dset + '.png')
        fig.savefig(dirpath + '/' + dset + '.svg')
        
        # Build interactive plot
        fig = px.line(data, x=data.index, y=data.columns, title = None,
                      labels = {
                                'Timestamp' : 'Date',
                                'value'     : dset_groups[dset]['ytitle'],
                                'variable'  : 'data source'
                                })
        fig.write_html(dirpath + '/' + div_pfx + dset + '.html', full_html=False)
        
        
def buildHTML(dirpath):
    print('Building HTML Dashboard...')
    
    # Set up HTML page
    html_head = ('''
    <!doctype html>
    <html>
    <head>
        <title>GSLMO Dashboard</title>
    </head>
    <body>
        <h1>Great Salt Lake Microbialite Observatory Dashboard</h1>
        <p>Environmental measurements for the GSLMO</p>
        <p>Plot by Dr. Carie Frantz, Department of Earth and Environmental Sciences, Weber State University
        <br />Created using Plotly for Python using the script <a href=""
        <br />Plot last upadted '''
        + date.today().strftime('%Y-%m-%d') + '</p>')

    html_body = ''
    html_foot = '''
    </body>
    </html>
    '''
    
    # Load in and append html figure div for each dataset
    for dset in dset_groups:
        # Load in and append html
        with open(dirpath + '/' + div_pfx + dset + '.html', 'r', encoding = 'UTF-8') as file:
            div_html = file.read()
        html_body = (
            html_body + '\n'
            + '<h1>' + dset_groups[dset]['title'] + '</h1>'
            + '\n'   + div_html)
        
    # Write the combined HTML file
    html_fullpage = html_head + '\n' + html_body + '\n' + html_foot
    with open(
            dirpath + '/' + 'GSLMO_dashboard.html','wt',
            encoding='utf-8') as file:
        file.write(html_fullpage)
    
    

def formatConvertSmoothData(dset, var, ycol_name):
    # Get the data
    file = dset_groups[dset]['datasets'][var]['file']
    xcol = files[file]['xcol']
    ycol = dset_groups[dset]['datasets'][var]['ycol']
    data = files[file]['raw_data'][[xcol,ycol]].copy()
    convert = dset_groups[dset]['datasets'][var]['conv']
    
    # Format the data
    data.columns = ['Timestamp', ycol_name]
    print('      Converting timestamps for ' + var + '...')
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])
    data[ycol_name] = pd.to_numeric(data[ycol_name], errors='coerce')
    data.set_index('Timestamp', inplace=True)
    
    # Resample the data to hourly values
    smoothed_hourly = data.resample('1H').mean()
    
    # Convert units if needed
    if convert:
        fctn = getattr(ResearchModules, convert)
        smoothed_hourly[ycol_name] = [fctn(x)
                                    for x in smoothed_hourly[ycol_name]]
        
    return smoothed_hourly



def buildSummaries(dirpath):
    '''
    Creates static plots, interactive (plotly) plots, and a data sumamry

    Parameters
    ----------
    dirpath : str
        Base directory where files are stored and saved.

    Returns
    -------
    None.

    '''
    # Set up the summary
    data_summary = pd.DataFrame(
        columns=['Dataset','min_val','min_date','max_val','max_date','median',
                 'avg','stdev'])
    data_summary.set_index('Dataset',inplace=True)
    
    # Go through data groups and plot static figures, generate summaries
    for dset in dset_groups:
        print('Building ' + dset + ' figure...')
        
        # Create a new static figure
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
            data_summary.to_csv(
                dirpath + '/timeseries_data_summary_' + dset + '_' + var
                + '.csv')

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
   
    # Load files
    dirpath = loadFiles()
    # Build the summary plots
    buildPlots(dirpath)
    # Build the interactive plot HTML page
    buildHTML(dirpath)
    

    
