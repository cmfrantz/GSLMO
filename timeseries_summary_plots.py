#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Carie Frantz'
__email__ = 'cariefrantz@weber.edu'
"""timeseries_summary_plots
Created on Fri Sep 30 10:12:33 2022

@author: cariefrantz
@project: GSLMO

Script compiled GSL timeseries data, including elevation data and
HOBO logger data, summarizes it for different time periods, and plots it.

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
# Delete temporary variables with filepaths
# Comment out code to find files from filepaths


####################
# IMPORTS
####################

import ResearchModules
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
# from datetime import datetime


####################
# VARIABLES
####################

# Plot default variables
plotsize_default = (12, 4)

# Formatting for datetime axis
years = mdates.YearLocator()
months = mdates.MonthLocator()
years_fmt = mdates.DateFormatter('%Y')
plot_date_range = ['2019-01-01', '2023-01-01']
date_ranges = [
    ['2019-03-01', '2022-10-20'],
    ['2019-07-01', '2019-08-31'],
    ['2020-07-01', '2020-08-31'],
    ['2021-07-01', '2021-08-31'],
    ['2021-07-21', '2021-08-12'],
    ['2021-09-27', '2021-11-12'],
    ['2022-07-01', '2022-08-31'],
    ['2022-07-12', '2022-08-02'],
    ['2022-07-12', '2022-10-20']
]

# Plots to generate
plots = {
    'elev': {
        'ytitle': 'Lake elevation (m asl)',
        'ylim': [1276, 1279],
        'datasets': {
            'elevation at Saltair': {
                'file': 'elevation_Saltair',
                'ycol': '14n',
                'conv': 'ft_to_m',
                'style': 'line',
                'axis': 1,
                },
            'elevation at Causeway': {
                'file': 'elevation_Causeway',
                'ycol': '14n',
                'conv': 'ft_to_m',
                'style': 'line',
                'axis': 1
                },
            'Water depth measured at Site B (m)': {
                'file': 'manual_data',
                'ycol': 'water_depth_m',
                'conv': 'none',
                'style': 'dots',
                'axis': 2,
                'ylim': [-1.25, 1.75]
                }
            }
        },
    'depth': {
        'ytitle': 'Water depth (m)',
        'ylim': 'auto',
        'datasets': {
            'Site B': {
                'file': 'site_depths',
                'ycol': 'depth_B',
                'conv': 'none',
                'style': 'line',
                'axis': 1
                },
            'Site B3': {
                'file': 'site_depths',
                'ycol': 'depth_B3',
                'conv': 'none',
                'style': 'line',
                'axis': 1
                },
            'Manual measurements': {
                'file': 'manual_data',
                'ycol': 'water_depth_m',
                'conv': 'none',
                'style': 'dots',
                'axis': 1
                }
            }
        },
    'temp_all': {
        'ytitle': 'Temperature (' + chr(176) + 'C)',
        'ylim': 'auto',
        'datasets': {
            'Site A Pendant': {
                'file': 'site_A_pend',
                'ycol': 'T_C',
                'conv': 'none',
                'style': 'line',
                'axis': 1
                },
            'Site A Button A (top)': {
                'file': 'site_A_butt_A',
                'ycol': 'T_F',
                'conv': 'F_to_C',
                'style': 'line',
                'axis': 1
                },
            'Site B Pendant': {
                'file': 'site_B_pend',
                'ycol': 'T_C',
                'conv': 'none',
                'style': 'line',
                'axis': 1
                },
            'Site B Button B (top)': {
                'file': 'site_B_butt_B',
                'ycol': 'T_F',
                'conv': 'F_to_C',
                'style': 'line',
                'axis': 1
                },
            'Site B Button C (side)': {
                'file': 'site_B_butt_C',
                'ycol': 'T_F',
                'conv': 'F_to_C',
                'style': 'line',
                'axis': 1
                },
            'Manual measurements - top': {
                'file': 'manual_data',
                'ycol': 'T_top_C',
                'conv': 'none',
                'style': 'dots',
                'axis': 1
                },
            'Manual measurements - mid': {
                'file': 'manual_data',
                'ycol': 'T_mid_C',
                'conv': 'none',
                'style': 'dots',
                'axis': 1
                },
            'Manual measurements - bott': {
                'file': 'manual_data',
                'ycol': 'T_bot_C',
                'conv': 'none',
                'style': 'dots',
                'axis': 1
                }
            }
        },
    'temp_B': {
        'ytitle'    : 'Temperature (C)',
        'ylim'      :     'auto',
        'datasets'  : {
            'Site B Pendant': {
                'file': 'site_B_pend',
                'ycol': 'T_C',
                'conv': 'none',
                'style': 'line',
                'axis': 1
                },
            'Site B Button B (top)': {
                'file': 'site_B_butt_B',
                'ycol': 'T_F',
                'conv': 'F_to_C',
                'style': 'line',
                'axis': 1
                },
            'Site B Button C (side)': {
                'file': 'site_B_butt_C',
                'ycol': 'T_F',
                'conv': 'F_to_C',
                'style': 'line',
                'axis': 1
                },
            'KUTSYRAC22' : {
                'file': 'KUTSYRAC22',
                'ycol': 'Temperature (F)',
                'conv': 'F_to_C',
                'style': 'line',
                'axis': 1
                },
            'KUTSYRAC27' : {
                'file': 'KUTSYRAC27',
                'ycol': 'Temperature (F)',
                'conv': 'F_to_C',
                'style': 'line',
                'axis': 1
                },
            'Manual measurements - top': {
                'file': 'manual_data',
                'ycol': 'T_top_C',
                'conv': 'none',
                'style': 'dots',
                'axis': 1
                },
            'Manual measurements - mid': {
                'file': 'manual_data',
                'ycol': 'T_mid_C',
                'conv': 'none',
                'style': 'dots',
                'axis': 1
                },
            'Manual measurements - bott': {
                'file': 'manual_data',
                'ycol': 'T_bot_C',
                'conv': 'none',
                'style': 'dots',
                'axis': 1
                }
            }
        },
    'Precip': {
        'ytitle' : 'Accumulated daily precipitation (cm)',
        'ylim' : 'auto',
        'datasets' : {
            'KUTSYRAC22' : {
                'file': 'KUTSYRAC22',
                'ycol': 'Precip. Accum. (in)',
                'conv': 'inch_to_cm',
                'style': 'line',
                'axis': 1
                },
            'KUTSYRAC27' : {
                'file': 'KUTSYRAC27',
                'ycol': 'Precip. Accum. (in)',
                'conv': 'inch_to_cm',
                'style': 'line',
                'axis': 1
                }
            }
        },
    'light': {
        'ytitle': 'Light intensity (lux)',
        'ylim': 'auto',
        'datasets': {
            'Site A Button A (top)': {
                'file': 'site_A_butt_A',
                'ycol': 'lumen_sqft',
                'conv': 'lumft_to_lux',
                'style': 'line',
                'axis': 1
                },
            'Site B Button B (top)': {
                'file': 'site_B_butt_B',
                'ycol': 'lumen_sqft',
                'conv': 'lumft_to_lux',
                'style': 'line',
                'axis': 1
                },
            'Site B Button C (side)': {
                'file': 'site_B_butt_C',
                'ycol': 'lumen_sqft',
                'conv': 'lumft_to_lux',
                'style': 'line',
                'axis': 1
                }
            }
        },
    'pressure': {
        'ytitle': 'Absolute pressure (in Hg)',
        'ylim': 'auto',
        'datasets': {
            'Site A Pendant': {
                'file': 'site_A_pend',
                'ycol': 'P_abs',
                'conv': 'none',
                'style': 'line',
                'axis': 1
                },
            'Site B Pendant': {
                'file': 'site_B_pend',
                'ycol': 'P_abs',
                'conv': 'none',
                'style': 'line',
                'axis': 1
                },
            }
        },
    'salinity': {
        'ytitle': 'Salinity (%)',
        'ylim': 'auto',
        'datasets': {
            'Water surface': {
                'file': 'manual_data',
                'ycol': 'Water surface.5',
                'conv': 'none',
                'style': 'dots',
                'axis': 1
                },
            'Mid': {
                'file': 'manual_data',
                'ycol': 'Mid (if diff. from max vis).4',
                'conv': 'none',
                'style': 'dots',
                'axis': 1
                },
            'MVD': {
                'file': 'manual_data',
                'ycol': 'Max visible depth.5',
                'conv': 'none',
                'style': 'dots',
                'axis': 1
                },
            'Sed-water interface': {
                'file': 'manual_data',
                'ycol': 'Sed/water interface.5',
                'conv': 'none',
                'style': 'dots',
                'axis': 1
                }
            }
        }
    }

# Datasets to draw from
dirpath = (
    'G:/My Drive/Teaching, Research, Etc/Research/Great Salt Lake/' + 
    '2022 Microbialite Desiccation Bio Paper/Timeseries Field & Logger Data')
files = {
    'elevation_Saltair': {
        'title': 'Elevation at Saltair (USGS)',
        'xcol': '20d',
        'datefmt': '%m/%d/%Y %H:%M',
        'fname': 'Elev_Saltair_071001-220925.csv'
        },
    'elevation_Causeway': {
        'title': 'Elevation S of RR causeway near Lakeside (USGS)',
        'xcol': '20d',
        'datefmt': '%m/%d/%Y %H:%M',
        'fname': 'Elev_Causeway_191028-221027.csv'
        },
    'site_A_pend': {
        'title': 'Site A Pendant',
        'xcol': 'Datetime',
        'datefmt': '%m/%d/%Y %H:%M',
        'fname': 'SiteB_Pendant_combined_QC.csv'
        },
    'site_A_butt_A': {
        'title': 'Site A Button A (top)',
        'xcol': 'Datetime',
        'datefmt': '%m/%d/%Y %H:%M',
        'fname': 'SiteA_ButtonA_combined_QC.csv'
        },
    'site_B_pend': {
        'title': 'Site B Pendant',
        'xcol': 'Datetime',
        'datefmt': '%m/%d/%Y %H:%M',
        'fname': 'SiteB_Pendant_combined_QC.csv'
        },
    'site_B_butt_B': {
        'title': 'Site B Button B (top)',
        'xcol': 'Datetime',
        'datefmt': '%m/%d/%Y %H:%M',
        'fname': 'SiteB_ButtonB_combined_QC.csv'
        },
    'site_B_butt_C': {
        'title': 'Site B Button C (side)',
        'xcol': 'Datetime',
        'datefmt': '%m/%d/%Y %H:%M',
        'fname': 'SiteB_ButtonC_combined_QC.csv'
        },
    'manual_data': {
        'title': 'Manual field measurements',
        'xcol': 'Datetime',
        'datefmt': '%m/%d/%Y %H:%M',
        'fname': 'field_monitoring_data_fmttd_B.csv'
        },
    'site_depths': {
        'title': 'Calculated field site depths',
        'xcol': '20d',
        'datefmt': '%m/%d/%Y',
        'fname': 'daily_site_depth_calc.csv'
        },
    'KUTSYRAC22': {
        'title': 'KUTSYRAC22 weather station data',
        'xcol': 'Time',
        'datefmt': '%m/%d/%Y %H:%M',
        'fname': 'KUTSYRAC22_190301-201122.csv'
        },
    'KUTSYRAC27': {
        'title': 'KUTSYRAC27 weather station data',
        'xcol': 'Time',
        'datefmt': '%m/%d/%Y %H:%M',
        'fname': 'KUTSYRAC27_200901-221106.csv'
        },
}


####################
# FUNCTIONS
####################
def load_files(filelist='auto', files=files, dirpath=dirpath):
    '''
    Loads in all of the timeseries files

    Parameters
    ----------
    filelist : str, optional
        'GUI' asks the user to find each file.
        'auto' pulls files in automatically from filepaths stored as global
            variables. The default is 'auto'.
    files : dict of dict, optional
        dict containing sub-duct fo reach file to load, which each include
        information needed to load in the file. The default is files, which
        is defined in the global variables.
    dirpath : str, optional
        Directory where files are stored. The default is the dirpath defined
        in the global variables.

    Returns
    -------
    files : dict of dicts
        Adds imported data to each file set stored in the 'files' variable.

    '''
    if filelist == 'auto':
        # Load in files from pre-defined filepaths
        print('Loading files...')
        for file in files:
            # Load in the file
            print('Loading file for ' + file + '...')
            files[file]['data'] = pd.read_csv(dirpath+'/'+files[file]['fname'])

    else:
        # Load in files by asking user to find them
        for file in files:
            # Load in the file
            filename, dirpath, data = ResearchModules.fileGet(
                'Select file with data for ' + files[file]['title'],
                directory=dirpath)
            files[file]['data'] = data

    # Get list of y_cols
    y_col_list = []
    for plot in plots:
        for var in plots[plot]['datasets']:
            if plots[plot]['datasets'][var]['ycol'] not in y_col_list:
                y_col_list.append(plots[plot]['datasets'][var]['ycol'])

    # Prep data
    # Convert timestamps
    for file in files:
        print('Converting timestamps for ' + file + '...')
        files[file]['data'].index = pd.to_datetime(
            files[file]['data'][files[file]['xcol']], errors='coerce')

    # Convert data
    for plot in plots:
        for var in plots[plot]['datasets']:
            print('Converting data for ' + plot + ' ' + var + '...')
            data = files[plots[plot]['datasets'][var]['file']]['data'][
                plots[plot]['datasets'][var]['ycol']].copy()
            # Convert to numeric
            data = pd.to_numeric(data, errors='coerce')
            # Convert units
            if plots[plot]['datasets'][var]['conv'] != 'none':
                conv = getattr(
                    ResearchModules, plots[plot]['datasets'][var]['conv'])
                data = conv(data)
            files[plots[plot]['datasets'][var]['file']]['data'][
                plots[plot]['datasets'][var]['ycol'] + '_conv'] = data.copy()

    return files, dirpath


def plot_timeseries(data_files, plots=plots, dirpath=dirpath):
    '''
    Plots all of the timeseries specified in plots variable

    Parameters
    ----------
    data_files : dict of dicts
        dict of different files, each file dict containing data to plot.
        This is generated by load_files.
    plots : dict of dicts, optional
        dict containing a list of plots to generate. The default is plots,
        which is defined in the global variables.
    dirpath : str
        Directory path for saving figures. The default is dirpath, which was
        defined in the global variables.

    Returns
    -------
    None.

    '''
    # Plot figures
    for plot in plots:
        print('\nCreating ' + plot + ' figure ...')
        # Create a new figure
        fig, ax = plt.subplots(figsize=plotsize_default)
        legend = []

        # Plot each dataset
        for var in plots[plot]['datasets']:
            print(' Plotting ' + var + '...')
            # Get the data
            file = plots[plot]['datasets'][var]['file']
            dset = data_files[file]['data'].copy()
            dset['ydata'] = dset[
                plots[plot]['datasets'][var]['ycol'] + '_conv']
            dset['dt'] = data_files[file]['data'].index

            # Plot the data
            # If specified, plot as a scatterplot
            if plots[plot]['datasets'][var]['style'] == 'dots':

                # If secondary axis specified, create & plot on secondary axis
                if plots[plot]['datasets'][var]['axis'] == 2:
                    ax2 = ax.twinx()
                    ax2 = plt.scatter(dset['dt'], dset['ydata'])
                    ax_sec = plt.gca()
                    ax_sec.set_ylabel(var)
                    ax_sec.set_ylim(plots[plot]['datasets'][var]['ylim'])

                # Otherwise just plot
                else:
                    plt.scatter(dset['dt'], dset['ydata'])

            # If scatterplot not specified, assume it's a line plot
            else:
                ResearchModules.plotData(
                    dset, 'dt', 'ydata', 'Date',
                    plots[plot]['ytitle'], var, ax=ax,
                    plotsize=plotsize_default, smooth=True, xtype='datetime',
                    datefmt=files[file]['datefmt'])

                # Save the axis handle
                if plots[plot]['ylim'] != 'auto':
                    ax_pri = plt.gca()

            # Add to legend
            legend.append(var)

        # Add the legend
        if len(legend) > 1:
            ax.legend(legend)
            
        # Set the limits of the x axis
        # !! This isn't working!
        # ax_pri.set_xlim(plot_date_range)

        # If specified, reset the limits of the y axis
        if plots[plot]['ylim'] != 'auto':
            ax_pri.set_ylim(plots[plot]['ylim'])

        # Show and save the figure
        fig.show()
        fig.savefig(dirpath + '/' + plot + '.png')
        fig.savefig(dirpath + '/' + plot + '.pdf', transparent=True)


def summarize_timeseries(data_files, plots=plots, date_ranges=date_ranges,
                         dirpath=dirpath):
    '''
    Summarizes the timeseries collections generated by load_files,
    saves summaries in an Excel file.

    Parameters
    ----------
    data_files : dict of dicts
        This is the output of load_files.
    plots : dict of dicts, optional
        List of data sets (plots). The default is plots, which is defined
        in the global variables.
    date_ranges : list of lists, optional
        List of [start date, end date] as strings. The default is date_ranges,
        which is defined in the global variables.
    directory : str, optional
        Directory path for saving the Excel file. The default is dirpath,
        which was defined in the global variables.

    Returns
    -------
    None.

    '''
    # For each timeseries, generate a summary for each dataset
    summaries = {}
    for plot in plots:
        for var in plots[plot]['datasets']:
            # Generate summary
            print('Generating summary for ' + plot + ': ' + var + '...')
            summary = pd.DataFrame(index = list(range(len(date_ranges))),
                                   columns = ['date_start', 'date_end',
                                              'min', 'min_dates',
                                              'max', 'max_dates',
                                              'avg', 'stdev', 'median'])
            # Loop through each date series
            for n, dates in enumerate(date_ranges):
                # Snip date range
                summary.loc[n,['date_start','date_end']] = dates
                d_sub = (
                    data_files[plots[plot]['datasets'][var]['file']]['data']
                    [plots[plot]['datasets'][var]['ycol']+'_conv'].to_frame())
                d_sub = d_sub[dates[0]:dates[1]]
                
                # Find min & min date
                min_val = d_sub.min()[0]
                summary.iloc[n]['min'] = min_val
                datelist = (
                    d_sub[d_sub[plots[plot]['datasets'][var]['ycol']
                                + '_conv'] == min_val].resample(
                                    '1D').mean().index)
                summary.iloc[n]['min_dates'] = ', '.join(
                    datelist.strftime('%Y-%m-%d'))
                
                # Find max & max date
                max_val = d_sub.max()[0]
                summary.iloc[n]['max'] = max_val
                datelist = (
                    d_sub[d_sub[plots[plot]['datasets'][var]['ycol']
                                + '_conv'] == max_val].resample(
                                    '1D').mean().index)
                summary.iloc[n]['max_dates'] = ', '.join(
                    datelist.strftime('%Y-%m-%d'))
    
                # Find avg, stdev, & median
                summary.iloc[n]['avg'] = float(d_sub.mean())
                summary.iloc[n]['stdev'] = float(d_sub.std())
                summary.iloc[n]['median'] = float(d_sub.median())
                
            summaries[plot + ' ' + var] = summary
    
    # Write summaries to Excel
    writer = pd.ExcelWriter(dirpath + '/timeseries_summary.xlsx')
    for summary in summaries:
        print('Saving ' + summary + 'summary...')
        if len(summary)<30:
            summaries[summary].to_excel(writer, sheet_name = summary)
        else:
            summaries[summary].to_excel(writer, sheet_name=summary[0:30])
    writer.save()
    writer.close()
            
        
                
                
                


# %%
####################
# MAIN FUNCTION
####################
if __name__ == '__main__':
    # This version pulls in files defined in the global variables
    data_files, dirpath = load_files()
    '''This version asks for user-specified files
    data_files = load_files(filelist='GUI', dir=os.get_cwd())
    '''
    plot_timeseries(data_files)
    summarize_timeseries(data_files)
