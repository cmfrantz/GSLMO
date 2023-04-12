# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 09:25:06 2023

@author: cariefrantz

Builds figures for 2023 microbialite exposure paper

Input requirements:
    
    TSV table of daily average lake elevation data
    
    CSV table of microbialite exposure data with columns
        ELEVATION | HighLow | NorthSouth | SUM_Shape_Area
        (and any additional rows deleted)
        Elevation values represent the lower bound in 1 ft lake elevation
        increments.
        HighLow is the confidence level for the mapped shape area.
        NorthSouth is the arm of the lake.
        SUM_Shape_Area is the area of microbialites (in m^2) found between
        the elevation for that row and and 1' higher.
"""

####################
# IMPORTS
####################
import ResearchModules as rm
import numpy as np
import pandas as pd
from pandas.tseries.offsets import DateOffset
import sklearn.linear_model as skmodel
import seaborn as sns
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

####################
# VARIABLES
####################

# Formatting
# Nine shades of different colors from ColorBrewer2.0
cb_colors = {
    'reds'      : ['#67000d','#a50f15','#cb181d','#ef3b2c','#fb6a4a',
                   '#fc9272','#fcbba1','#fee0d2','#fff5f0'],
    'greens'    : ['#00441b','#006d2c','#238b45','#41ab5d','#74c476',
                   '#a1d99b','#c7e9c0','#e5f5e0','#f7fcf5'],
    'pinks'     : ['#67001f','#980043','#ce1256','#e7298a','#df65b0',
                   '#c994c7','#d4b9da','#e7e1ef','#f7f4f9'],
    'blues'     : ['#08306b','#08519c','#2171b5','#4292c6','#6baed6',
                   '#9ecae1','#c6dbef','#deebf7','#f7fbff']
    }
paper_colors = {
    'blues'     : ['#5f6d7c','#627e96','#5286aa','#7398b7','#92acc5',
                   '#b3c3d5','#d6dde7'],
    'greens'    : ['#4d5249','#5e6c51','#657f4c','#5f8d3d','#7c9c59',
                   '#98af7b','#b7c4a0'],
    'pinks'     : ['#8a4340','#aa4c64','#d5769c']
    }
# Colors to actually use in the figures
colors = {
    'all'       : paper_colors['blues'][0],
    'high'      : paper_colors['blues'][2],
    'low'       : paper_colors['blues'][4],
    'NA all'    : paper_colors['pinks'][0],
    'NA high'   : paper_colors['pinks'][1],
    'NA low'    : paper_colors['pinks'][2],
    'SA all'    : paper_colors['greens'][0],
    'SA high'   : paper_colors['greens'][2],
    'SA low'    : paper_colors['greens'][5],
    }

figw = 10
figh = 5
figsize = [figw,figh]

# Data parsing
datefmt = '%Y-%m-%d'
smooth_over = 'Q'

# Lake elevation file
elev_row_head = 31
elev_col_date = '20d'
elev_col_elev = '14n'

# Microbialite exposure file (areas in m2)
expos_row_head = 0
expos_col_elev = 'ELEVATION'
expos_col_conf = 'HighLow'
expos_col_arm = 'NorthSouth'
expos_col_area = 'SUM_Shape_Area'
labels = {
    'NA high'   : ['High','North'],
    'NA low'    : ['Low','North'],
    'SA high'   : ['High','South'],
    'SA low'    : ['Low','South']
    }

# Previous maps
micr_maps_summary_km2 = pd.DataFrame(
    index=['Eardley','Baskin','Vanden Berg', 'Bouton'],
    data=np.array([
        [117, 160, np.nan],
        [700,300,np.nan],
        [56,92,np.nan],
        [np.nan,np.nan,1261]
        ]),
    columns=['South Arm','North Arm','Total'])


####################
# SCRIPTS
####################

def importData():
    '''
    Imports lake elevation and microbialite exposure data from files

    Returns
    -------
    elev_data_rs : Series
        List of elevation values interpolated/smoothed over the range defined.
    expos_data : pandas.DataFrame
        Data for microbialite exposure at different confidence levels for each
        elevation level in the dataset.

    '''

    # Lake elevation
    # Grab file
    # lake_elev = rm.download_lake_elevation_data(
    #    '1847-10-18', date.today().strftime(datefmt), '1001000', 28)
    elev_file, dirpath, elev_data = rm.fileGet(
        'Lake elevation tsv', file_type='tsv', header_row=elev_row_head)
    # Convert elevation data to numeric
    elev_data['elevation'] = pd.to_numeric(
        elev_data[elev_col_elev], errors='coerce')
    # Convert index values to timestamps
    elev_data['date'] = pd.to_datetime(elev_data[elev_col_date])
    elev_data['20d'] = elev_data['date'].dt.strftime('%Y-%m-%d')
    elev_data.set_index('date', drop=True, inplace=True) 
    elev_data = elev_data['elevation']
    # Interpolate & calculate time-weighted average
    elev_data_rs = elev_data.interpolate()
    elev_data_rs = elev_data_rs.resample(smooth_over).mean()
    elev_data_rs.index = elev_data_rs.index + DateOffset(days=-3)
    
        
    # Microbialite exposure
    # Import and trim file
    expos_file, dirpath, expos_file_data = rm.fileGet(
        'Microbialite exposure csv', directory=dirpath, file_type = 'csv',
        header_row = expos_row_head)
    # Set up the new dataframe
    elevations = list(set(expos_file_data.index))
    elevations = [x for x in elevations if str(x) != 'nan']
    expos_data = pd.DataFrame(index = elevations)
    for category in labels:
        expos_data[category] = expos_file_data[
            (expos_file_data[expos_col_conf]==labels[category][0])
            & (expos_file_data[expos_col_arm]==labels[category][1])
            ][expos_col_area]/1E6
    expos_data.fillna(0, inplace=True)
    expos_data['NA all'] = expos_data['NA high'] + expos_data['NA low']
    expos_data['SA all'] = expos_data['SA high'] + expos_data['SA low']
    expos_data['high'] = expos_data['NA high'] + expos_data['SA high']
    expos_data['low'] = expos_data['NA low'] + expos_data['SA low']
    expos_data['all'] = expos_data['high']+expos_data['low']
    expos_data = expos_data[
        ['NA high','NA low','NA all',
         'SA high','SA low','SA all',
         'high','low','all']]
    expos_data.fillna(0, inplace=True)
    # Calculate exposures at each confidence level
    for arm in ['NA','SA','both']:
        for conf in ['high','low','all']:
            expos_data = calcExposure(expos_data, arm, conf)
            
    # Save updated file
    expos_data.to_csv(dirpath + '/ElevDataFmttd.csv')
    
    return dirpath, elev_data_rs, expos_data


def calcExposure(micr_expos_data, arm, conf_level):
    '''
    Calculates the total area and percent of microbialites exposed at different
    elevations from the elevation band data imported

    Parameters
    ----------
    micr_expos_data : pandas.DataFrame
        Table of exposure in each elevation band for each confidence level
    arm : str
        Lake arm to calculate for
    conf_level : str
        Confidence level to calculate for.

    Returns
    -------
    micr_expos_data : pandas.DataFrame
        Table of exposure with the columns 'tot_expos_' and '%expos_' added.

    '''
    if arm == 'both': pfx = ''
    else: pfx = arm + ' '
    
    # Find sum of all microbialite area at the confidence level
    area_total = micr_expos_data[pfx + conf_level].sum()
    
    # Find percent in each band
    micr_expos_data['%in_band_' + pfx + conf_level] = (
        micr_expos_data[pfx + conf_level]/area_total)
    
    # Find total exposed at each elevation
    micr_expos_data['tot_expos_' + pfx + conf_level] = np.nan
    for i, elev in enumerate(micr_expos_data.index):
        micr_expos_data.loc[elev, 'tot_expos_' + pfx + conf_level] = (
            micr_expos_data.iloc[i:][pfx + conf_level].sum())
        
    # Calc percent exposed at each elevation
    micr_expos_data['%expos_' + pfx + conf_level] = (
        micr_expos_data['tot_expos_' + pfx + conf_level]/area_total)
    
    return micr_expos_data


def polyBestFit(xdata, ydata, degree):
    '''
    Creates a polynomial best fit model of the exposure vs. elevation data
    at the confidence level given

    Parameters
    ----------
    xdata : series of float or int of length N
        x-axis data (e.g., elevation).
    ydata : series of float or int of length N
        y-axis data (e.g., total exposure)
    degree : int
        Degree of the polynomial equation to fit

    Returns
    -------
    fitvals : array of float
        Polynomial best fit coefficients.
    fitmodel : model
        Model of exposure vs. elevation.
    r2 : float
        R square value for the model vs the actual data.

    '''
    fitvals = np.polyfit(xdata, ydata, degree)
    fitmodel = np.poly1d(fitvals)
    r2 = np.corrcoef(ydata, fitmodel(xdata))[0,1]**2
    return fitvals, fitmodel, r2


def PoissonFit(elev, ydata):
    '''
    Generates a Poisson regression model for the data
    (initial tests = not a great fit)
    '''
    # Create and scale the elevation bins to represent elevation above minimum
    xmin = min(elev)
    xdata = [[el-xmin, el-xmin+1] for el in elev]
    # Create a new Poisson Regression model
    prmodel = skmodel.PoissonRegressor(max_iter=1000)
    # Train the model on the data
    prmodel.fit(xdata, ydata)
    # Determine the fit score (D^2, equivalent to R^2)
    score = prmodel.score(xdata,ydata)
    coeffs = prmodel.coef_
    return prmodel, score, coeffs


def logistic(x, L, x0, k, b):
    '''logistic function definition'''
    y = L / (1 + np.exp(-k * (x-x0))) + b
    return (y)


def logisticCurveFit(elev, ydata, elev_corr_factor):
    '''Logistic function data fitting
    Uses scipy's Curve Fit to fit a logistic function (s-curve) to the data
    Code modified from desertnaut/Brenlla's solution found here:
        https://stackoverflow.com/questions/55725139/fit-sigmoid-function-s-shape-curve-to-data-using-python
    '''
    # Mirror elevation data using elev_corr_factor (typically the max elev)
    elev_c = elev_corr_factor - elev
    
    # Mandatory initial guess for parameters
    L = max(ydata)                  # spread of the data
    b = np.median(elev_c)           # bias factor*
    #    * a true logistic function has its x-axis center at zero;
    #       this factor moves the x-axis to start at 0
    k = 1                           # curve steepness
    x0 = np.median(ydata)           # sigmoid center
    p0 = [L, b, k, x0]              # initial (guess) parameters
    
    # Find the optimized parameters (p_opt) for the best fit
    p_opt, p_covar = curve_fit(logistic, elev_c, ydata, p0, method='dogbox')
    
    # Calculate parameter errors
    p_error = np.sqrt(np.diag(p_covar))
    
    return p_opt, p_error
    

def calc_r2(y_meas, y_model):
    '''Calculate r2'''
    residuals = y_meas - y_model
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y_meas-np.mean(y_meas))**2)
    r2 = 1 - (ss_res/ss_tot)
    return r2
    


def findElevationBands(micr_expos_data, arm, conf_level):
    # Use a best fit polynomial model to calculate the elevations where each
    # exposure percentage is hit.
    # Get the model
    fitvals, fitmodel, r2 = polyBestFit(
        micr_expos_data.index.values,
        micr_expos_data['%expos_' + arm + ' ' + conf_level],
        6)
    modeled_exp = pd.DataFrame(
        index=np.arange(min(micr_expos_data.index.values),
                        max(micr_expos_data.index.values), 0.1).round(1))
    modeled_exp['%exp'] = fitmodel(modeled_exp.index.values).round(2)
    
    # Determine bands at which x% of microbialites are exposed
    percentages = pd.DataFrame(
        index=np.arange(0.1,1.1,0.1).round(1),data=np.nan,
        columns=['elevation'])
    for percent in percentages.index.values:
        percentages.loc[percent]['elevation'] = modeled_exp[modeled_exp['%exp']==percent].index.values[0]
        
    
    return modeled_exp, percentages



def GSL_elevation_plot(ax, lake_elev, color='k'):
    ax.plot(lake_elev.index,lake_elev,color=color)
    ax.set_xlabel('Year')
    ax.set_ylabel('Lake elevation (ft asl)')
    
    return ax


def ft2m(ft):
    return 0.3048*ft

def m2ft(m):
    return 3.28084*m


        

# FIGURE 1B LAKE ELEVATION
def Figure1B(dirpath, lake_elev, micr_expos_data, conf_level,
             shade_color=colors['SA all'], alpha_factor=5, ylim=[4172,4216],
             figsize=[figh*2,figw]):
    
    fig, axs = plt.subplots(2,1,figsize=figsize)
    
    #Figure 1A: microbialite exposure at elevation
    # Plot GSL elevation
    axs[0] = GSL_elevation_plot(axs[0], lake_elev)    
    # Overlay gradient indicating percentage of microbialites exposed
    expos_interp = pd.DataFrame(
        index=np.arange(4172,4200,0.1).round(1),
        data=np.interp(
            np.arange(4172,4200,0.1), micr_expos_data.index,
            micr_expos_data['%expos_' + conf_level]).round(2),
        columns=['%exp'])
    for i, elev in enumerate(list(expos_interp.index)):
       if i==len(expos_interp)-1: val_max = 4200
       else: val_max = list(expos_interp.index)[i+1]
       axs[0].axhspan(
           elev, val_max,
           facecolor=shade_color, alpha=1-expos_interp.iloc[i]['%exp'])
    axs[0].set_ylim(ylim)
    ax2 = axs[0].secondary_yaxis('right', functions=(ft2m,m2ft))
    ax2.set_ylabel('Lake elevation (m asl)')
      
    #Figure 1B: microbialites by elevation band
    # Plot GSL elevation
    axs[1] = GSL_elevation_plot(axs[1], lake_elev)  
    # Overlay gradient indicating percentage of microbialites in that band
    for i, elev in enumerate(list(micr_expos_data.index)):
        if i==len(micr_expos_data)-1:   val_max = 4200
        else: val_max = list(micr_expos_data.index)[i+1]
        axs[1].axhspan(
            elev, val_max, facecolor = shade_color,
            alpha = (
                micr_expos_data.iloc[i]['%in_band_' + conf_level] *
                alpha_factor))
    axs[1].set_ylim(ylim)
    
    # Save figure
    fig.savefig(dirpath+'/Fig1B.png', transparent=True)
    fig.savefig(dirpath+'/Fig1B.pdf', transparent=True)
        

# FIGURE 4B ALL MAPS COMPARISON BAR PLOT
def Figure4B(dirpath, micr_expos_data, color_map, figsize=figsize):
    # Add Laura's map data to the table
    micr_maps_summary_km2.loc['Wilcock\n(high confidence)'] =  [
        micr_expos_data['SA high'].sum(),
        micr_expos_data['NA high'].sum(),
        np.nan]
    micr_maps_summary_km2.loc['Wilcock\n(all)'] = [
        micr_expos_data['SA high'].sum() + micr_expos_data['SA low'].sum(),
        micr_expos_data['NA high'].sum() + micr_expos_data['NA low'].sum(),
        np.nan]
    micr_maps_data = micr_maps_summary_km2.fillna(0)
    
    # Prep the data
    maplist = list(micr_maps_data.index)    
   
    fig, ax = plt.subplots(figsize=figsize)
    bottom = np.zeros(len(maplist))
    
    for n, arm in enumerate(micr_maps_data.columns):
        ax.bar(maplist, micr_maps_data[arm], 0.5, label=arm, bottom=bottom,
               color = color_map[n])
        bottom += micr_maps_data[arm]
        
    ax.legend(loc='upper left', frameon=False)
    ax.set_ylabel('Mapped microbialite extent (km2)')
    ax.set_xlabel('Map')
    
    # Save figure
    fig.savefig(dirpath+'/Fig4B.png', transparent=True)
    fig.savefig(dirpath+'/Fig4B.pdf', transparent=True)
    

# FIGURE 10 MICROBIALITE DISTRIBUTION HISTOGRAM
def Figure10(dirpath, micr_expos_data, figsize=[figw,figh*3]):
    fig, axs = plt.subplots(3,1,figsize=figsize)
    arms = ['NA','SA']
    ylabel = 'Mapped microbialite extent (km2)'
    xlabel = 'Elevation band (ft-asl)'
    legloc = 'upper right'
    
    # Build confidence level plots
    # for i, conf_level in enumerate(conf_levels):
    #     sfx = ' ' + conf_level
    #     for arm in arms:
    #         bottom = np.zeros(len(micr_expos_data))
    #         axs[i,0].bar(
    #             micr_expos_data.index, micr_expos_data[arm + sfx],
    #             0.5, bottom=bottom, color=colors[arm + sfx],
    #             label=arm)
    #         
    #         bottom = bottom +  micr_expos_data[arm + sfx].values
    #     axs[i,0].set_title(conf_level)
    #     axs[i,0].set_ylabel(ylabel)
    #     axs[i,0].set_xlabel(xlabel)
    #     axs[i,0].legend(loc=legloc, frameon=False)
        
    # Build arm category plots
    for i, arm in enumerate(arms):
        bottom = np.zeros(len(micr_expos_data))
        for conf_level in ['high','low']:
            sfx = ' ' + conf_level
            axs[i].bar(
                micr_expos_data.index,
                micr_expos_data[arm + sfx],
                0.5, bottom=bottom, color=colors[arm + sfx],
                label = arm + sfx + ' confidence')
            bottom = bottom + micr_expos_data[arm + sfx].values
        axs[i].set_title(arm)
        axs[i].set_xlabel(xlabel)
        axs[i].set_ylabel(ylabel)
        handles, labels = axs[i].get_legend_handles_labels()
        axs[i].legend(handles[::-1], labels[::-1], loc=legloc, frameon=False)
    
    # Build combined plot
    bottom = np.zeros(len(micr_expos_data))
    for arm in ['SA','NA']:
        for conf_level in ['high','low']:
            sfx = ' ' + conf_level
            axs[2].bar(
                micr_expos_data.index,
                micr_expos_data[arm + sfx],
                0.5, bottom=bottom, color=colors[arm + sfx],
                label = arm + sfx + ' confidence')
            bottom = bottom + micr_expos_data[arm + sfx].values
        axs[2].set_title('Whole lake')
        axs[2].set_xlabel(xlabel)
        axs[2].set_ylabel(ylabel)
        axs[2].legend(loc=legloc, frameon=False)
        
    # Save figure
    fig.savefig(dirpath+'/Fig10.png',transparent=True)
    fig.savefig(dirpath+'/Fig10.pdf', transparent=True)
            
        
         
            
        

# FIGURE 12 ELEV/EXPOSURE
def Figure12(dirpath, micr_expos_data, figsize=[figw,figh*3], polydeg=6):
    logistic_factors = pd.DataFrame(columns=['r2',
        'L','k','x0','b',
        'L_sterr','k_sterr','x0_sterr','b_sterr'])
    fig, axs = plt.subplots(3,1,figsize=figsize)
    elev = micr_expos_data.index
    for i, arm in enumerate(['NA','SA','both']):
        if arm == 'both': pfx = ''
        else: pfx = arm + ' '
        for conf in ['high','all']:
                 
            # Model data with polynomial best fit line
            # fitvals, fitmodel, r2 = polyBestFit(
            #     micr_expos_data.index,
            #     micr_expos_data['tot_expos_' + pfx + conf],
            #     degree = polydeg)
            
            # Model data with sigmoid function
            # y = L / (1 + np.exp(-k * (x-x0))) + b
            elev_corr_factor = max(elev)
            p_opt, p_error = logisticCurveFit(
                elev, micr_expos_data['tot_expos_' + pfx + conf],
                elev_corr_factor)
            # Calculate bestfit line
            y_bestfit = logistic(
                elev_corr_factor-elev,
                p_opt[0], p_opt[1], p_opt[2], p_opt[3])
            # Calculate r2
            r2 = calc_r2(micr_expos_data['tot_expos_' + pfx + conf], y_bestfit)
            # Save bestfit factors
            logistic_factors.loc[pfx + conf] = (
                [r2] + list(p_opt) + list(p_error))
            # Calculate error ranges
            y_max = logistic(
                elev_corr_factor-elev,
                p_opt[0] + p_error[0],
                p_opt[1] + p_error[1],
                p_opt[2] + p_error[2],
                p_opt[3] + p_error[3])
            y_min = logistic(
                elev_corr_factor-elev,
                p_opt[0] - p_error[0],
                p_opt[1] - p_error[1],
                p_opt[2] - p_error[2],
                p_opt[3] - p_error[3])
            
            # Build plots
            # Plot error ranges
            axs[i].fill_between(
                elev, y_max, y_min, color=colors[pfx+conf], alpha = 0.3)
            # Plot logistic curve bestfit
            axs[i].plot(elev, y_bestfit.values, color=colors[pfx + conf],
                        label = conf + ' logistic, r2 = ' + str(r2.round(3)))
            # Plot points
            axs[i].scatter(
                elev,
                micr_expos_data['tot_expos_' + pfx + conf],
                color=colors[pfx + conf],
                label=conf + ' confidence')
            
            # Plot 2022 low
            axs[i].axvline(x=4188.5, color='k', linestyle='--')
            axs[i].set_xlabel('Lake elevation (ft asl)')
            axs[i].set_ylabel('Area of exposed microbialites (km2)')
            axs[i].set_title(pfx + conf)
            #axs[i].set_ylim([0,math.ceil(max(y_max)/50)*50])
            axs[i].legend(loc='upper right', frameon=False)
            
    # Save plot
    plt.savefig(dirpath+'/Fig12.png',transparent=True)
    plt.savefig(dirpath+'/Fig12.pdf',transparent=True)
    # Save parameters
    logistic_factors.to_csv(dirpath+'/logistic_factors.csv')
            


# FIGURE A1 DISTRIBUTION STATISTICS
def FigureA1(dirpath, micr_expos_data, color):
    # Format dataset and calculate summary statistics
    plotlist = ['NA high','SA high','NA low','SA low','NA all','SA all','all']
    dsets = pd.DataFrame()
    summary = pd.DataFrame(index = plotlist, columns = [5,10,90,95,'mean','median'])
    for p in plotlist:
        a = prep_df_4boxplot(micr_expos_data, p)
        dsets = pd.concat([dsets,a], ignore_index = True, axis=1)
        b = np.percentile(a, [5,10,90,95])
        summary.loc[p] = np.append(b,[round(a.values.mean(),1),np.median(a)])
   
    summary.to_csv(dirpath+'/statistics.csv') 
        
    # Build plots
    fig, axs = plt.subplots(2,1,figsize=[figw,figh*2])
    sns.violinplot(data=dsets, color=color, ax=axs[0])
    sns.boxplot(data=dsets, color=color, ax=axs[1])
    axs[0].set_ylabel('Elevation (ft-asl)')
    axs[1].set_ylabel('Elevation (ft-asl)')
    plt.show()
    # Save plot
    fig.savefig(dirpath+'/FigA1.pdf',transparent=True)
    fig.savefig(dirpath+'/FigA1.png',transparent=True)
    
    
def prep_df_4boxplot(df, area_col, multfactor = 100):
    ''' Restructure the weighted dataframe for use in boxplots '''
    df = df[area_col]*multfactor
    df = df.astype(int)
    a = pd.DataFrame(df.index.repeat(df))
    return a  
    
    
    

            
    
#%%

####################
# CODE
####################

# Import data
dirpath, lake_elev, micr_exposure = importData()

# Generate all figures
Figure1B(dirpath, lake_elev, micr_exposure, 'all',
        shade_color=colors['SA all'], alpha_factor=7)
Figure4B(dirpath, micr_exposure, [colors['SA low'],colors['NA low'],'grey'])
Figure10(dirpath, micr_exposure)
Figure12(dirpath, micr_exposure)
FigureA1(dirpath, micr_exposure, 'gray')
