#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Carie Frantz'
__email__ = 'cariefrantz@weber.edu'
"""DensityDiff
Created on Wed Jun 24 09:25:59 2020
@author: cariefrantz
@project: GSLMO

Determines relative influence of density assumptions on calculated lake depth
from HOBO logger water pressure data and weather station air pressure data.

This script was created as part of the
Great Salt Lake Microbialite Observatory project

Arguments:  None

Requirements:
    HOBO_SiteA.csv
    HOBO_SiteB.csv

Example in command line:
    python DensityDiff.py

Dependencies Install:
    sudo apt-get install python3-pip python3-dev
    pip install datetime
    pip install numpy
    pip install matplotlib

You will also need to have the following files
    in the same directory as this script.
They contain modules and variables that this script calls.
    ResearchModules.py
If you get an error indicating that one of these modules is not found,
    change the working directory to the directory containing these files.


Copyright (C) 2020  Carie M. Frantz

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
# IMPORTS
####################

from datetime import datetime

import numpy as np
from matplotlib import pyplot as plt

import ResearchModules

# Daylight savings time?
# https://www.onsetcomp.com/support/tech-note/how-does-hobolink-and-rx3000-handle-changes-between-standard-and-daylight-savings



#%%
####################
# MAIN FUNCTION
####################
if __name__ == '__main__':    
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
    depth_min_density = ResearchModules.calcDepth(
        data['water_pressure'], data['air_pressure_kPa'],  min_density)
    depth_max_density = ResearchModules.calcDepth(
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
