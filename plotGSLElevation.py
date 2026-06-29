# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 15:59:22 2026

@author: cariefrantz

Builds plots of Great Salt Lake elevation in the context of historical trends.
- Downloads data from USGS.
- Calculates min/max and time-weighted mean & 95th % ranges for selected timeperiods.
- Builds and saves a static plot with selected historical references.
- Builds and saves an interactive (Bokeh) plot in web (HTML) format with
    selected historical references.

"""

####################
# IMPORTS
####################
import os
import io
import requests
import matplotlib.pyplot as plt
import pandas as pd
from pandas.tseries.offsets import DateOffset

# from bokeh.io import show
from bokeh.layouts import column
from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource, Div, HoverTool


####################
# VARIABLES
####################
directory = os.getcwd()     # Directory for saving the page

### Data Retrieval Variables (for USGS API)
station_id = "10010000"     # USGS Great Salt Lake at Saltair Boat Harbor, UT
parameter_code = "62614"    # Lake water surface elevation above NGVD29/NAVD88
today = pd.Timestamp.now().strftime("%Y-%m-%d") # Today's date
date_start = "1847-10-18"   # Start date for data grab
                            # Start of reconstructed history for Saltair
                            # is 1847-10-18
date_end = today            # End date for data grab; default = today
      
                      
### Data analysis time periods
# Dictionaries containing:
#   - years [start, end]
#   - colors for plotting [main (mean/percentile windows), light (min), dark (max)]
#   - list of parameters to plot in the static plot
#       (options are mean, min, max, range95 (95% range))
#   - list of parameters to plot in the interactive (bokeh) plot
#       (options are mean, min, max)
plotperiods = {
    'Preindustrial' : {
        'years'     : ['1850', '1900'],
        'colors'    : ['#8c96c6', '#b3cde3', '#88419d'],
        'static_plotlist'   : ['mean', 'min', 'max', 'range95'],
        'bokeh_plotlist'    : ['mean']
        },
    'Historical'    : {
        'years'     : ['1900', '2000'],
        'colors'    : ['#66c2a4', '#b2e2e2', '#238b45'],
        'static_plotlist'   : ['mean', 'min', 'max', 'range95'],
        'bokeh_plotlist'    : ['mean', 'min', 'max']
        },
    'Modern'        : {
        'years'     : ['2000', today],
        'colors'    : ['#fe9929', '#fed98e', '#cc4c02'],
        'static_plotlist'   : ['mean', 'min', 'max', 'range95'],
        'bokeh_plotlist'    : []
        }
    }


### Static plot drawing parameters
elev_color = "royalblue"                                              
plt.rcParams["svg.fonttype"] = "none"   # This gets plots to save
                            # files with editable text (text as strings)
                            
### Interactive HTML (Bokeh) plot variables
# Plot formatting
plt_ht = 5
plt_w = 10
mkrsize = 5
linew = 4
alpha = 0.5
toolset = 'box_zoom, xwheel_zoom, pan, reset, save'
active_drag = 'box_zoom'
active_inspect = 'auto'
active_scroll = 'xwheel_zoom'
active_tap = 'auto'

# HTML page formatting
HTML_head = ('''
<h1>Great Salt Lake South Arm Elevation</h1>
<p>Daily mean lake water surface elevation above ngvd 1929 from the USGS
National Water Information System / USGS Utah Water Science Center
<br />Elevation measured at Saltair Boat Harbor, 
<a href="https://waterdata.usgs.gov/monitoring-location/10010000/">
Station 10010000</a></p>
<p>Plot by Dr. Carie Frantz,
<a href="https://www.weber.edu/ees">Department of Earth and Environmental 
Sciences</a>, Weber State University, using Python script
<a href="https://github.com/cmfrantz/GSLMO">plotGSLElevation.py</a></p>
<p>Definitions: Preindustrial is defined as '''
 + plotperiods['Preindustrial']['years'][0] + '–'
 + plotperiods['Preindustrial']['years'][1] + '.'
 + ' Historical is defined as '
 + plotperiods['Historical']['years'][0] + '–'
 + plotperiods['Historical']['years'][1] + '.</p>'
 #+ '''
 #<p>Data type key (display using the Hover tool):
 #<ul>
 #<li>A &emsp; Approved for publication — Processing and review completed.
 #</li>
 #<li>P &emsp; Provisional data subject to revision.</li>
 #<li>e &emsp; Value has been estimated.</li>
 #<li>Eqp &emsp; Value affected by equipment malfunction.</li>
 #</ul>
 #</p>
#'''
)
HTML_newmin = [
    '<h2>New minimum: ',
    ' ft reached on ',
    ('''
        </h2>
        <p><b>Use the toolbars to the right of the plot to scroll/zoom and display
        daily mean values.</b></p>
        <p>Plot last updated 
        '''
        + today + '.</p>')
    ]
    

####################
# FUNCTIONS
####################   

def fetchData(station_id = station_id, parameter_code = parameter_code,
              date_start = date_start, date_end = date_end):
    '''
    Retrieves elevation data from the USGS.

    Parameters
    ----------
    station_id : str (optional)
        ID string (8-digit) for the station to retrieve.
        The default is the station id defined in the initial file variables.
    parameter_code : str (optional)
        USGS API parameter code for the elevation parameter to retrieve.
        The default is the station id defined in the initial file variables.
    date_start : date str (optional)
        The start date for the data grab in YYYY-mm-dd format.
        The default is defined in the initial file variables.
    date_end : date str (optional)
        The start date for the data grab in YYYY-mm-dd format.
        The default is today's date.

    Raises
    ------
    Exception
        Raises an error if no data is found for the station id and parameter code.
    ValueError
        Raises an error if the parameter code is not found in the downloaded data.

    Returns
    -------
    df : pandas.DataFrame
        Table containing the values for the selected parameters.
        Returned columns are Date, Elevation, and Quality_Code.

    '''
    
    # Fetch data from USGS website
    url = (
           f"https://waterservices.usgs.gov/nwis/dv/"
           f"?format=rdb"
           f"&sites={station_id}"
           f"&parameterCd={parameter_code}"
           f"&startDT={date_start}"
           f"&endDT={date_end}"
           )
    
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch data from USGS. Status code: {response.status_code}..."
            )
    
    # Parse the returned RDB format
    # Filter out comments (lines starting with '#')
    lines = response.text.splitlines()
    data_lines = [line for line in lines if not line.startswith("#")]
    
    if len(data_lines) < 2:
        # Return error if no data
        print(
            f"No data returned for site {station_id} with parameter {parameter_code}"
            )
        df = pd.DataFrame()
    else:
        # Extract the header row and skip the row-definition column
        header = data_lines[0]
        records = data_lines[2:]
        clean_tsv_data = "\n".join([header] + records)
        # Convert tsv to csv
        raw_df = pd.read_csv(io.StringIO(clean_tsv_data), sep="\t")
        
    # Dynamically isolate and clean columns
    # USGS column headers for values contain the parameter code but append a statistic suffix (e.g., '_62614_00003')
    val_col = [
        col
        for col in raw_df.columns
        if f"_{parameter_code}_" in col and not col.endswith("_cd")
    ]
    cd_col = [
        col
        for col in raw_df.columns
        if f"_{parameter_code}_" in col and col.endswith("_cd")
    ]

    # Flexible fallback if the column string structure differs
    if not val_col:
        val_col = [
            col
            for col in raw_df.columns
            if parameter_code in col and not col.endswith("_cd")
        ]
        cd_col = [
            col
            for col in raw_df.columns
            if parameter_code in col and col.endswith("_cd")
        ]

    if not val_col:
        raise ValueError(
            f"Could not locate value column matching parameter code {parameter_code}"
        )

    # Standardize the DataFrame
    df = pd.DataFrame()
    df["Date"] = pd.to_datetime(raw_df["datetime"])
    df["Elevation"] = pd.to_numeric(raw_df[val_col[0]], errors="coerce")
    if cd_col:
        df["Quality_Code"] = raw_df[cd_col[0]]

    # Drop any records with missing elevation data and sort chronologically
    df = df.dropna(subset=["Elevation"]).sort_values("Date").reset_index(drop=True)

    print(f"Successfully loaded {len(df)} records into the DataFrame.")

    return df



def interpolateElev(elev_data):
    '''
    Resamples elevation data to return resampled daily data and interpolated
    weekly elevation data.

    Parameters
    ----------
    elev_data : pandas.DataFrame
        Table of elevation values. Must contain the columns "Date" and "Elevation".

    Returns
    -------
    elev_data_daily :  pandas.DataFrame
        Table of daily elevation values for the entire date range.
    elev_interp_weekly :  pandas.DataFrame
        Table of interpolated weekly elevation values.

    '''
    elev_data["Elevation"] = pd.to_numeric(elev_data["Elevation"], errors="coerce")
    data = elev_data[["Date","Elevation"]].set_index("Date")
    
    # Resample to daily
    elev_data_daily = data.resample('D').mean()
    elev_data_daily["Date"] = [str(dt)[:10] for dt in
                               elev_data_daily.index.values]
    
    # Interpolate & calculate time-weighted average
    interp_d = elev_data_daily["Elevation"].interpolate()
    elev_interp_weekly = interp_d.resample('W').mean()
    elev_interp_weekly.index = elev_interp_weekly.index + DateOffset(days=-3)
    elev_interp_weekly = elev_interp_weekly.to_frame(name = "Elevation")
    elev_interp_weekly["Date"] = [str(dt)[:10] for dt in
                                  elev_interp_weekly.index.values]
    
    return elev_data_daily, elev_interp_weekly



def calcStats(elev_data_daily, elev_interp_weekly, date_start, date_end):
    '''
    Calculates mean, min, max values and 95th percentile ranges
    for the specified date range.

    Parameters
    ----------
    elev_data_daily : pandas.DataFrame
        Table of daily elevation values.
        Must contain the columns "Date" and "Elevation".
    elev_interp_weekly: pandas.DataFrame
        Table of weekly interpolated elevation values.
        Must contain the columns "Date" and "Elevation".
    date_start : date str
        Start date for the period (selects values >= this date).
        Can be in format "YYYY" or "YYYY-mm-dd".
    date_end :  date str
        End date for the period (selects values < this date).
        Can be in format "YYYY" or "YYYY-mm-dd".

    Returns
    -------
    elev_mean : float
        Mean elevation for the date range.
    elev_min : float
        Minimum elevation for the date range.
    elev_max : float
        Maximum elevation for the date range.
    elev_lower95 : float
        lower bound for the 95th percentile range for the date range.
    elev_upper95 : float
        upper bound for the 95th percentile range for the date range.

    '''
    # Find max and min from daily station measurements
    d_vals = elev_data_daily.loc[
        (elev_data_daily["Date"] >= date_start) &
        (elev_data_daily["Date"] < date_end), "Elevation"].copy()
    
    elev_min = d_vals.min()
    elev_max = d_vals.max()
    
    # Calculate mean & 95th percentile ranges from weekly interpolated values
    # for a time-weighted average
    w_vals = elev_interp_weekly.loc[
        (elev_interp_weekly["Date"] >= date_start) &
        (elev_interp_weekly["Date"] < date_end), "Elevation"].copy()
    elev_mean = round(w_vals.mean(), 1)
    elev_lower95 = round(w_vals.quantile(0.025), 1)
    elev_upper95 = round(w_vals.quantile(0.975), 1)
    
    return elev_mean, elev_min, elev_max, elev_lower95, elev_upper95



def buildRefPeriodDict(elev_data, plotperiods):
    '''
    Builds the dictionaries of reference elevation lines and range boxes
    based on the plotperiods defined in the initial variables
    to pass to the staticPlot function.

    Parameters
    ----------
    elev_data : pandas.DataFrame
        Table of elevation values. Must contain the columns "Date" and "Elevation".
    plotperiods : dict of dicts
        Dictionary where each 1st level entry is a timeperiod to plot, with
        nested dictionaries in the format:
            timeperiodlabel : {
                'years'     : ['start_yyyy', 'end_yyyy'],
                'colors'    : ['mean_color_value', 'min_color_value', 'max_color_value'],
                'plotlist'  : [list of stats to plot from 'mean', 'min', 'max', 'range95']
                }

    Returns
    -------
    h_lines : dict
        Dictionary containing information for all of the elevation reference
        lines to plot.
    h_boxes : dict
        Dictionary containing information for all of the elevation range
        reference boxes to plot.

    '''
    # Set up empty dictionaries to contain info for any horizontal lines or
    # range boxes to plot
    h_lines = {}
    h_boxes = {}
    
    # Go through each plot period timeperiod, calculate elevation statistics,
    # and build selected horizontal lines and 95% range boxes for the plot 
    for timeperiod in plotperiods:
        stats = plotperiods[timeperiod]['stats']
        colors = plotperiods[timeperiod]['colors']
        # Add each selected elevation line and range box to the list to plot
        for label in plotperiods[timeperiod]['static_plotlist']:
            if label == 'mean':
                h_lines[f"{timeperiod} {label}"] = [stats[0], colors[0]]
            if label == 'min':            
                h_lines[f"{timeperiod} {label}"] = [stats[1], colors[1]]
            if label == 'max':
                h_lines[f"{timeperiod} {label}"] = [stats[2], colors[2]]
            if label == 'range95':
                h_boxes[f"{timeperiod} 95% range"] = [stats[3:], colors[0]]
                
    return h_lines, h_boxes


def staticPlot(data, filename, figsize=(12,6),
               title = "Great Salt Lake Historical Elevation",
               years = "full", h_lines = None, h_boxes = None, legend = False):
    '''
    Produces and saves a plot of the elevation data as png and editable svg files.
    Use this by itself for no (or manual) elevation reference lines/boxes.

    Parameters
    ----------
    data : pandas.DataFrame
        Table containing the elevation data.
        Must include the columns "Date" and "Elevation".
    filename : str
        Name (prefix) for the image files to save.
    figsize : tuple, optional
        Dimensions (width, height) for the image. The default is (12,6).
    title : str, optional
        Title for the plot. The default is "Great Salt Lake Historical Elevation".
    years : str or list of int, optional
        Range of years to plot. The default is "full", which plots the full
        downloaded range of dates. Otherwise, specify a [min_year, max_year],
        for example: [1980, 2026]
    h_lines : dict, optional
        Dictionary containing any horizontal lines to plot. The default is None.
        Dict must take the form {"Line label": [elevation_value, color_hex]} for each line.
    h_boxes: dict, optional
        Dictionary containing any range boxes to plot. The default is None.
        Dict must take the form
        {"Box label": [[elevation_min, elevation_max], colorhex]} for each line.
    legend : bool, optional
        Whether to add a legend to the plot. The default is False.

    Returns
    -------
    None.

    '''
    plt.figure(figsize = figsize)
    plt.plot(data["Date"], data["Elevation"], label = "Lake Elevation",
             color=elev_color)
    
    # Add optional horizontal reference lines if provided
    if h_lines:
        for i, (label, vals) in enumerate(h_lines.items()):
            elev = vals[0]
            color = vals[1]
            plt.axhline(y=elev, label=f"{label} ({elev:.1f} ft)", color = color)
            
    # Add optional reference range boxes if provided
    if h_boxes:
        for i, (label, vals) in enumerate(h_boxes.items()):
            range_vals = vals[0]
            color = vals[1]
            plt.axhspan(
                ymin = range_vals[0],
                ymax = range_vals[1],
                color = color,
                alpha = 0.2,
                label = label
                )
            
    if years != "full":
        yr_start = pd.to_datetime(f"{years[0]}-01-01")
        yr_end = pd.to_datetime(f"{years[1]}-12-31")
        plt.xlim(yr_start,yr_end)
    
    plt.title("Great Salt Lake Elevation")
    plt.xlabel("Year")
    plt.ylabel("Elevation (Feet above sea level)")
    plt.grid(True, linestyle=":", alpha=0.5)
    
    if legend:
        plt.legend(loc="upper right")
    
    plt.tight_layout()
    plt.savefig(directory + '\\' + filename + ".png", dpi=300)
    plt.savefig(directory + '\\' + filename + ".svg", format="svg")
    print(f"Graph successfully saved as {filename}.png & .svg")
    
    

def appendNewminHTML(elev_data, HTML_head, HTML_newmin):
    '''
    Appends information about the lake's elevation minimum to the HTML header.'

    Parameters
    ----------
    elev_data : pandas.DataFrame
        Table containing the elevation data.
        Must include the columns "Date" and "Elevation".
    HTML_head : str
        HTML defining the page header.
    HTML_newmin : list of str
        HTML pieces for the lake elevation minumum. Must be a three-part list:
            Text preceding the elevation value
            Text between the elevation value and date when the min was reached
            End text
            [str, str, str]

    Returns
    -------
    HTML_head : str
        Updated HTML block.

    '''
    # Find min & date
    elev_min = elev_data["Elevation"].min()
    elev_min_date = elev_data[
        elev_data["Elevation"]==elev_min]["Date"][0]

    # Update HTML header
    HTML_head = (HTML_head + HTML_newmin[0] + str(elev_min) + HTML_newmin[1]
                 + elev_min_date + HTML_newmin[2])
    
    return HTML_head


    
def buildBokehPlot(elev_data_daily, elev_interp_weekly, HTML_head,
                   filename, plotperiods_wStats):
    # Find the date range
    datemin = elev_data["Date"].min()
    datemax = elev_data["Date"].max()
    
    # Format the data for plotting in Bokeh
    source = ColumnDataSource(data={
        'dt'      : elev_data_daily.index,
        'date'    : elev_data_daily["Date"],
        'elev'    : elev_data_daily["Elevation"],
        #'dtype'   : elev_data[col_dtype]
        })

    # Build the bokeh figure
    print('\nBuilding the Bokeh figure...')
    fig = figure(height = plt_ht*100, width = plt_w*100,
                 tools = toolset,
                 x_axis_type = 'datetime',
                 active_drag = active_drag, active_scroll=active_scroll,
                 active_tap = active_tap,
                 title = 'Great Salt Lake elevation measured at Saltair')
    fig.xaxis.axis_label = 'Date'
    fig.yaxis.axis_label = 'Lake elevation (ft)'

    # Add the historical min, average, max lines
    varorder = {
        'mean'  : 0,
        'min'   : 1,
        'max'   : 2
        }
    for tp in plotperiods:
        for var in plotperiods[tp]['bokeh_plotlist']:
            varnum = varorder[var]
            val = plotperiods[tp]['stats'][varnum]
            fig.line(
                [datemin, datemax],
                [val, val],
                color = plotperiods[tp]['colors'][varnum],
                line_width=linew, alpha=alpha,
                legend_label = f"{str(round(val,1))} ft ({tp} {var})"
                )

    # Add the station measurements
    meas = fig.circle(
        x='dt', y='elev', source = source, size = mkrsize, alpha = alpha,
        color=elev_color, legend_label = 'Station measurements'
        )

    
    # Add the interpolated weekly mean
    fig.line(
        elev_interp_weekly["Date"], elev_interp_weekly["Elevation"],
        color=elev_color, alpha=alpha,
        legend_label='Interpolated weekly mean elevation')

    # Configure the toolbar
    hover = HoverTool(
        tooltips=[
            ('date',        '@date'         ),
            ('elevation',   '@elev{0.0}'    ),
            #('data type',    '@dtype'       )
            ],
        mode='vline', renderers = [meas]
        )

    fig.add_tools(hover)
    fig.toolbar.active_inspect = None

    #show(fig)

    # Save HTML page
    HTML_head = appendNewminHTML(elev_data_daily, HTML_head, HTML_newmin)
    output_file(directory + '\\' + filename + '.html')
    save(column([Div(text = HTML_head),fig]))
    
    print(f"Interactive Bokeh plot successfully saved as {filename}.html")
    
#%%
####################
# MAIN
####################
if __name__ == '__main__':
    
    # Download the data from USGS
    elev_data = fetchData()
    
    # Calculate daily & weekly interpolated elevations
    elev_data_daily, elev_interp_weekly = interpolateElev(elev_data)
    
    # Calculate timeperiod stats
    for timeperiod in plotperiods:
        # Subset the data to the specified years in the timeperiod
        years = plotperiods[timeperiod]['years']
        plotperiods[timeperiod]['stats'] = calcStats(elev_data,
            elev_interp_weekly, years[0], years[1])
    
    
    # Build reference timeperiod stats, lines, & range boxes
    # Run this unless manually specifying the reference lines & boxes
    [h_lines, h_boxes] = buildRefPeriodDict(elev_data, plotperiods)
                
    # Static plot of the lake elevation and all selected lines/range boxes
    staticPlot(elev_data, 'GSL_Elevation',
               h_lines = h_lines, h_boxes = h_boxes, legend = True)
    
    # Bokeh plot of the lake elevation
    buildBokehPlot(elev_data_daily, elev_interp_weekly, HTML_head,
                   'GSL_Elevation', plotperiods)
    
    
