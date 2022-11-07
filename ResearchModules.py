# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 13:50:49 2020

@author: cariefrantz
"""

###############
# IMPORTS
###############

import os
from tkinter import *
from tkinter import filedialog
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from datetime import timedelta
from scipy.interpolate import make_interp_spline


###############
# GLOBAL VARIABLES
###############

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


###############
# FUNCTIONS
###############

###############
# FILE ACQUISITION AND MANIPULATION

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


def download_lake_elevation_data(sdate_min, sdate_max, site=10010000):
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
    site : int, optional
        USGS site number

    Returns
    -------
    elev_data : pandas DataFrame containing five columns:
        agency | site_no | datetime | elevation (ft) | Data qualification
        (A = Approved for publication, P = Provisional)

    """
    # site = 10010000 # Great Salt Lake at Saltair Boat Harbor, UT
    # site = 10010024 # Great Salt Lake S of causeway near Lakeside, UT
    
    # Generate URL
    data_URL = ("https://waterdata.usgs.gov/nwis/dv?cb_62614=on&format=rdb" +
                 "&site_no=" + str(site) + "&referred_module=sw&period=" +
                 "&begin_date=" + sdate_min +
                 "&end_date=" + sdate_max)
    
    data_URL = ("https://nwis.waterservices.usgs.gov/nwis/iv/" + 
                "?sites=" + str(site) + "&parameterCd=62614" +
                "&startDT=" + sdate_min +
                "&endDT=" + sdate_max +
                "&siteStatus=all&format=rdb")
    
    # Load in website data
    elev_data = pd.read_csv(data_URL, sep = '\t', header = 28)
    
    # Save timestamps as index and convert date format
    elev_data['date'] = pd.to_datetime(elev_data['20d'])
    elev_data['20d'] = elev_data['date'].dt.strftime('%Y-%m-%d')
    elev_data.set_index('date', drop=True, inplace=True)
    
    return elev_data


def combineFiles(filelist, sep=',', header=0, force_cols=False):
    '''
    Combines a group of csv files into one big table

    Parameters
    ----------
    filelist : list of str
        list of files with filepaths
    sep : str, optional
        Seperator for the csv file. The default is ','.
    header : int, optional
        Row number of the header for each file. The default is 0.
    force_cols : bool, optional
        Whether or not to force match column names. The default is False.
            If true, the columns of the first file are used for each
                subsequent file.
            If false, columns with different names will be added as new
                columns

    Returns
    -------
    combined : TYPE
        DESCRIPTION.

    '''
    # Read in the first file to form the template
    combined = pd.read_csv(filelist[0], sep=sep, header=header)
    cols = list(combined.columns)
    
    # Read in and add each additional file
    for file in filelist[1:]:
        data = pd.read_csv(file, sep=sep, header=header)
        if force_cols:
            col_map = dict(zip(list(data.columns)[0:len(cols)],cols))
            data.rename(col_map, inplace=True)
        combined=combined.append(data)
        
    if force_cols:
        combined=combined[cols]
        
    return combined
        

def nansplit(value_list):
    '''Splits list at nans and returns list of nested lists (groups)'''
    # Split off any nan-containing rows
    groups = np.split(value_list, np.where(value_list.isnull().any(axis=1))[0])
    # Remove NaN entries and delete
    groups = [gr[~gr.isnull().any(axis=1)] for gr in groups if not
              isinstance(gr, np.ndarray)]
    groups = [gr for gr in groups if not gr.empty]
    return groups



###############
# DATA PLOTTING FUNCTIONS


def smooth_timeseries_data(data, valcol, resample_interval='1d',
                           smooth_interval='7d'):
    '''
    Smooths timeseries data by resampling and calculating a simple moving
    average.

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe with index = timestamps and columns containing data to be
        smoothed.
    valcol : str
        Name of the column containing the data to be smoothed
    resample_interval : str, optional
        Frequency for time resampling. The default is '1d' (daily).
    smooth_interval : str, optional
        Bin interval for simple moving average. The default is '7d' (weekly).

    Returns
    -------
    df_resampled : pd.DataFrame
        Dataframe containing the smoothed data.

    '''
    
    # Create the trimmed dataframe
    df = pd.DataFrame(data=data[valcol])
    df['Timestamp'] = df.index.to_pydatetime()
    df.set_index('Timestamp', inplace=True)
    
    # Summarize by date
    df_resampled=pd.DataFrame()
    df_resampled['mean'] = df.resample(resample_interval).mean()
    df_resampled['median'] = df.resample(resample_interval).median()
    df_resampled['min'] = df.resample(resample_interval).min()
    df_resampled['max'] = df.resample(resample_interval).max()

    
    # Moving average
    df_resampled['SMA'] = df_resampled['mean'].rolling(smooth_interval).mean()
    
    return df_resampled



def plotData(data, xcol, ycol, xlabel, ylabel, title, ax = [],
             plotsize=(12,6), smooth=False, savefig=False,
             xtype='general', datefmt='%m/%d/%y %H:%M'):
    '''
    Plots x,y data as a line plot, saves as png and svg.

    Parameters
    ----------
    data : pd.DataFrame
        Table containing the x and y data
    xcol : str
        Name of the dataframe column containing the x data
        'index' pulls x data from the dataframe index
    ycol : str
        Name of the dataframe column containing the y data
    xlabel : str
        X axis label for the plot
    ylabel : str
        Y axis label for the plot
    title : str
        Plot title for filename
    ax : matplotlib._subplots.AxesSubplot. The default is []
        Pass a subplot axes handle if a subplot already exists that the plot
        should be added to. The default creates a new plot.
    plotsize : tuple, optional
        Size of the plot (w, ht). The default is (12,6).
    smooth : bool, optional
        Whether or not to perform data smoothing. The default is False.
    xtype : str, optional
        Type of x-axis data. The default is 'general'.
        Options:
            'general'   : For non-timeseries x values
            'datetime'  : For timeseries x values
    datefmt : str, optional
        Datetime format in the table. Required if xtype == datetime.
        The default is '%m/%d/%y %H:%M'.

    Returns
    -------
    None.

    '''
    # Datetime axis formatting information
    years = mdates.YearLocator()
    months = mdates.MonthLocator()
    years_fmt = mdates.DateFormatter('%Y')
    
    # Default fig
    fig=[]

    # Select columns
    if xcol == 'index':
        xdata=data.index.values
    else:
        xdata = data[xcol].values 
    ydata = data[ycol].values
    
    # Convert timeseries data
    if xtype=='datetime':
        xdata = pd.to_datetime(xdata, errors='coerce')
        # xdata = [datetime.strptime(date, datefmt, errors='coerce') for date in xdata]
    else:
        xdata = pd.to_numeric(ydata, errors='coerce')
    
    # Format y data
    ydata = pd.to_numeric(ydata, errors='coerce')

    # Perform smoothing    
    if smooth==True:
        if xtype=='general':
            spline = make_interp_spline(xdata, ydata)
            xdata = np.linspace(xdata.min(), xdata.max(), 500)
            ydata = spline(xdata)
        
        # For datetime x, smooth data by moving average    
        if xtype=='datetime':
            df = pd.DataFrame(data=ydata,index=xdata,columns=['y'])
            smoothed = smooth_timeseries_data(df, 'y')
            ydata = smoothed['SMA'].values
            xdata = smoothed.index
            
            #y_df = pd.DataFrame(
            #    data = ydata, index = xdata, columns = ['y'], copy = True)
            #y_df = y_df[~y_df.index.duplicated()]
            #y_df = y_df.resample('1T').interpolate(
            #    'index', limit=20, limit_area = 'inside').resample(
            #        '7d').asfreq().dropna()
            # Determine weekly min/max values
            #minmax = y_df.resample('7d')['y'].agg(['min','max'])
            #ydata = y_df['y'].values
            #xdata = list(y_df.index)
    
    # Build new figure if no subplot exists
    if not ax:
        fig, ax = plt.subplots(figsize=plotsize)
        
    # Build plot
    ax.plot(xdata, ydata)
    ax.set(xlabel=xlabel, ylabel=ylabel)
    
    if xtype=='datetime':
        # Prettify datetime axis
        ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(years_fmt)
        ax.xaxis.set_minor_locator(months)
        
        # Round to nearest years
        datemin = pd.to_datetime(xdata[0].year, format='%Y')
        datemax = pd.to_datetime((xdata[-1] + timedelta(days=365)).year, format='%Y')
        ax.set_xlim(datemin, datemax)
    
    # Export plot
    if savefig:
        if fig:
            fig.show()
            fig.savefig(title + '.png')
            fig.savefig(title + '.svg')
        else:
            print('''Error: Trying to save a partial figure in PlotData.
If your plot has only one line, leave the ax value to default (ax=[]).
If you are plotting multiple lines, you will need to save the figure outside
the PlotData function.''')



###############
# COMMON CALCULATIONS

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


def convert_pressure(elev_m, T_C, P, conv_type):
    '''
    Converts weather station-reported pressures between absolute (at station)
    and relative (at sea level) pressure.

    Parameters
    ----------
    elev_m : int or float
        station (or location) elevation in meters
    T_C : int or float
        station temperature in degrees C
    P : int or float
        pressure to convert; can be any unit that scales linearly with kPa
        (including inHg)
    conv_type : str
        'abs_to_rel'    converts absolute (measured at the station) pressure
                        to relative (at sea level) pressure
        'rel_to_abs'    converts relative (value at sea level) pressure to
                        absolute pressure (equivalent at some elevation)

    Returns
    -------
    P_out : float
        converted pressure (in the original units)

    '''
    # Physical constants
    Lb = -0.0065    # standard temperature lapse rate (K/m)
    R = 8.31432     # ideal gas constant (N*m/mol/K)
    g0 = 9.80665    # gravitational acceleration (m/s^2)
    M = 0.0289644   # molar mass of Earth's air (kg/mol)
    
    # Convert ft to m
    # elev_m = 0.3048 * elev_ft
    
    # Convert T in C to K
    Tk = T_C + 273.15
    
    if conv_type == 'abs_to_rel':
        P_out = P * (1+Lb*elev_m/(Tk-Lb*elev_m))**(g0*M/R/Lb)
        
    if conv_type == 'rel_to_abs':
        P_out = P * (1+Lb*elev_m/(Tk-Lb*elev_m))**(-g0*M/R/Lb)
        
    return P_out


def calcDepth(water_pressure_Nm2, air_pressure_Nm2, density_gcm3):
    '''
    Calculates water depth from measured water and air pressure, plus density

    Parameters
    ----------
    water_pressure_Nm2 : int
        Water pressure in units of newtons per m^2.
    air_pressure_Nm2 : int
        Air pressure in units of newtons per m^2.
    density_gcm3 : int
        Water density in g/cm^3.

    Returns
    -------
    depth : int
        Water depth in meters.
        
    '''
    depth = ((water_pressure_Nm2 - air_pressure_Nm2) / 
             (density_gcm3 * gravity_factor * 1000))
    return depth


###############
# UNIT CONVERSIONS

def C_to_K(temp_C):
    '''Converts temperature in C to absolute temperature in Kelvin'''
    T_K = temp_C + 273.15
    return T_K


def F_to_C(temp_F):
    '''Converts temperature in Fahrenheit to temperature in Celsius'''
    T_C = (temp_F-32)*5/9
    return T_C


def ft_to_m(ft):
    '''Converts feet to meters'''
    m = ft/3.281
    return m


def inch_to_cm(inch):
    '''Concerts inches to cm'''
    cm = inch*2.54
    return cm


def lumft_to_lux(lumft):
    '''Converts lumen/ft2 to lux (lumen/m2)'''
    lux = lumft * 10.764
    return lux


def inHg_to_kPa(P_inHg):
    '''Converts pressure in inches mercury to kPa'''
    P_kPa = P_inHg * 3.386
    return P_kPa


def inHg_to_Nm2(P_inHg):
    '''Converts pressure in inches mercury to newtons/m^2'''
    P_Nm2 = P_inHg * 3386
    return P_Nm2


def kPa_to_Nm2(P_kPa):
    '''Converts pressure in kPascals to newtons/m^2'''
    P_Nm2 = P_kPa*1E3
    return P_Nm2