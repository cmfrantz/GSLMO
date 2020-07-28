# -*- coding: utf-8 -*-
"""
Created on Wed Feb 18 2020
Last updated Thursday Mar 30 2020

@author: cariefrantz
Carie Frantz
Weber State University
Department of Earth & Environmental Sciences

Imports csv output from PHREEQC (output of PHREEQC_output_combiner.py), 
Plots user-defined fan diagram(s) with process arrow(s)

To run:
  1. Generate model calculation table in PHREEQC for all of the pH, TA, T, and TDS values to be tested and plotted
  2. Output table should include the headers:
          pH  T(C)  Alk(meq/kg)  TDS(ppt)  density(g/cm3)   si_Anhydrite  si_Aragonite  si_other minerals...
     and either    m_CO2  m_HCO3-  m_CO3-2  
     and/or        DIC(mmol/kg)  <--This will be used as default if available
     Note that the file PHREEQC spits out has weird spaces in the header that need to be removed first using a replace all
  4. Run this script.
  5. "Measured value" will place a star where on the plot at the measured value.

"""

"""
------------------
IMPORTS AND SETUP
------------------
Do not change these
"""
import os
import sys
from tkinter import filedialog
from tkinter import *
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.patches as mpatches
from matplotlib import ticker, cm
import numpy as np
import pandas as pd
import math
from scipy import interpolate

# This tells matplotlib to save text in a format that Adobe Illustrator can read
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

"""
------------------
VARIABLES
------------------
Modify these as needed to fit the available data and desired product.
"""
# Variable names for user to choose from when building plots
"""
varnames = [
        ["T",   "T(C)",         "Temperature (\u00b0C)"                 ],
        ["pH",  "pH",           "pH"                                    ],
        ["Alk", "Alk(meq/kg)",  "Total Alkalinity (meq/kg)"             ],
        ["DIC", "DIC(mmol/kg)", "Dissolved Inorganic Carbon (mmolC/kg)" ],
        ["TDS", "TDS(ppt)",     "Total Dissolved Solids (g/L)"          ],
        ["Ca",  "[Ca](mg/kg)",  "Calcium concentration (mg/kg)"         ]
        ]
varnames=pd.DataFrame(varnames,index=[x[0] for x in varnames],columns=['short','columnname','fullname'])
"""
varlist = {
        'T':    {'short': 'T',      'digits': 0,    'colname': 'T(C)',          'fullname': 'Temperature (\u00b0C)'         },
        'pH':   {'short': 'pH',     'digits': 1,    'colname': 'pH',            'fullname': 'pH'                            },
        'Alk':  {'short': 'Alk',    'digits': 0,    'colname': 'Alk(meq/kg)',   'fullname': 'Total Alkalinity (meq/kg)'     },
        'DIC':  {'short': 'DIC',    'digits': 0,    'colname': 'DIC(mmol/kg)',  'fullname': 'Dissolved Inorganic Carbon (mmolC/kg)'},
        'TDS':  {'short': 'TDS',    'digits': 0,    'colname': 'TDS(ppt)',      'fullname': 'Total Dissolved Solids (g/L)'  },
        'Ca':   {'short': 'Ca',     'digits': 0,    'colname': '[Ca](mg/kg)',   'fullname': 'Calcium concentration (mg/kg)' }
        }

DICcols = ["m_CO2","m_HCO3-","m_CO3-2"] # Names of columns in input spreadhseet containing TIC values (mol/L)
carbVars = ["pH", "Alk", "DIC"]         # Variables that define the carbonate system. Only use two at a time.

arrowMargin = 0.05  # How far from the edge of the plot (in % width) a process arrow can reach

# Boundaries for the plot color key (omega values)
cmap = 'RdBu_r'     # Colormap to use
clrbounds = 'Calc'  # Calculate colorbounds from the values provided below
omega_min = 1E-3    # Min value for the colormap
omega_max = 1000    # Max value for the colormap
# Or a list of boundary values can be given

# Formatting options
cbar_num_format = '%g'
    
# %%
"""
------------------
THESE FUNCTIONS PERFORM KEY CALCULATIONS
------------------
"""

# Converts pH to (H+) in mM
def pH2H(pH):
    H=10**(-pH+3)
    return H

# Converts (H+) in mM to pH
def H2pH(H):
    pH=-np.log10(H/1000)
    return pH

# Calculate DIC in mmol/kg
def calcDIC(DICvals):
    # DICvals is a matrix with columns m_CO2, m_HCO3-, m_CO3-2 (in mol/kg)
    DIC = DICvals.sum(axis=1)*1000              # Calculates DIC in mmol/kg
    return DIC

# Round a list of numerical values to 1 significant figure
def round1SF(list):
    for i in np.arange(len(list)):
        list[i] = round(list[i], -int(np.floor(np.log10(abs(list[i])))))
    return list


# Creates a list of values evenly spaced in log 10 space
# start, end are the endpoints for the set
# step is the number of points within each log step
# Define 3 of 4 values
def makeLogspace(**kwargs):
    # Define *three* of four possible variables
    # start     = start value for list  (default = 1e-10)
    # end       = end value for list    (default = 1)
    # res       = minimum number of values between each log10 step (default = 3)
    # steps     = number of steps between start & end       (default = 10)
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


# %%
"""
------------------
THESE FUNCTIONS  GET AND PREP DATA BASED ON USER INPUT
------------------
"""
# Ask the user to find the csv file to use, load the file data
def getCSV(title):
    while True:
        try:
            root = Tk()                     # Opens user input window
            root.filename = filedialog.askopenfilename(initialdir = "/", title = title, filetypes = [('CSV', '*.csv')])     # Ask user for file
            filename = root.filename        # Retrieves the selected filename
            print (filename)                # Prints the filename
            root.destroy()                  # Closes the user input window
            print('Loading file...')    
            data = getData(filename)        # Loads in data from filename
            break
        except ValueError:
            print("Something was wrong with the file " + filename + ".  Try again...")

    return data, filename

#
#!!!!! Need to figure out how to loop exceptions if the data isn't in the expected format
def getData(filename):
    data = pd.read_csv(filename, delimiter=",", index_col=False)    # Loads in csv data as a pandas dataframe
    data = addDIC(data)     # Adds DIC columns if not already there
    return data


"""
# Use this if the user already has a formatted matrix of data
# This isn't currently being used
# Get csv matrix of values from user
def importMatrix():
    # Open a user input dialog for user to select data csv file
    # Get data from the user
    data, filename = getCSV("Select csv file containing the matrix table of omega data")
    
    # Determine the size of the matrix and assign values to the rows and columns by user input
    mineral = input("Which mineral are the omega values for? (Enter text)  > ")
    varX = input("what variable to the columns of data represent? (Enter text)  > ")
    varY = input("What variable do the rows of data represent? (Enter text)  > ")
    valStartCol = float(input("Enter the start value for '" + varX + "'  > "))
    valEndCol = float(input("Enter the end value for '" + varX + "'  > "))
    valStartRow = float(input("Enter the start value for '" + varY + "'  > "))
    valEndRow = float(input("Enter the end value for '" + varY + "'  > "))
    x_head = np.linspace(valStartCol, valEndCol, len(data[0]))  # Labels columns with the corresponding y axis value
    y_head = np.linspace(valStartRow, valEndRow, len(data))     # Labels rows with the corresponding x axis value
    X,Y = np.meshgrid(x_head, y_head)
    
    return X, Y, data, varX, varY, mineral, filename
"""

# Select axis variables from a list
def selectAxisVariable(axis, var_available):
    while True:
        var = input("What is the " + axis + " axis variable to plot? Type one: " + ", ".join(var_available) + "  > ")
        if var in var_available:
            var_available.remove(var)
            break
        else: print("Error. Choose an available variable. ")
    return var, var_available


# Trim the table
def trimTable(var_available, data):
    vals = []
    
    for var in var_available:
        
        print('Trimming ' + var + '...')
        # If a variable is DIC, use the binned DIC values
        if var == 'DIC': varcol = 'DIC_round'
        # Otherwise, select the appropriate column
        else: varcol = varlist[var]['colname']
        #else: varcol = varnames.loc[var]['columnname']
        
        # Find the unique options for the axis variable
        uniques = np.unique(data[varcol].tolist())
        uniques = uniques[~np.isnan(uniques)]
    
        # Convert to strings
        uniques = ['{0:g}'.format(x) for x in uniques]  # format: g option removes insigificant trailing zeroes and decimal point if no remaining digits follow.
        
        # Ask the user to select among the unique values
        val = float(pickValue(uniques, 'What is the value of ' + var + '?'))
        vals.append(val)
        
        # Deletes rows that do not contain user-defined variable values
        data=data.loc[data[varcol] == val]
        
    return [var_available,vals], data

# Pick a value from the list
def pickValue(valueList, text):
    valueList = [str(x) for x in valueList]     # Convert any numbers to str
    while True:
        value = input(text + '  Options: ' + ', '.join(valueList) + '  > ')
        if value in valueList:
            break
        else: print('Error. Select a valid value from among the listed options.')
    return value

# Build a 2D matrix from a subset of the data to use for the user-defined plot
def buildMatrixFromTable(data):
    # Function imports a PHREEQC output table and with user input generates a 2D matrix of omega values
    
    # Make a list of the available variables
    #var_available = list(var['short'] for var in varlist.values() if var)
    var_available = list(var for var in varlist.keys() if var)
    
    # Have user select the desired x and y axes  
    # Get x and y axis variables
    [varX, var_available] = selectAxisVariable('x', var_available)
    [varY, var_available] = selectAxisVariable('y', var_available)
    
    # In order to prevent over-constraining the carbonate system, determine which carbonate variables remain
    var_available = constrainCarbonateSys(var_available)
    
    # Get values of remaining variables and delete data from table that doesn't match
    [var_vals, trimdata] = trimTable(var_available, data)
    
    # Build the matrix
    # Find & sort unique input values for each axis variable
    # Find data that matches and fill in matrix
    headX = getHeaderSet(varX, trimdata)
    headY = getHeaderSet(varY, trimdata)
    
    # Pick the mineral to plot
    mineral = pickValue(allMinerals(trimdata.columns), 'Which mineral saturation value are you interested in?')
   
    
    # Convert saturation index to omega
    omegas = 10**(trimdata['si_'+mineral])
    
    # Create the meshgrid
    print('Computing meshgrid...')
    X,Y = np.meshgrid(headX, headY)
    xdata = trimdata[varlist[varX]['colname']]
    ydata = trimdata[varlist[varY]['colname']]
    Z = interpolate.griddata((xdata,ydata), omegas, (X,Y), method='cubic')
    # Interpolation method options = 'cubic', 'linear', 'nearest'
    
    # Create a container for the xy values
    xyVals = {
            'x' : {'var': varX, 'data': xdata},
            'y' : {'var': varY, 'data': ydata}
            }
    
    matrix3D = {
            'X': X,
            'Y': Y,
            'Z': Z
            }
    
    return matrix3D, xyVals, var_vals, mineral


# From the data matrix headers, return the minerals
def allMinerals(header):
    minerals = [col for col in header if 'si_' in col]
    minerals = [x.strip('si_') for x in minerals]
    return minerals

# Determines the variables available to constrain the system
def getHeaderSet(var, data):
    # If the variable being plotted is DIC, pick the rounded values for the headers
    if var == 'DIC':
        columnname = 'DIC_round'
    # Otherwise, the header values should be the unique values in the set
    else:
        columnname = varlist[var]['colname']
    head = np.unique(data[columnname])
    return head

# DIC switch to pick 2 of 3 DIC parameters to use to define the carbonate system
def constrainCarbonateSys(var_available):
    carbParams = list(set(var_available).intersection(carbVars))
    x = len(carbParams)
    if x == 0: print('Warning: Carbonate system is over-constrained.')
    elif x == 2: carbParams.remove(pickValue(carbParams, 'Which additional parameter would you like to use to constrain the carbonate system?'))
    elif x == 3:
        carbParams.remove(pickValue(carbParams, 'You must choose two parameters to constrain the carbonate system. Pick the first. '))
        carbParams.remove(pickValue(carbParams, 'Pick the second.'))           
            
    for val in carbParams: var_available.remove(val)
    
    return var_available


# Add DIC to the dataset if not already present
def addDIC(data):
    # Check if data already has DIC entered
    DICcol = varlist['DIC']['colname']
    if DICcol not in data.columns:
        print('Adding DIC data...')
        data[DICcol] = calcDIC(data[DICcols])    # Calculates DIC in mmol/kg
    
    # Sort DIC values into bins
    DIC = data[DICcol]
    bins = np.linspace(DIC.min(), DIC.max(), 10)              # Create bin boundaries (10 boundaries = 9 bins)
    digitized = np.digitize(DIC, bins)                        # Determine which bin each value is in
    bin_means = [round(DIC[digitized == i].mean(), 0) for i in range(1, len(bins)+1)]     # Find the rounded mean of each bin
    # Assign bin values to the DIC_round column
    data['DIC_round']=np.nan
    for i in range(1, len(bins)+1):
        data.loc[digitized==i,'DIC_round'] = bin_means[i-1]
        
    return data
    

# Generates a detailed filename based on the subset of data plotted
def genFilename(varX, varY, var_vals, mineral):
    #filepfx = input("File name prefix:   > ")
    filepfx = 'fan_'
    varstr = ''
    for x in range(len(var_vals[0])):
        varstr = varstr + '_' + var_vals[0][x] + str(round(var_vals[1][x]))
    filename = filepfx + varY + 'v' + varX + varstr + '_' + mineral
    
    return filename
        

# %%
"""
------------------
THESE FUNCTIONS BUILD THE PLOTS
------------------
"""


#Plot contour plot
def plot_contour(matrix3D, xyVals, var_vals, mineral):
    
    # Plot variables
    varX =  xyVals['x']['var']
    varY =  xyVals['y']['var']
    xdata = xyVals['x']['data']
    ydata = xyVals['y']['data']
    
    # Define colormap
    # Alternately, check out these methods:
    # Log scale: https://matplotlib.org/3.2.1/tutorials/colors/colormapnorms.html
    # Diverging scale: https://matplotlib.org/3.1.1/gallery/userdemo/colormap_normalizations_diverging.html#sphx-glr-gallery-userdemo-colormap-normalizations-diverging-py
    
    cbounds = calcColorBounds(clrbounds)
    pltKwargs = {
            'levels':   cbounds,
            'norm':     colors.BoundaryNorm(boundaries=cbounds, ncolors=256),
            'cmap':     cmap
            }
    
    # Build the plot          
    def buildplot():
        fig, ax = plt.subplots()
        
        # Make the filled contour plot
        data_contourfplot = ax.contourf(matrix3D['X'], matrix3D['Y'], matrix3D['Z'], **pltKwargs)
        #data_contourfplot = ax1.contourf(x_head, y_head, data, cntr_levels)  # Makes plot with pre-defined contour levels
        # data_contourfplot.cmap.set_under('white')  # This code blocks out part of the graph in theory
        
        # Draw a contour line at omega = 1.0
        data_contourlevels = ax.contour(data_contourfplot, levels = [1.0], colors = 'k')
        #data_contourlevels = ax1.contour(data_contourfplot, cntr_levels, colors = 'k', linewidths = cntr_linewidths)  # Uses pre-defined contour levels and lines
        # plt.clabel(data_contourlevels, colors = 'k', fmt = '%2.1f', fontsize=8)  #Label contour lines
            
        # Add titles and axis labels and set range
        ax.set_title(mineral + ' saturation')
        ax.set_xlabel(varlist[varX]['fullname'])
        ax.set_ylabel(varlist[varY]['fullname'])
        
        # Add colorbar

        cbar = fig.colorbar(data_contourfplot, ax = ax, extend='max', orientation='vertical', format=cbar_num_format)
        #cbar.set_clim(0,10)
        cbar.ax.set_ylabel('Omega') 
        
        return fig, ax
    
    # Preview the plot
    def previewPlot():
        if input('Preview the plot now? Y/N  > ') == 'Y': plt.show()
    
    ########
    # Plot first draft (view basic version to determine what else to add)
    fig, ax = buildplot()
    previewPlot()
    
    ###
    # Plot second draft (add all of the extras and re-plot)
    fig, ax = buildplot()
        
    # Add the extras  
    
    # Set the display range
    xBounds = getBounds(varX, xdata)
    yBounds = getBounds(varY, ydata)
    ax.set(xlim=xBounds, ylim=yBounds)
    ax.autoscale(False)
    
    # Overlay modeled data points
    ax.plot(xdata,ydata, 'k,', zorder=1)
    
    # Set default origin
    origin = [np.average(xdata), np.average(ydata)]
    
    # Overlay measured value if user wants
    addStar = input('Add measured value star? Y/N >  ')
    if addStar == 'Y':
        origin = getStarCoord(varX, varY, xBounds, yBounds)
        ax.plot(origin[0], origin[1], 'k*', zorder=1)  # Add the measurement star
        
    # Add process arrows if user wants
    addArrow = input('Add process arrow(s)? Y/N >  ')
    if addArrow == 'Y':
        arrows = addArrows(varX, varY, xBounds, yBounds, origin)
        for arrow in arrows:
            ax.add_artist(arrows[arrow]['arrow'])
            ax.text(**buildLabel(arrow, arrows[arrow]['endcoord'], origin))
                
    previewPlot()
    
    # Save the image
    filename=genFilename(varX, varY, var_vals, mineral)
    fig.savefig(os.getcwd() + '\\' + filename + ".svg", transparent=True)
    fig.savefig(os.getcwd() + '\\' + filename + ".pdf", transparent=True)
    


########
# Calculate the color scale boundaries
def calcColorBounds(clrbounds):
    # Default is to use the provided list clrbounds, otherwise...
    if type(clrbounds) != list:
        print('Calculating colorbounds...')
        bottom = makeLogspace(start = omega_min, end = 1, steps = 10)
        top = makeLogspace(start = 1, end = omega_max, steps = 10)
        boundlist = round1SF(list(bottom[0:-1])+list(top))
    # Define the color space
    return boundlist

# Formats number in 3*10^2 format
# Not currently used
def fmtExp(x, pos):
    a, b = '{:.0e}'.format(x).split('e')
    # x = a * 10**b = a * 10**(b-1) * 10**1
    a = int(a)
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)

# Define contour levels
# This is not currently used, but could be for finer control of contour levels
def find_contourLevels(data):
    # 1. Determine the contour range and values
    cntr_levels = [0.0,0.5,0.9]             # Defines the contour values below 1.0
    maxOmega = np.amax(np.ceil(data))       # Finds the max omega value in the data matrix and rounds up to the nearest integer
    # Select the step size for the contour plot
    if maxOmega>3: 
        delta = 1
    else:
        delta = (maxOmega-1)/5
        
    list_HighOmega = np.arange(1,maxOmega+delta,delta)  # Set the contour levels for omega > 1
    cntr_levels.extend(list_HighOmega)      # Combine the two lists of contour levels
    cntr_linewidths = [0]*len(cntr_levels)  # Define line widths for the contour lines
    cntr_linewidths[3] = 1                  # Set the line width for omega = 1 to 1 px (thicker)
    
    return cntr_levels, cntr_linewidths

# Determine the range over which to show the plot      
def getBounds(var, vardata):
    bounds = [min(vardata), max(vardata)]   # Default is the full range
    sel = input('Would you like to set the ' + var + ' axis display range? Y/N  > ')
    if sel == 'Y':
        inval = input(
                "Enter the desired range as min-max (e.g., '2-7'), 'Auto' to automatically select a mid-range, or 'Range' to use the full range of values. \nThe range for this axis is : " 
                + str(round(min(vardata),1)) + ' - ' + str(round(max(vardata),1)) + '  > ')     
        if "-" in inval:                   # User-specified range
            bounds = [float(i) for i in inval.split('-')]
                
        elif inval == "Auto":              # Auto takes the avg +/- std as the range
            avg = np.mean(vardata)
            std = np.std(vardata)
            bounds = [avg-std, avg+std]       
    
    return bounds
            
            
# %%
"""
------------------
THESE FUNCTIONS BUILD PLOT ANNOTATIONS
------------------
"""   

# Get the coordinates for the measurement star
def getStarCoord(varX, varY, xBounds, yBounds):
    vardict = {
            'x': {  'var':      varX,
                    'bounds':   xBounds},
            'y': {  'var':      varY,
                    'bounds':   yBounds}
            }
    
    for var in list(vardict):
        while True:
            bounds = vardict[var]['bounds']
            val = input('What is the measured value of ' 
                        + vardict[var]['var'] 
                        + '? \nThe range plotted is ' 
                        + str(round(min(bounds))) + ' - '
                        + str(round(max(bounds))) + '  > ')
            try:
                vardict[var]['val'] = float(val)
            except:
                if val == 'q': sys.exit()
                else: print('Choose a valid value. Enter "q" to quit.')
                
            else: break
        
    return [vardict['x']['val'], vardict['y']['val']]



# Add process arrows
def addArrows(varX, varY, xBounds, yBounds, origin):
    
    # Loop to get process arrow(s)
    addProcess = "Y"
    arrows = {}
    
    #pd.DataFrame(columns=["process","dx","dy"])
    
    while addProcess == "Y" :
        # Ask user for details, generate coordinates
        [process, a] = genProcessArrow(varX, varY)
        arrows[process] = a
        addProcess = input("Add another process arrow? Y/N >  ")
        if addProcess != "Y":
            break
        
    # Scale arrows so they fit in figure    
    arrows = scaleArrows(varX, varY, xBounds, yBounds, origin, arrows)
    
    # Build arrow annotations
    arrows = buildArrows(arrows, origin)
    
    return arrows


# Build arrows for microbial metabolism or other process
def genProcessArrow(varX,varY):
      
    # Use the column names (which contain units) for the text  
    # If pH is plotted, ask user for change in (H+) instead of change in pH
    varXtext = varlist[varX]['colname'] if varX !='pH' else 'H+ in mmol/kg'
    varYtext = varlist[varY]['colname'] if varY !='pH' else 'H+ in mmol/kg'
    
    # Get the process details
    process = input("Name of the process?  >  ")
    dx = float(input("How many units does the process change " + varXtext + "?  >  "))
    dy = float(input("How many units does the process change " + varYtext + "?  >  "))
    
    arrowDict = {
            'dx':    dx,
            'dy':    dy
            }

    return process, arrowDict


# Build the arrow art
def buildArrows(arrows, origin):
    processes = [x for x in arrows]
    
    for process in processes:
        arrows[process]['arrow'] = mpatches.FancyArrowPatch(
                posA =          arrows[process]['endcoord'],
                posB =          origin,
                arrowstyle =    "<-",
                shrinkA =       0,
                shrinkB =       0,
                mutation_scale = 5
                )
    return arrows


# Scale the generated arrows to fit the plot
def scaleArrows(varX, varY, xBounds, yBounds, origin, arrows):
    # Here,     varX/varY are the variable names
    #           xBounds/yBounds are the plot axis bounds for x and y [min, max]
    #           origin is the point from which arrows radiate
    #           arrows are a dict of processes with process name, dx, and dy values 
    
    processes = [x for x in arrows]     # Gets list of processes
    sflist = []
    
    # Calculate the scale factors for each process and axis
    for process in processes:
        # Calculate the scale factors
        arrows[process]['sfx'] = determine_sf(varX, xBounds, origin[0], arrows[process]['dx'])
        arrows[process]['sfy'] = determine_sf(varY, yBounds, origin[1], arrows[process]['dy'])
        sflist = sflist + [arrows[process]['sfx'], arrows[process]['sfy']]
        
    # Find the minimum scale factor
    sf = min(sflist)
    
    for process in processes:
        [sdx, xcoord] = findArrowCoords(varX, origin[0], arrows[process]['dx'], sf)
        [sdy, ycoord] = findArrowCoords(varY, origin[1], arrows[process]['dy'], sf)
                
        # Save the arrow data
        arrows[process].update({
                'sf':       sf,
                'sdx':      sdx,
                'sdy':      sdy,
                'endcoord': [xcoord, ycoord]
                })
        
    return(arrows)

# Determine scale factors
def determine_sf(var, bounds, origin_val, delta):
    if var == 'pH':
        [boundsH, valH] = calcpHbounds(bounds, origin_val)
        sf = calc_sf(boundsH, valH, [delta])
    else:
        sf = calc_sf(findBounds(bounds), origin_val, [delta])
    return sf

# Calculate the arrow scale factor based on the available plot space
def calc_sf(bounds, val, delta)  :
    
    # Here, bounds is the allowable min and max value that the arrow can go to    
    # Loop through the deltas and determie sf to set arrow vector length to the limit
    sf = []
    for i in delta:
        if i<0:
            len = abs(val - min(bounds))
            sf.append(len/abs(i))
        elif i>0:
            len = abs(max(bounds) - val)
            sf.append(len/i)
        else:
            sf.append(np.nan)
            
    return min(sf)


# Determine arrow length and coordinates
def findArrowCoords(var, origin_val, delta, sf):
    # Calculate vector length
    vector_len = delta*sf
    
    if var == 'pH':
        Hcoord = pH2H(origin_val) + vector_len
        coord = H2pH(Hcoord)
    else: coord = origin_val + vector_len
    
    return vector_len, coord
    
# Uses the arrowMargin value to determine the min and max arrow tip values for an axis
def findBounds(lims):
    # lims defines the plot boundaries: [lim_min, lim_max]
    
    width = max(lims)-min(lims)
    margin = width * arrowMargin
    
    bound_min = min(lims) + margin
    bound_max = max(lims) - margin
    
    return [bound_min, bound_max]

# Calculate plot bounds in [H+] space if one of the axes is pH
def calcpHbounds(bounds, val):
    
    # Determine the bounds in pH space
    pHwidth = max(bounds)-min(bounds)
    pHmargin = pHwidth * arrowMargin
    
    # Determine the bounds in [H+] space
    maxH = pH2H(min(bounds)+pHmargin)
    minH = pH2H(max(bounds)-pHmargin)
    
    # Convert the pH val to [H+]
    valH = pH2H(val)
    
    return [minH, maxH], valH
    
# Build process label
def buildLabel(text, arrowEnd, origin):
    # Figure out text alignment
    
    # default alignment
    ha = 'center'
    va = 'center'
    
    if arrowEnd[1]<origin[1]:
        va='top'
    elif arrowEnd[1]>origin[1]:
        va='bottom'
    elif arrowEnd[0]<origin[0]:
        ha='right'
    elif arrowEnd[0]>origin[0]:
        ha='left'  
    # Options for ha = 'center', 'right', 'left'
    # Options for va = 'center', 'top', 'bottom', 'baseline', 'center_baseline'
    
    labelDict = {
            'x':    arrowEnd[0],
            'y':    arrowEnd[1],
            's':    text,
            'ha':   ha,
            'va':   va
            }
    
    return labelDict

# %%
"""
------------------
MAIN FUNCTION
------------------
"""

if __name__ == '__main__':
    
    # Get data from the user
    [data, infilename] = getCSV("Select combined PHREEQC output csv file")
    # Use this if need to reset data while troubleshooting
    # data = getData(infilename)
    
    # Build plot(s)
    newplot = "Y"
    while newplot == "Y" :
        newplot = input("Build a new plot? Y/N >  ")
        if newplot != "Y":
            break
        # Create the data matrix to plot
        [matrix3D, xyVals, var_vals, mineral] = buildMatrixFromTable(data)
        # Build the plot
        plot_contour(matrix3D, xyVals, var_vals, mineral)
