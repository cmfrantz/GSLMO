# -*- coding: utf-8 -*-
"""precip_totals
Created on Sat Nov 12 15:14:58 2022

@author: cariefrantz
"""

####################
# IMPORTS
####################

import ResearchModules
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


####################
# VARIABLES
####################

# Plot default variables
plotsize_default = (12, 6)

# Stations
stations = ['KUTSYRAC22', 'KUTSYRAC27']
precip_col = 'Precip. Accum. (in)'

# Formatting for datetime axis
years = mdates.YearLocator()
months = mdates.MonthLocator()
years_fmt = mdates.DateFormatter('%Y')
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

# %%
####################
# MAIN FUNCTION
####################
if __name__ == '__main__':
    # Import weather data files
    filename, dirpath, data = ResearchModules.fileGet(
        'Select file with merged weather data from both stations (csv)')
    
    # Format timestamp
    data.index = pd.to_datetime(data.index, errors='coerce')
    
    # Resample to daily grabbing precip accum. max
    data_cols = [col for col in data.columns if precip_col in col]
    daily_data = data[data_cols].resample('1d').max()
    
    # Convert in to cm
    data_conv_cols = [col.replace('in','cm') for col in data_cols]
    daily_data[data_conv_cols] = ResearchModules.inch_to_cm(daily_data)
    
    # Save data
    daily_data.to_csv(dirpath + '/daily_precip.csv')
    
    # Plot daily rain
    fig, ax = plt.subplots(figsize=plotsize_default)
    legend = []
    for n, station in enumerate(stations):
        ResearchModules.plotData(
            daily_data, 'index', data_conv_cols[n], 'Date',
            'Accumulated precip. (cm)', 'Precipitation', ax=ax,
            xtype='datetime', datefmt='%m/%d/%Y %H:%M:%S')
        legend.append(station)
    ax.legend(legend)
    # Show and save the figure
    fig.show()
    fig.savefig(dirpath + '/daily_precip.png')
    fig.savefig(dirpath + '/daily_precip.svg')
    
    # Calc sum for each date range
    date_sums = pd.DataFrame(
        index=list(range(len(date_ranges))),
        columns=['date_start','date_end','sum','avg','stdev'])
    for n,dates in enumerate(date_ranges):
        date_sums.loc[n,'date_start'] = dates[0]
        date_sums.loc[n,'date_end'] = dates[1]
        date_sums.loc[n,'sum'] = daily_data.loc[dates[0]:dates[1]]['avg_' + precip_col].sum()
        date_sums.loc[n,'avg'] = daily_data.loc[dates[0]:dates[1]]['avg_' + precip_col].mean()
        date_sums.loc[n,'stdev'] = daily_data.loc[dates[0]:dates[1]]['avg_' + precip_col].std()
    date_sums.to_csv(dirpath + '/precip_stats.csv')
