# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 13:50:49 2020

@author: cariefrantz
"""
import os
from tkinter import *
from tkinter import filedialog
import numpy as np
import pandas as pd
import math


# GLOBAL VARIABLES
gravity_factor = 9.80665

GSLMO_html_head = '''
<h1>Great Salt Lake Microbialite Observatory</h1>
<h2>Weber State University College of Science</h2>

<p>Lead investigator: Dr. Carie Frantz, Department of Earth and Environmental 
Sciences, <a href="mailto:cariefrantz@weber.edu">cariefrantz@weber.edu</a></p>
<p>This project is funded by the National Science Foundation,
<a href="https://www.nsf.gov/awardsearch/showAward?AWD_ID=1801760">
Award #1801760</a></p>
'''


# FUNCTIONS

def getFiles(title, directory = os.getcwd(), file_type = [('CSV', '*.csv')]):
    '''Gets list of files from user selection'''
    root = Tk()
    fileList = filedialog.askopenfilenames(initialdir=directory, title = title,
                                        filetypes = file_type)
    root.destroy()
    dirPath = os.path.dirname(fileList[0])
    
    return fileList, dirPath


def fileGet(title, tabletype = 'Generic', directory = os.getcwd(),
            file_type = 'csv', header_row = 0, index_col = 0):
    '''This script imports data from a file chosen with a user input GUI.
    
    Parameters
    ----------
    title : str
        Text to put in the user input window.
    tabletype: str
        Type of table to input.
        Options are 'Generic' (default), 'HOBO_raw', 'HOBO_comb', 'field',
            and 'PHREEQC'
    directory : str, optional
        The start directory to search in. The default is os.getcwd().
    file_type : str, optional
        The type of file. Options are currently only:
            'csv' (default)     comma-seperated file
            'tsv'               tab-seperated file
    header_row : int, optional
        The row of the file to capture for the data header. The default is 0.
    index_col : int, optional
        The column of the file to capture for the data index. The default is 0.

    Returns
    -------
    filename : str
        Selected file full filepath.
    dirPath : str
        Filepath for the directory containing the selected file.
    data : pandas.DataFrame
        DataFrame containing the indexed data read in from the file.
    '''
    
    # If type of file is specified, use the proper format
    if tabletype == 'HOBO_raw':
        header_row = 1
        index_col = 0
        file_type = 'csv'
    if tabletype == 'HOBO_comb':
        header_row = 0
        index_col = 1
        file_type = 'csv'
    if tabletype == 'field':
        header_row = 1
        index_col = 0
    if tabletype == 'PHREEQC':
        header_row = 0
        index_col = 0
    
    # Define filetypes
    if file_type == 'csv':
        ftype = [('CSV', '*.csv')]
        sep = ','
    elif file_type == 'tsv':
        ftype = [('TSV'), '*.tsv, *.txt']
        sep = '\t'
    
    # Open user input file dialog to pick file
    root=Tk()
    filename=filedialog.askopenfilename(initialdir=directory, title = title,
                                        filetypes = ftype)
    dirPath = os.path.dirname(filename)     # Directory
    root.destroy()
    
    # Read file
    print('Loading ' + filename + '...')
    data = pd.read_csv(filename, sep = sep,
                       header = header_row, index_col = index_col)
    
    return filename, dirPath, data


def calcDepth(water_pressure, air_pressure, density):
    depth = (water_pressure - air_pressure) * density / gravity_factor
    return depth


def round1SF(list):
    '''Round a list of numerical values to 1 significant figure'''
    for i in np.arange(len(list)):
        list[i] = round(list[i], -int(np.floor(np.log10(abs(list[i])))))
    return list


def makeLogspace(**kwargs):
    '''
    Creates a list of values evenly spaced in log 10 space

    Parameters
    ----------
    **kwargs : Input arguments
        Define three of possible four variables: start, end, res, &/or steps:
            start   = start value for list
                        (default = 1e-10)
            end     = end value for list
                        (default = 1)
            res     = minimum number of values between each log10 step
                        (default = 3)
            steps   = number of steps between start & end
                        (default = 10)

    Returns
    -------
    logspace: list of numerical values


    '''
    print(kwargs)
    # Defaults
    def_steps = 10
    def_res = 1
    def_min = 0
    
    arglist = [x for x in kwargs]
      

    if 'start' in arglist:
        minval = np.log10(kwargs['start'])
        print('start is in arglist. minval = ' + str(minval))
        
        if 'end' in arglist:
            maxval = np.log10(kwargs['end'])
            diff = maxval-minval
            
            if 'res' in arglist:
                resolution = kwargs['res']
                n = math.ceil(diff/resolution+1)
                
            elif 'steps' in arglist:
                n = kwargs['steps']
                
            else:
                n = def_steps
                
        elif 'res' in arglist:
            if 'steps' in arglist:
                maxval = minval + kwargs['steps']/kwargs['res']
                n = kwargs['steps']
                
            else:
                maxval = minval + def_steps/kwargs['res']
                n = def_steps
        else:
            if 'steps' in arglist:
                maxval = minval + kwargs['steps']/def_res
                n = kwargs['steps']
            else:
                maxval = minval + def_steps/def_res
                n = def_steps
    elif 'end' in arglist:
        maxval = np.log10(kwargs['end'])
        print('start is not in arglist. end is in arglist. maxval = ' + str(maxval))
        
        if 'res' in arglist:
            if 'steps' in arglist:
                minval = maxval - kwargs['steps']/kwargs['res']
                n = kwargs['steps']
            else:
                minval = maxval - def_steps/kwargs['res']
                n = def_steps
        else:
            if 'steps' in arglist:
                minval = maxval - kwargs['steps']/def_res
                n = kwargs['steps']
            else:
                minval = maxval - def_steps/def_res
                n = def_steps
                
    elif 'res' in arglist:
        print('start and end are not in arglist. res is in arglist.')
        minval = def_min
        if 'steps' in arglist:
            maxval = minval + kwargs['steps']/def_res
            n = kwargs['steps']
        else:
            maxval = minval + def_steps/def_res
            n = def_steps
        
    else:
        print('start, end, and res are not in arglist.')
        if 'steps' in arglist:
            minval = def_min
            maxval = minval + kwargs['steps']/def_res
            n = kwargs['steps']
        else:
            minval = def_min
            maxval = minval + def_steps/def_res
            n = def_steps
    
    print('minval: '+str(minval)+'  maxval: '+str(maxval)+'  n: '+str(n))
    return np.logspace(minval, maxval, num = n, endpoint = True, base = 10)



def nansplit(value_list):
    '''Splits list at nans and returns list of nested lists (groups)'''
    # Split off any nan-containing rows
    groups = np.split(value_list, np.where(value_list.isnull().any(axis=1))[0])
    # Remove NaN entries and delete
    groups = [gr[~gr.isnull().any(axis=1)] for gr in groups if not
              isinstance(gr, np.ndarray)]
    groups = [gr for gr in groups if not gr.empty]
    return groups


def download_lake_elevation_data(sdate_min, sdate_max):
    """
    This function downloads lake elevation data at Saltair from the USGS
    waterdata web interface

    Parameters
    ----------
    sdate_min : string
        Start date for data download in format 'YYYY-mm-dd'.
        (use date_min.strftime('%Y-%m-%d') to format a timestamp)
    sdate_max : string
        End date for data download in format 'YYYY-mm-dd'.

    Returns
    -------
    elev_data : pandas DataFrame containing five columns:
        agency | site_no | datetime | elevation (ft) | Data qualification
        (A = Approved for publication, P = Provisional)

    """
    site_no = 10010000 # Great Salt Lake at Saltair Boat Harbor, UT
    
    # Generate URL
    data_URL = ("https://waterdata.usgs.gov/nwis/dv?cb_62614=on&format=rdb" +
                 "&site_no=" + str(site_no) + "&referred_module=sw&period=" +
                 "&begin_date=" + sdate_min +
                 "&end_date=" + sdate_max)
    
    # Load in website data
    elev_data = pd.read_csv(data_URL, sep = '\t', header = 31)
    
    # Save timestamps as index and convert date format
    elev_data['date'] = pd.to_datetime(elev_data['20d'])
    elev_data['20d'] = elev_data['date'].dt.strftime('%Y-%m-%d')
    elev_data.set_index('date', drop=True, inplace=True)
    
    return elev_data