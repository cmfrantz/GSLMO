# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 20:13:24 2021

@author: cariefrantz
@project: GSLMO

Scrapes weather history for a Weather Underground Personal Weather Station

This script does NOT require an API key, enabling the downloading of data
for any PWS of interest.

This script loads the daily data table for a site for each date in a user-
selected range, scrapes the data, and adds it to a csv file.
It saves a csv file containing all of the scrape-able data for the date range.

In order to ensure that data is available in the future (and limit your
carbon footprint) please use this script with care:
    1. Only download data you will use.
    2. Avoid needless queries: Prior to attempting to scrape data for a
    station, use the Graph view on the station website to determine the range
    where there is valid data prior to attempting to scrape data.

This script was created as part of the
Great Salt Lake Microbialite Observatory project

It was modified from a script by jumanbar posted at
https://stackoverflow.com/questions/55306320/

Arguments:
    station     (unique station identifier, e.g., KUTSYRAC22)
    date_start  (beginning date to find data for in format %Y-%m-%d,
                 e.g., 2019-01-30)
    date_end    (end date to find data for in format %Y-%m-%d,
                 e.g., 2021-06-29)

Example in command line:
    python WUNDERScrape.py

Dependencies Install:
    sudo apt-get install python3-pip python3-dev
    pip install requests
    pip install beautifulsoup4
    pip install datetime
    pip install time
    pip install tkinter


"""
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import tkinter as tk
from tkinter import filedialog


#######################
# GLOBAL VARIABLES
#######################

# Change these if the page HTML changes
date_fmt = '%Y-%m-%d' # Date format for the URL
table_no = 3 # Table number on the website
time_col = 0 # Column in the website table that contains the time

# Change this as desired
max_tries = 5 # Number of times to try to load a date before moving on


#######################
# FUNCTIONS
#######################

def scrape_page(file, station, date, header=True):
    '''
    Function scrapes the page for the input date and saves the data to the
    data file.

    Parameters
    ----------
    file : str
        The file path containing the csv to create or append.
    date : str
        The date, formatted as defined by the date_fmt variable.
    header : bool
        Whether or not to include the header row. The default is True.
        Setting header = False omits the header row.

    Raises
    ------
    ValueError
        If no data is found for the date (but the website otherwise loads),
        a ValueError is raised.

    Returns
    -------
    None.

    '''
    
    # Generate the URL string
    url = ('https://www.wunderground.com/dashboard/pws/'
           + station + '/table/' + date + '/' + date + '/daily')
           
    # Scrape the URL
    content = requests.get(url)
    soup = BeautifulSoup(content.text, 'html.parser')
    
    # Find the data table on the page
    tables = soup.find_all('table')
    data_table = tables[3]
    rows = data_table.findAll('tr')
     
    # Raise an error if there is no data for the date
    if len(rows)<3:
        raise ValueError('There is no data for ' + date + '.')
    
    # Save scraped data as csv-formatted text
    print('Saving data for ' + date + '...')
    out_file = open(file,'a',encoding='utf8')

    if header:
        # Get the header values (row 1)
        table_head = data_table.findAll('th')
        headers = []
        for head in table_head:
            headers.append(head.text.strip())
            
        # Append units to the header values
        firstrow = rows[2].findAll('td')
        for i,column in enumerate(firstrow):
            text = column.text.strip()
            text = text.rsplit('\xa0°')
            if len(text)>1:
                headers[i] = headers[i] + ' (' + text[1] + ')'
                
        # Write the header values
        out_file.write(','.join(headers) + '\n')
    
    # Write each row of data
    if len(rows)>2:
        for row in range(2, len(rows)):
            columns = rows[row].findAll('td')
            output_row = []
            for column in columns:
                text = column.text.strip()
                outtext = text.rsplit('\xa0°')[0]
                outtext = outtext.rsplit(' w/m²')[0]
                output_row.append(outtext)
            
            # Add the date to the time value
            output_row[time_col] = date + ' ' + output_row[time_col]
            
            # Add the row to the csv text
            out_file.write(','.join(output_row) + '\n')
    
    # Save the file
    out_file.close()
    
def get_weather_for_range(station, date_start, date_end, directory):
    '''
    This script scrapes weather data for each date within a date range
    from the Weather Underground station indicated and saves the combined file
    in the selected directory.

    Parameters
    ----------
    station : str
        Weather Underground station code, e.g., KUTSYRAC22
    date_start : str
       start date in the format 'yyyy-mm-dd'
    date_end : str
        end date in the format 'yyyy-mm-dd'
    directory : str
        directory where data should be saved

    Returns
    -------
    filename : str
        name of the combined data file

    '''
    print('\n*** Scraping Weather Underground for data from Station '
          + station + ' between ' + date_start
          + ' and ' + date_end + '. ***\n')
    
    filename = directory + '/wu_' + station + '.csv'
        
    # Loop through each date in the range and scrape the station's data
    dt_start = datetime.strptime(date_start, date_fmt)
    dt_end = datetime.strptime(date_end, date_fmt)
    dt_curr = dt_start
    header = True
    try_count = 0
    while dt_curr<=dt_end:
        # Scrape the Weather Underground data table page
        try:
            scrape_page(filename, station, dt_curr.strftime(date_fmt),
                        header = header)
        # If a ValueError is returned, skip to the next date
        except ValueError as e:
            print(e)
            dt_curr = next_day(dt_curr)
        # An IndexError indicates a problem with website loading
        except IndexError:
            if try_count < max_tries:
                # Wait and try again
                time.sleep(5)
                try_count += 1
            else:
                # After the max number of tries is reached, skip the date
                dt_curr = next_day(dt_curr)
                try_count = 0
        else:
            header = False
            dt_curr = next_day(dt_curr)
            
    return filename
    
    
def next_day(dt):
    ''' Advance the datetime value (dt) by one day '''
    nextday = dt + timedelta(days=1)
    return nextday

#%%
        
# MAIN
if __name__ == '__main__': 
    
    print('''
          *** This script scrapes weather data from Weather Underground ***
          ''')
    
    # Get input parameters from the user
    station = input('Enter the 10-digit station code (e.g., KUTSYRAC22)  > ')
    date_start = input('Enter the start date (format: 2020-02-28)  > ')
    date_end = input('Enter the end date (format: 2021-04-19)  > ')
        
    # Save the data table contents to a csv file in a user-selected directory
    root = tk.Tk()
    directory = filedialog.askdirectory(initialdir=os.getcwd())
    root.destroy()
    
    filename = get_weather_for_range(station, date_start, date_end, directory)

        
    print('\n*** All done! Data saved in ' + filename + ' ***')

