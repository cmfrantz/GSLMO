# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 10:12:33 2022
@author: cariefrantz
@project: GSLMO

Script plots compiled GSL timeseries data, including elevation data and
HOBO logger data.
"""

####################
# IMPORTS
####################
import ResearchModules
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


####################
# VARIABLES
####################
# Plot default variables
plotsize_default = (12,6)
resample_interval = '1d'
smooth_interval = '7d'

# Formatting for datetime axis
years = mdates.YearLocator()
months = mdates.MonthLocator()
years_fmt = mdates.DateFormatter('%Y')

# Plots to generate
plots = {
    'elev' : {
        'ytitle' : 'Lake elevation (ft asl)',
        'datasets' : {
            'elevation_Saltair' : {
                'file' : 'elevation_Saltair',
                'ycol' : '14n'
                },
            'elevation_Causeway' : {
                'file'  : 'elevation_Causeway',
                'ycol'  : '14n'
                }
        }
    },
    'temp' : {
        'ytitle' : 'Temperature (' + chr(176) + 'C)',
        'datasets' : {
            'Site A Pendant' : {
                'file' : 'site_A_pend',
                'ycol' : 'T_C'
                },
            'Site A Button A (top)' : {
                'file' : 'site_A_butt_A',
                'ycol' : 'T_C'
                },
            'Site B Pendant' : {
                'file' : 'site_B_pend',
                'ycol' : 'T_C'
                },
            'Site B Button B (top)' : {
                'file' : 'site_B_butt_B',
                'ycol' : 'T_C'
                },
            'Site B Button C (side)' : {
                'file' : 'site_B_butt_C',
                'ycol' : 'T_C'
                }
            }
        },
    'light' : {
            'ytitle' : 'Light intensity (lumen/ft2)',
            'datasets' : {
                'Site A Button A (top)' : {
                    'file' : 'site_A_butt_A',
                    'ycol' : 'Lux_lum_ft2'
                    },
                'Site B Button B (top)' : {
                    'file' : 'site_B_butt_B',
                    'ycol' : 'Lux_lum_ft2'
                    },
                'Site B Button C (side)' : {
                    'file' : 'site_B_butt_C',
                    'ycol' : 'Lux_lum_ft2'
                    }
                }
            },
    'pressure' : {
        'ytitle' : 'Absolute pressure (in Hg)',
        'datasets' : {
            'Site A Pendant' : {
                'file' : 'site_A_pend',
                'ycol' : 'P_abs'
                },
            'Site B Pendant' : {
                'file' : 'site_B_pend',
                'ycol' : 'P_abs'
                },
            }
        }
    }

# Datasets to draw from
files = {
    'elevation_Saltair' : {
        'title' : 'Elevation at Saltair (USGS)',
        'xcol'  : '20d',
        'datefmt' : '%m/%d/%Y %H:%M'
        },
    'elevation_Causeway' : {
        'title' : 'Elevation at Causeway (USGS)',
        'xcol'  : '20d',
        'datefmt'   : '%m/%d/%Y %H:%M'
        },
    'site_A_pend' : {
        'title' : 'Site A Pendant',
        'xcol'  : 'Datetime',
        'datefmt' : '%m/%d/%Y %H:%M'
        },
    'site_A_butt_A' : {
        'title' : 'Site A Button A (top)',
        'xcol'  : 'Datetime',
        'datefmt' : '%m/%d/%Y %H:%M'
        },
    'site_B_pend' : {
        'title' : 'Site B Pendant',
        'xcol'  : 'Datetime',
        'datefmt' : '%m/%d/%Y %H:%M'
        },
    'site_B_butt_B' : {
        'title' : 'Site B Button B (top)',
        'xcol'  : 'Datetime',
        'datefmt' : '%m/%d/%Y %H:%M'
        },
    'site_B_butt_C' : {
        'title' : 'Site B Button C (side)',
        'xcol'  : 'Datetime',
        'datefmt' : '%m/%d/%Y %H:%M'
        }
    }


#%%
####################
# MAIN FUNCTION
####################
if __name__ == '__main__':
    # Load in files
    dirpath = os.getcwd()
    for file in files:
        # Load in the file
        filename, dirpath, data = ResearchModules.fileGet(
            'Select file with data for ' + files[file]['title'], directory=dirpath)
        files[file]['data'] = data
    
    # Plot figures
    for plot in plots:
        # Create a new figure
        fig, ax = plt.subplots(figsize=plotsize_default)
        legend=[]
        
        # Plot each line
        for var in plots[plot]['datasets']:
            # Get the data
            file = plots[plot]['datasets'][var]['file']
            
            # Plot the data
            ResearchModules.plotData(
                files[file]['data'], files[file]['xcol'],
                plots[plot]['datasets'][var]['ycol'], 'Date',
                plots[plot]['ytitle'], var, ax=ax, plotsize=plotsize_default,
                smooth=True, xtype='datetime',
                datefmt=files[file]['datefmt'])
            
            # Add to legend
            legend.append(var)
            
        # Add the legend
        if len(legend)>1:
            ax.legend(legend)
        
        # Show and save the figure
        fig.show()
        fig.savefig(dirpath + '/' + plot + '.png')
        fig.savefig(dirpath + '/' + plot + '.svg')