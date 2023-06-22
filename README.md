# GSL
Great Salt Lake data analysis scripts used for Great Salt Lake Microbialite Observatory data processing
by Carie Frantz cariefrantz@weber.edu

## List of scripts
<table>
<tr><th>Script</th><th>Description</th><th>Data files used</th><th>Other requirements</th></tr>
<tr><td>DataProcessing.py</td><td>Master data processing script. Builds <a href="https://faculty.weber.edu/cariefrantz/GSL/GSLMO_plots_bokeh.html">HTML page</a> of static and <a href="https://docs.bokeh.org">bokeh</a> interactive plots for GSLMO website updating. Updates web files with new logger data. Right now it only plots HOBO data.</td><td>Files on faculty page: SiteA_combined.csv, SiteB_combined.csv, LakeElevationSaltair.csv, plus raw offloaded HOBO csv files</td><td>StationWeather.py code must be edited to add API keys before using this script.</td></tr>
<tr><td>GSL_equation_of_state.py</td><td>Uses the Naftz et al. (2011) equation of state to convert measured density values to salinity and vice versa.</td><td>none</td><td>Scripts require either density or salinity and temperature values.</td></tr>
<tr><td>format_field_data.py</td><td>Formats downloaded field metadata file for use in plot_timeseries.py script.</td><td>Downloaded field data csv file</td><td></td></tr>
<tr><td>plotGSLElevation.py</td><td>Builds an <a href="https://faculty.weber.edu/cariefrantz/GSL/GSL_elevation.html">HTML page</a> with an interactive <a href="https://docs.bokeh.org">bokeh</a> plot of Great Salt Lake elevation from USGS data</td><td></td><td>ResearchModules.py</td></tr>
<tr><td>merge_depths.py</td><td>Compares manual measurements to USGS logged lake depth measurements</td><td>Elevation files downloaded from USGS for Saltair and Causeway sites, manual field measurements</td><td></td></tr>
<tr><td>timeseries_summary_plots.py</td><td>Creates timeseries plots for compiled GSL data over different timeperiods, and generates data summary file.</td><td>Data files for lake elevation, HOBO logs, field metadata</td><td>ResearchModules.py</td></tr>
<tr><td>process_timeseries.py</td><td>Plots and summarizes GSLMO timeseries data over full data interval, and creates HTML dashboard.</td>Combined, quality-checked files for all HOBO data loggers plus lake elevation data<td></td><td>ResearchModules.py</td></tr>
<tr><td>timeseries_daily_summary_table.py</td><td>Condenses timeseries data to daily data</td><td>timeseries-data.xlsx (Spreadsheet containing all of the compiled timeseries)</td><td>ResearchModules.py</td></tr>
<tr><td>WUNDERScrape.py</td><td>Scrapes the <a href="https://www.wunderground.com">Weather Underground</a> website for a personal weather station to download daily data for a date range.</td><td></td><td>This script worked with wunderground.com PWS page formatting on 6/30/2021. Any changes to the page HTML may break this script.</td></tr>
<tr><td>WUNDERCompare.py</td><td>Generates a <a href="https://faculty.weber.edu/cariefrantz/GSL/WUNDERplots.html">website</a> with interactive <a href="https://docs.bokeh.org">bokeh</a> plots from scraped <a href="https://www.wunderground.com">Weather Underground</a> data generated by WUNDERScrape.py. Allows easy and pretty comparison of data from different stations.</td><td>A set of wu_STATION.csv files generated by WUNDERScrape.py</td><td></td></tr>
<tr><td>combine_weather_stations.py</td><td>Combines scraped weather station data from two stations to generate a continuous record of pressure</td><td>Two scraped weather CSV files generated by WUNDERScrape.py</td><td></td></tr>
<tr><td>precip_totals.py</td><td>Determines daily precipitation totals from scraped weather data</td><td>Weather station data from WUNDERScrape.py</td><td></td></tr>
<tr><td>core_data_analysis.py</td><td>For the GSL microbialite desiccation project: creates summary figure looking at the different core depths sampled at different timepoints.</td><td>bio_meas.xlsx (Compiled bio measurements spreadsheet)</td><td>ResearchModules.py</td></tr>
<tr><td>bio_res_pearson.py</td><td>Calculates Pearson correlation statistics for different parameters (microscopy, extract results) measured on biological samples as part of the GSL microbialite desiccation project.</td><td>bio_meas.xlsx (Compiled bio measurements spreadsheet)</td><td>ResearchModules.py</td></tr>
<tr><td>BrightfieldColorProcess.ijm</td><td>Script measures green area in brightfield photomicrographs in a directory.</td><td>All brightfield photomicrograph images (*.tif)</td><td>ImageJ macro</td></tr>
<tr><td>ConfocalColorProcess.ijm</td><td>Script measures fluorescent area in each channel in *.oir multichannel images.</td><td>All confocal photomicrographs (*.oir)</td><td>ImageJ macro</td></tr>
<tr><td>micr_exposure_paper.py</td><td>Script processes lake elevation and microbialite mapping data to perform analyses and generate figures used in the 2023 Great Salt Lake Microbialite Extent manuscript.</td><td>tsv table of daily average lake elevation data, csv table of mapped microbialite areas in different elevation bands.</td><td>Researchmodules.py</td></tr>
</table>

## Shared scripts
The following scripts are called by several of the main scripts listed above. Download these to the same directory as the scripts above.
<table>
<tr><th>Script</th><th>Description</th></tr>
<tr><td>ResearchModules.py</td><td>Common functions used by multiple other scripts.</td></tr>
</table>

## Setting up & running
### Python scripts (*.py)
#### Packages
The code for this project uses the following list of packages in order to run. Different scripts use different packages.
<ul>
	<li>beautifulsoup4</li>
	<li>bokeh</li>
	<li>datetime</li>
	<li>math</li>
	<li>matplotlib</li>
	<li>numpy</li>
	<li>os</li>
	<li>pandas</li>
	<li>plotly</li>
	<li>progress</li>
	<li>requests</li>
	<li>scipy</li>
	<li>seaborn</li>
	<li>sklearn</li>
	<li>subprocess</li>
	<li>sys</li>
	<li>time</li>
	<li>tkinter</li>
</ul>

To install using conda, execute the command:

	conda install tkinter
	conda install progress
	
...and so on

To install using pip, execute the command:

	pip install tkinter
	pip install progress
	
...and so on

#### Running
Once python and the packages listed above have been installed, to run a script from command line, execute the command:

	python DensityDiff.py
	python WebTaxBarplotsSimple.py
	
...and so on

### ImageJ macros (*.ijm)
<ol>
<li>Install ImageJ. I recommend the <a href="https://imagej.net/software/fiji/downloads">Fiji package</a>.</li>
<li>Download the macros and image files to seperate folders.</li>
<li>In ImageJ, Plugins -> Macros -> Run..., select the macro file, then select the directory containing the iamges to process.</li>
</ol>
