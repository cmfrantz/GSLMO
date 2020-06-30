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




def fileGet(title, tabletype = 'Generic', directory = os.getcwd(),
            file_type = 'csv', header_row = 0, index_col = 0):
    '''This script imports data from a file chosen with a user input GUI.
    
    Parameters
    ----------
    title : str
        Text to put in the user input window.
    tabletype: str
        Type of table to input.
        Options are 'Generic' (default)
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
    error_text = ('Error: y_data is in the wrong format. Passed '
                  + str(type(y_data))
                  + ', not list of numerical values or pandas.DataFrame.')
    # If y_data is a list of numbers, plot them
    if type(y_data) in [list, pd.core.series.Series]:
        if type(y_data[0]) in [int, float, np.float64, np.float32, np.integer]:
            ax.plot(time_data, y_data, lw = line_width)
    # If y_data is a list of numerical lists, plot each list as a line
        elif type(y_data[0]) in [list, pd.core.series.Series] and (
                type(y_data[0][0]) in
                [int, float, np.float64, np.float32, np.integer]):
            for y_list in y_data:
                ax.plot(time_data, y_list, lw = line_width)
    elif isinstance(y_data, pd.DataFrame):
        n = y_data.shape[1]
        # If multiple y are passed but only one x, make copies of x
        if type(time_data) == list:
            time_data = time_data * n
        # Loop through and plot each timeseries
        for i in range(n):
            ax.plot(time_data[:,i], y_data.iloc[:,i], lw = line_width)
    else: print(error_text)
    # Add labels 
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    if len(title)>0: ax.set_title(title)
    # Add legend
    if legend:
        ax.legend(legend)
    
