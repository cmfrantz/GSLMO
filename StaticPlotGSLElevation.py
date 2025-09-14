# -*- coding: utf-8 -*-
"""
Created on Sat Jul 24 10:21:06 2021
Refactored in 2024 to simplify and focus on a static matplotlib plot.

@author: cariefrantz

This script plots the historical and recent lake elevation of the Great
Salt Lake's South Arm, using data from a manually-downloaded USGS data file.

The final output is a static plot saved as 'GSL_Elevation.png' and
'GSL_Elevation.svg'.
"""

####################
# IMPORTS
####################
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date

####################
# VARIABLES
####################

# --- Data Sources ---
# Local file containing the manually-downloaded USGS data.
# This should be a tab-separated file.
LOCAL_DATA_FILE = "dv.txt"

# --- Data Column Names ---
# This column name is used for the data after being processed from the USGS.
COL_ELEV_FT = 'elevation_ft'

# --- Data Analysis Periods ---
PI_START = '1850'  # Start of 'pre-industrial' period
PI_END = '1900'    # End of 'pre-industrial' period
HIST_START = '1900' # Start of 'historical' period
HIST_END = '2000'   # End of 'historical' period

# --- Plot Formatting ---
FIG_SIZE = (12, 6)
MARKER_SIZE = 5
LINE_WIDTH = 2
ALPHA = 0.6
FONT_SIZE = 12
plt.rcParams.update({'font.size': FONT_SIZE})

# --- Plot Date Range ---
# Set to None to plot the full date range available in the data.
# Or, set specific start and end dates as strings, e.g., '2000-01-01'.
today = date.today()
today_str = today.strftime("%Y-%m-%d")
PLOT_START_DATE = '2015-01-01'
PLOT_END_DATE = today_str

# --- Plot Y-Axis Scaling ---
# Controls the Y-axis limits.
# - 'auto': Automatically scales to the data within the specified plot date range.
# - [min, max]: A list specifying the exact min and max for the Y-axis (e.g., [4189, 4200]).
# - None: Scales to the full range of the entire dataset.
Y_AXIS_SETTING = [4188,4200]

# --- Context Markers ---
# Set to True to add lines showing historical ranges
HIST_MIN = False
HIST_MAX = False
HIST_MEAN = False
PI_MEAN = False
MGMT_RANGE = True

####################
# CODE
####################

# --- 1. DATA LOADING AND PREPARATION ---

# Load the data from the local, manually-downloaded file.
print(f"Loading data from local file: {LOCAL_DATA_FILE}...")
try:
    # Define column names for the tab-separated data file.
    col_names = ['agency', 'site_no', 'date', COL_ELEV_FT, 'code']

    # Read the tab-separated file.
    # The 'comment' parameter skips the initial header block from the USGS file.
    # 'header=None' is used because the data itself doesn't have a header row.
    usgs_df = pd.read_csv(
        LOCAL_DATA_FILE,
        sep='\t',
        comment='#',
        header=None,
        names=col_names
    )

    # The file may contain extra descriptive lines after the comments.
    # The actual data rows start with 'USGS' in the first column.
    usgs_df = usgs_df[usgs_df['agency'] == 'USGS'].copy()

    # Convert date strings to datetime objects and set as the index
    usgs_df['date'] = pd.to_datetime(usgs_df['date'])
    usgs_df.set_index('date', inplace=True)

    # Convert the elevation column to a numeric type, forcing errors to NaN
    usgs_df[COL_ELEV_FT] = pd.to_numeric(usgs_df[COL_ELEV_FT], errors='coerce')

    # Create the final dataframe with just the elevation data
    combined_elev = usgs_df[[COL_ELEV_FT]]

    # Clean up the final dataset
    combined_elev.sort_index(inplace=True)
    combined_elev.dropna(subset=[COL_ELEV_FT], inplace=True)

except FileNotFoundError:
    print(f"Error: The data file '{LOCAL_DATA_FILE}' was not found in the same directory as the script.")
    combined_elev = pd.DataFrame(columns=[COL_ELEV_FT])
except Exception as e:
    print(f"Failed to load or process the local data file: {e}")
    # Create an empty dataframe to prevent the script from crashing
    combined_elev = pd.DataFrame(columns=[COL_ELEV_FT])


# --- 2. DATA ANALYSIS ---

if not combined_elev.empty:
    print("Analyzing data to find historical benchmarks...")
    # Resample to daily mean to fill any gaps for consistent analysis
    daily_elev = combined_elev.resample('D').mean()
    # Create an interpolated, weekly-averaged series for a smoother plot line
    weekly_interp = daily_elev.interpolate().resample('W').mean()

    # Calculate key historical values using the full dataset
    pi_mean = weekly_interp.loc[PI_START:PI_END, COL_ELEV_FT].mean()
    hist_mean = weekly_interp.loc[HIST_START:HIST_END, COL_ELEV_FT].mean()
    hist_min = combined_elev.loc[HIST_START:HIST_END, COL_ELEV_FT].min()
    hist_max = combined_elev.loc[HIST_START:HIST_END, COL_ELEV_FT].max()
    record_low = combined_elev[COL_ELEV_FT].min()
    record_low_date = combined_elev[COL_ELEV_FT].idxmin()

    print(f"  Pre-industrial Mean ({PI_START}-{PI_END}): {pi_mean:.1f} ft")
    print(f"  Historical Mean ({HIST_START}-{HIST_END}): {hist_mean:.1f} ft")
    print(f"  Historical Min ({HIST_START}-{HIST_END}): {hist_min:.1f} ft")
    print(f"  Historical Max ({HIST_START}-{HIST_END}): {hist_max:.1f} ft")
    print(f"  All-time Record Low: {record_low:.2f} ft on {record_low_date.strftime('%Y-%m-%d')}")


    # --- 3. PLOTTING ---

    print("\nBuilding the plot...")
    fig, ax = plt.subplots(figsize=FIG_SIZE)

    # Plot the interpolated weekly mean as the main trend line
    ax.plot(weekly_interp.index, weekly_interp[COL_ELEV_FT],
            color='midnightblue', linewidth=LINE_WIDTH,
            label='Interpolated Weekly Mean Elevation')

    # Plot the daily measurements as points for detail
    #ax.scatter(combined_elev.index, combined_elev[COL_ELEV_FT],
    #           color='lightblue', s=MARKER_SIZE,
    #           label='Daily Mean Elevation')

    # Add context markers
    if PI_MEAN:
        ax.axhline(pi_mean, color='gray', linestyle='--', linewidth=LINE_WIDTH, alpha=ALPHA,
                   label=f'Pre-industrial Mean ({pi_mean:.1f} ft)')
    if HIST_MEAN:
        ax.axhline(hist_mean, color='darkgrey', linestyle='--', linewidth=LINE_WIDTH, alpha=ALPHA,
                   label=f'Historical Mean ({hist_mean:.1f} ft)')
    if HIST_MAX:
        ax.axhline(hist_max, color='steelblue', linestyle=':', linewidth=LINE_WIDTH, alpha=ALPHA,
                   label=f'Historical Max ({hist_max:.1f} ft)')
    if HIST_MIN:
        ax.axhline(hist_min, color='crimson', linestyle=':', linewidth=LINE_WIDTH, alpha=ALPHA,
                   label=f'Historical Min ({hist_min:.1f} ft)')
    if MGMT_RANGE:
        ax.axhspan(4198, 4205, color = 'green', alpha=0.2, label = 'Healthy Lake Management Range (4198-4205 ft)')

    # Formatting the plot
    ax.set_title('Great Salt Lake Elevation (South Arm - Saltair Station 10010000)')
    ax.set_xlabel('Year')
    ax.set_ylabel('Lake Elevation (ft above NGVD 1929)')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Set the x-axis limits if a custom date range is provided
    if PLOT_START_DATE and PLOT_END_DATE:
        start_date = pd.to_datetime(PLOT_START_DATE)
        end_date = pd.to_datetime(PLOT_END_DATE)
        ax.set_xlim(start_date, end_date)

    # Set y-axis limits based on the Y_AXIS_SETTING variable
        if isinstance(Y_AXIS_SETTING, list) and len(Y_AXIS_SETTING) == 2:
            # Option 1: A manual range is specified, e.g., [4189, 4200]
            ax.set_ylim(Y_AXIS_SETTING[0], Y_AXIS_SETTING[1])
        elif Y_AXIS_SETTING == 'auto' and PLOT_START_DATE and PLOT_END_DATE:
            # Option 2: Autoscale to the data within the specified date range
            start_date = pd.to_datetime(PLOT_START_DATE)
            end_date = pd.to_datetime(PLOT_END_DATE)
            mask = (combined_elev.index >= start_date) & (combined_elev.index <= end_date)
            ranged_data = combined_elev.loc[mask]
    
            if not ranged_data.empty:
                min_elev = ranged_data[COL_ELEV_FT].min()
                max_elev = ranged_data[COL_ELEV_FT].max()
                # Add 5% padding for better visibility
                padding = (max_elev - min_elev) * 0.05
                ax.set_ylim(min_elev - padding, max_elev + padding)
        # Option 3: Y_AXIS_SETTING is None or invalid, so matplotlib's default full-scale is used.

    ax.legend(loc='lower left')
    fig.tight_layout()

    # --- 4. SAVING THE PLOT ---

    try:
        print("Saving figures to 'GSL_Elevation.png' and 'GSL_Elevation.svg'...")
        # Prevent font issues in SVG files for editing
        plt.rcParams['svg.fonttype'] = 'none'
        fig.savefig('GSL_Elevation.svg', format='svg')
        fig.savefig('GSL_Elevation.png', format='png', dpi=300)
        print("Script finished successfully.")
    except Exception as e:
        print(f"Could not save the plot. Error: {e}")

    # To display the plot if running in an interactive environment (e.g., Jupyter)
    # plt.show()
else:
    print("\nNo data was loaded. Skipping analysis and plotting.")

