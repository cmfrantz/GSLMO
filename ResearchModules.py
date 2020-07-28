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
import matplotlib
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters





def fileGet(title, tabletype = 'Generic', directory = os.getcwd(),
            file_type = 'csv', header_row = 0, index_col = 0):
    '''This script imports data from a file chosen with a user input GUI.
    
    Parameters
    ----------
    title : str
        Text to put in the user input window.
    tabletype: str
        Type of table to input.
        Options are 'Generic' (default), 'HOBO', 'field', and 'PHREEQC'
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
    if tabletype == 'HOBO':
        header_row = 1
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


def plotTimeseries(ax, time_data, y_data, y_label = '', x_label = 'Date',
                   title = '', line_width = 0.5, legend = False):
    '''Builds a timeseries plot of the passed dataset(s)
        
    Parameters
    ----------
    ax : axis object
        Axis to place the plots in
    time_data: list of datenum objects
        Datetime values corresponding to each datapoint.
        Options are 'Generic' (default)
    y_data: list of values, list of lists of values, or pandas.DataFrame
        Should have the same number of values as the corresponding list(s) in
        time_data
    y_label : str, optional
        Label for the y axis. The default is none ('').
    x_label: str, optional
        Label for the x axis. The defailt is 'Date'.
    title: str, optional
        Plot title. The default is none ('').
    line_width: float, optional
        Size of the plot lines. The default is 0.5.
    legend: list of str or 'False', optional
        List of labels for the legend; there should be as many entries as
        there are y_data datasets. The default is False (no legend).
        
    Returns
    -------
    None.
    '''
    register_matplotlib_converters()
    
    def findType(var):
        # Variables
        error_text_pre = 'Error: y_data is in the wrong format. Passed '
        error_text_sfx = ', not list of numerical values or pandas.DataFrame.'
        num_type_list = [int, float, np.float64, np.float32, np.integer,
                         pd._libs.tslibs.timestamps.Timestamp]
        
        # Function
        var_type = type(var)

        if var_type == list:
            if type(var[0]) in num_type_list:
                var_type = 'list'
            elif type(var[0]) == list:
                if type(var[0][0]) in num_type_list:
                    var_type = 'list of lists'
                else: print(error_text_pre + 'list of lists of ' +
                            str(type(var[0][0])) + error_text_sfx)
        elif isinstance(var, pd.DataFrame):
            var_type = 'DataFrame'
        else: print(error_text_pre + var_type + error_text_sfx)
        
        return var_type
    
    # Determine whether data is in a supported type format
    type_time_data = findType(time_data)
    type_y_data = findType(y_data)
    type_legend = findType(legend)
    
    # Plot the data based on the type of data passed
    if type_time_data == 'list':
        if type_y_data == 'list':
            ax.plot(time_data, y_data, lw = line_width)
        elif type_y_data == 'list of lists':
            for y_set in y_data:
                ax.plot(time_data, y_set, lw = line_width)
    elif type_time_data == 'list of lists':
        if type_y_data == 'list of lists' and len(y_data) == len(time_data):
            for i in range(len(time_data)):
                ax.plot(time_data[i], y_data[i], lw = line_width)
        else: print('Error: time_data and y_data lists are different lengths')
    else: print('Error: either time_data or y_data are in an unsupported ' +
                'format for the function plotTimeseries')
    

    # Add labels 
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    if len(title)>0: ax.set_title(title)
    # Add legend
    if legend:
        ax.legend(legend)



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
