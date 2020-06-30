# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 09:25:59 2020

@author: cariefrantz
"""

# Automate data addition from downloaded HOBO logs

'''
File sets:
    HOBO_SiteA.csv
    HOBO_SiteB.csv
    elevation_saltair.csv
'''
from datetime import datetime

import numpy as np
from matplotlib import pyplot as plt
from scipy import signal

import ResearchModules

# Daylight savings time?
# https://www.onsetcomp.com/support/tech-note/how-does-hobolink-and-rx3000-handle-changes-between-standard-and-daylight-savings




def calcDepth(water_pressure, air_pressure, density):
    gravity_factor = 9.80665
    depth = (water_pressure - air_pressure) * density / gravity_factor
    return depth
    
#%%
# Load file
filename, directory, data = ResearchModules.fileGet(
    'Select combined HOBO file', tabletype = 'HOBO')
# Delete nan rows
data = data.loc[data.index.dropna()]

# Get list of times
times = [datetime.strptime(dtime, '%m/%d/%Y %H:%M') for dtime in data.index]

# Density assumptions
# Site A
#min_density = 1.026
#max_density = 1.08
# Site B
min_density = 1.08
max_density = 1.106

# Calculate water depth
depth_min_density = calcDepth(
    data['water_pressure'], data['air_pressure_kPa'],  min_density)
depth_max_density = calcDepth(
    data['water_pressure'], data['air_pressure_kPa'], max_density)
differences = depth_max_density - depth_min_density
max_diff = np.nanmax(differences) * 100
mean_diff = np.nanmean(differences) * 100
print('Max: ' + str(round(max_diff,1)) + ' cm, ' +
      'Mean: ' + str(round(mean_diff,1)) + ' cm')

# Smooth signal for easier viewing

# Plot water depth at both sites
fig, axs = plt.subplots(1,2, figsize = (20, 8), sharex = True, sharey = True)
ResearchModules.plotTimeseries(
    axs[0], times, [depth_min_density, depth_max_density],
    y_label = 'Depth (m)',
    title = 'Calculated lake depth from HOBO logger data',
    legend = ['density = ' + str(min_density),
              'density = ' + str(max_density)])

axs[0].plot(times, depth_min_density, lw = 0.5)
axs[0].plot(times, depth_max_density, lw = 0.5)
axs[0].set_xlabel('Date')
axs[0].set_ylabel('Calculated water depth (m)\n'
                  + 'from water and air pressures measured by HOBO logger '
                  + 'and weather station')
axs[0].legend(['density = ' + str(min_density),
               'density = ' + str(max_density)])
axs[0].set_title('Difference in calculated water depth given different '
                 + 'assumptions for water density')
axs[1].fill_between(times, depth_min_density, depth_max_density)
axs[1].set_title('Max-Min depth: '
                 + 'max differnece = ' + str(round(max_diff,1)) + ' cm, '
                 + 'mean difference = ' + str(round(mean_diff,1)) + ' cm')
fig.savefig(directory + "\\test" + ".svg", transparent=True) # Save figure
