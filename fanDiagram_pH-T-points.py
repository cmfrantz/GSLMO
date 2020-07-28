#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Carie Frantz'
__email__ = 'cariefrantz@weber.edu'
"""Saturation Plot T-pH
Created on Mon Jul 27 12:46:47 2020
@author: cariefrantz
@project: GSLMO

DESCRIPTION blablabla

This script was created as part of the
Great Salt Lake Microbialite Observatory project

Arguments:  None

Requirements:
    PHREEQC-Out.csv
    GSL_FieldData.csv

Example in command line:
    python scriptname.py

Dependencies Install:
    sudo apt-get install python3-pip python3-dev
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
import ResearchModules

import numpy as np
import pandas as pd
from scipy import interpolate
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.dates as mdates
# This tells matplotlib to save text in a format that Adobe Illustrator can read
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42


####################
# VARIABLES
####################

# VARIABLES TO PLOT
Alk = 7
col_Alk = 'Alk(meq/kg)'
Ca = 200
col_Ca = '[Ca](mg/kg)'
TDS = 120
col_TDS = 'TDS(ppt)'
col_T = 'T(C)'
col_T_field = 'Water T (C).1'
col_pH = 'pH'
col_pH_field = 'Water above core.2'

# FAN DIAGRAM FORMATTING OPTIONS
cmap_fan = 'RdBu_r' # Colormap to use for fan diagram (background)
cmap_date = 'plasma' # Colormap for date points
# Boundaries for the plot color key (omega values)
clrbounds = 'Calc'  # Calculate colorbounds from the values provided below
omega_min = 1E-3    # Min value for the colormap
omega_max = 1000    # Max value for the colormap
# Or a list of boundary values can be given
cbar_num_format = '%g'  # Text format for the colorbar
mkr_shape = {
    'A'     : '^',
    'B'     : 'o'
    }

####################
# FUNCTIONS
####################



#%%
####################
# MAIN FUNCTION
####################
if __name__ == '__main__':
    
    # IMPORT & FORMAT DATA
    
    # Import PHREEQC data
    filename, directory, phreeqc_data = ResearchModules.fileGet(
        'Select PHREEQC output data file', tabletype = 'PHREEQC')
    
    # Import field data
    filename, directory, field_data = ResearchModules.fileGet(
        'Select field data file', tabletype = 'field', header_row = [0, 1],
        directory = directory)
    
    # Trim table to relevant values
    data = phreeqc_data.loc[phreeqc_data[col_Alk]==Alk,:]
    data = data.loc[data[col_Ca]==Ca,:]
    data = data.loc[data[col_TDS]==TDS,:]
    vals_T = np.unique(data[col_T])
    vals_pH = np.unique(data[col_pH])
    
    
    # PLOT DIAGRAMS
    
    # Loop through each mineral
    minerals = [col[3:] for col in data.columns if 'si_' in col]
    for mineral in minerals:
        # Convert saturation index to omega
        omegas = 10**(data['si_'+mineral])
    
        # Create the meshgrid
        print('Computing meshgrid...')
        X,Y = np.meshgrid(vals_pH, vals_T)
        xdata = data[col_pH]
        ydata = data[col_T]
        Z = interpolate.griddata((xdata,ydata), omegas, (X,Y), method='cubic')
        # Interpolation method options = 'cubic', 'linear', 'nearest'
        
        # Prep colormap
        bottom = ResearchModules.makeLogspace(
            start = omega_min, end = 1, steps = 10)
        top = ResearchModules.makeLogspace(
            start = 1, end = omega_max, steps = 10)
        cbounds = ResearchModules.round1SF(list(bottom[0:-1])+list(top))
        pltKwargs = {
                'levels':   cbounds,
                'norm':     colors.BoundaryNorm(boundaries=cbounds, ncolors=256),
                'cmap':     cmap_fan
                }
        
        
        # Plot fan diagram
        '''Enable this and swap ax for axs[0] for legend mode
        fig, axs = plt.subplots(
            ncols = 2, gridspec_kw = {'width_ratios' : [4,1]})
        '''
        fig, ax = plt.subplots(figsize = (9, 5))
        # Make the filled contour plot
        data_contourfplot = ax.contourf(X, Y, Z, **pltKwargs)
        
        # Draw a contour line at omega = 1.0
        data_contourlevels = ax.contour(data_contourfplot, levels = [1.0],
                                        colors = 'k')
        # Add titles and axis labels and set range
        ax.set_title(mineral + ' saturation')
        ax.set_xlabel('pH')
        ax.set_ylabel('Temperature (\u00b0C)')
        ax.autoscale(False)    
        
    
        # Overlay field T/pH points
        cmap = plt.get_cmap(cmap_date)
        field_data['datetime'] = [pd.to_datetime(dtime) 
                                  for dtime in field_data['Date']]
        field_data[col_pH_field] = pd.to_numeric(
            field_data[col_pH_field], errors = 'coerce', downcast = 'float')
        field_data[col_T_field] = pd.to_numeric(
            field_data[col_T_field], errors = 'coerce', downcast = 'float')
                
        # Prep colormap for date range
        date_min = min(field_data['datetime'])
        date_max = max(field_data['datetime'])
        date_range = (date_max - date_min).days
        # Create marker colormap (abbreviated colormap)
        date_mkr_cmap = pd.DataFrame(
            data = None, columns = ['datetime', 'dnum', 'color', 'datestr'])
        date_mkr_cmap['datetime'] = np.unique(field_data['datetime'])
        for date in date_mkr_cmap.index:
            dnum = (date_mkr_cmap.loc[date, 'datetime'] - date_min).days
            date_mkr_cmap.loc[date, 'dnum'] = dnum
            date_mkr_cmap.at[date, 'color'] =  (
                cmap(int(dnum * 255 / date_range)))
            date_mkr_cmap.loc[date, 'datestr'] = (
                date_mkr_cmap.loc[date,'datetime'].strftime('%b %Y'))
        # Create colorbar colormap (full colormap)
        date_cmap = pd.DataFrame(
            data = None,
            index = range(256),
            columns = ['datetime', 'datenum', 'color', 'datestr'])
        datenum = 0
        datetime = date_min
        datestep = date_range / 256
        dtstep = pd.DateOffset(days = datestep)
        date_cmap.loc[0] = [datetime, datenum, cmap(0), date_min.strftime('%b %Y')]
        for i in range(256):
            datenum = datenum + datestep
            datetime = datetime + dtstep
            date_cmap.loc[i, 'datetime'] = datetime
            date_cmap.loc[i, 'datenum'] = datenum
            date_cmap.loc[i, 'color'] = datenum *255 / date_range
            date_cmap.loc[i, 'datestr'] = datetime.strftime('%y %b')
         
        for val in field_data.index:
            # Determine marker properties
            marker = mkr_shape[field_data.loc[val,'Site']]
            color = date_mkr_cmap.loc[
                date_mkr_cmap['datetime'] == field_data.loc[val,'datetime'],
                'color']
            ax.scatter(pd.to_numeric(field_data.loc[val, col_pH_field],
                                     errors = 'coerce', downcast = 'float'),
                       pd.to_numeric(field_data.loc[val, col_T_field],
                                     errors = 'coerce', downcast = 'float'),
                       marker = marker, color = color,
                       label = val)
        
        # Add colorbars
        n = 6
        datestep = date_range / n
        datenums = np.arange(0, date_range + 1, datestep)
        datenums = [int(datenum) for datenum in datenums]
        date_labels = []
        for datenum in datenums:
            dt = date_min + pd.DateOffset(days = int(datenum))
            date_labels.append(dt.strftime('%b %Y'))
        norm = colors.Normalize(vmin = 0, vmax = n)
        cbar_dates = mpl.cm.ScalarMappable(norm = norm, cmap = cmap)
        cbar1 = fig.colorbar(cbar_dates, ax = ax,
                             orientation = 'vertical', pad = 0.1,
                             label = 'Measurement date',
                             ticks = range(n + 1))
        cbar1.ax.set_yticklabels(date_labels)
        cbar2 = fig.colorbar(data_contourfplot, ax = ax, extend = 'max',
                    orientation = 'vertical', format = cbar_num_format,
                    label = 'Omega')
        
        # Save figure
        fig.savefig(directory + '\\SaturationPlots_T-pH_' + mineral + '.svg')
