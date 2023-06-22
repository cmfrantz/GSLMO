# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 15:44:51 2023

@author: cariefrantz

Condenses timeseries data to daily summary table

"""

####################
# IMPORTS
####################

import ResearchModules
import os
import pandas as pd
import numpy as np
from tkinter import *
from tkinter import filedialog


####################
# VARIABLES
####################
dsets = {
    'elevation'     : {
        'title'     : 'Elevation (m)',
        'sheets'    : ['GSL_elevation_Saltair','GSL_elevation_Causeway'],
        'datecol'   : 'Datetime',
        'datacol'   : 'Elevation (m)',
        'headrow'   : 3,
        'summarize' : ['daily_mean']
        },
    'temperature'   : {
        'title'     : 'Temperature (\degC)',
        'sheets'    : ['HOBO_pendant','HOBO_button_top','HOBO_button_side'],
        'datecol'   : 'Datetime',
        'datacol'   : 'Temperature (°C)',
        'headrow'   : 3,
        'summarize' : ['daily_mean']
        },
    'light'         : {
        'title'     : 'Irradiance (lux)',
        'sheets'    : ['HOBO_button_top'],
        'datecol'   : 'Datetime',
        'datacol'   : 'Irradiance (lux)',
        'headrow'   : 3,
        'summarize' : ['daily_mean','daily_max']
        },
    'precip'        : {
        'title'     : 'Precipitation (cm)',
        'sheets'    : ['KUTSYRAC22','KUTSYRAC27'],
        'datecol'   : 'Datetime',
        'datacol'   : 'Precip. Accum (cm)',
        'headrow'   : 2,
        'summarize' : ['daily_accumulated']
        }
    }

date_min = '2019-01-01'
date_max = '2022-12-01'


####################
# FUNCTIONS
####################

def importData():
    '''
    Imports the spreadsheet, returns pandas.DataFrame containing the core data.
    '''
    # Get list of sheets to import
    sheet_list = []
    for ds in dsets:
        sheet_list=sheet_list+dsets[ds]['sheets']
    sheet_list = list(set(sheet_list))
    
    # Open user input file dialog to pick file
    root=Tk()
    filename = filedialog.askopenfilename(
        initialdir = os.getcwd(),
        title = 'Select compiled timeseries data file',
        filetypes = [('Excel', '*.xls, *.xlsx')])
    dirpath = os.path.dirname(filename)     # Directory
    root.destroy()
    
    # Import sheets
    sheets = {}
    for ds in dsets:
        for sheet in dsets[ds]['sheets']:
            if not sheet in sheets:
                print('Reading in ' + sheet + '...')
                sheets[sheet] = pd.read_excel(
                    filename, sheet_name = sheet,
                    header = dsets[ds]['headrow'],
                    index_col = dsets[ds]['datecol'])
    
    return sheets, dirpath

def summarizeData(sheets, dirpath):
    summary_table = pd.DataFrame()
    for ds in dsets:   
        # Grab the data
        for sheet in dsets[ds]['sheets']:
            data = sheets[sheet]
            data.index = pd.to_datetime(data.index, errors='coerce')
            data = data[date_min:date_max][dsets[ds]['datacol']].copy()
            data = pd.to_numeric(data, errors='coerce')
            for summary in dsets[ds]['summarize']:
                # Determine and run the type of summary
                data_summarized = eval(summary + '(data, sheet)')
                # Add to the table
                summary_table = pd.concat([summary_table, data_summarized], axis = 1, join='outer')
            
    # Save the table
    summary_table.to_excel(dirpath + '/timeseries_daily_summary.xlsx')

def daily_mean(data, sheet):
    data_summarized = data.resample('d').mean()
    data_summarized.name = sheet + ' daily mean ' + data.name
    return data_summarized
    
def daily_max(data, sheet):
    data_summarized = data.resample('d').max()
    data_summarized.name = sheet + ' daily max ' + data.name
    return data_summarized
    
def daily_accumulated(data, sheet):
    data_summarized = data.resample('d').max()
    data_summarized.name = sheet + ' daily accumulated ' + data.name
    return data_summarized
    



#%%
####################
# CODE
####################
if __name__ == '__main__': 
    sheets, dirpath = importData()
    summarizeData(sheets, dirpath)
    
    