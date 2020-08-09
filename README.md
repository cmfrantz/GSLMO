# GSL
Great Salt Lake data analysis scripts
by Carie Frantz cariefrantz@weber.edu

## List of scripts
<table>
<tr><th>Script</th><th>Description</th><th>Data files used</th><th>Other requirements</th></tr>
<tr><td>DataProcessing.py</td><td>Master data processing script. Builds HTML pages of static and bokeh interactive plots for GSLMO website updating. Right now it only plots HOBO data. Code to import raw HOBO data, match it to weather station data, and update the compiled HOBO data files is in progress.</td><td>HOBO_SiteA.csv, HOBO_SiteB.csv, raw offloaded HOBO csv files</td><td></td></tr>
<tr><td>DensityDiff.py</td><td>Determines the relative difference that different water density assumptions make on the calculated lake depth from HOBO logger water pressure data and weather station air pressure data.</td><td>HOBO_SiteA.csv, HOBO_SiteB.csv</td><td></td></tr>
<tr><td>fanDiagram_2.6.py</td><td>Builds fan diagrams with process arrows from PHREEQC saturation calculations.</td><td>PHREEQC-Out.csv</td><td></td></tr>
<tr><td>fanDiagram_pH-T-points.py</td><td>Plots fan diagrams for all available minerals from PHREEQC saturation calculations. Overlays measured pH and T points from the field.</td><td>PHREEQC-Out.csv, GSL_FieldData.csv</td><td></td></tr>
<tr><td>StationWeather.py</td><td>Downloads weather station data from remote weather station. Requires valid API key for remote weather station to work, the version in this code is intentionally invalid for security purposes. Requires additional dependencies not listed below.</td><td></td><td>Requires valid weather station API key</td></tr>
</table>

## Shared scripts
The following scripts are called by several of the main scripts listed above. Download these to the same directory as the scripts above.
<table>
<tr><th>Script</th><th>Description</th></tr>
<tr><td>ResearchModules.py</td><td>Common functions used by multiple other scripts.</td></tr>
<tr><td>ResearchModules_old.py</td><td>Contains code for timeseries plots no longer used by DataProcessing script.</td></tr>
</table>

## Setting up
The code for this project requires the following list of packages in order to run.
<ul>
<li>bokeh</li>
<li>datetime</li>
<li>math</li>
<li>matplotlib</li>
<li>numpy</li>
<li>os</li>
<li>pandas</li>
<li>progress</li>
<li>subprocess</li>
<li>sys</li>
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

## Running
Once python and the packages listed above have been installed, to run a script from command line, execute the command:

	python DensityDiff.py
	python WebTaxBarplotsSimple.py
	
...and so on

## Future fixes
<ul>
<li>fanDiagram_2.6: The arrows and other features in the fanDiagram_2.6 script are acting up</li>
<li>DataProcessing:
  <ul>
  <li>Download weather data
    <ul>
    <li>Finish script</li>
	<li>If weather download gives a timeout, restart from another date/time</li>
	</ul>
	</li>
  <li>Combine HOBO & weather data</li>
  <li>Add in field data plots</li>
  </ul>
  </li>
</ul>