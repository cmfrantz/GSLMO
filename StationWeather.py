"""
DOWNLOAD AMBIENT STATION's WEATHER DATA

Arguments:
    Start Date                              (%Y-%m-%d),
    End Date                                (%Y-%m-%d),
    API Key                                 (String)

Example in command line (note that the API key here is not valid):
    python3 station_weather.py 2019-07-20 2019-07-21 35c8a41b05324137a0bc3d220d17c6182df7184953d148c4b8fc8cafe6e06192

Dependencies Install:
    sudo apt-get install python3-pip python3-dev
    pip3 install ambient_api
    pip3 install ambient_aprs
    pip3 install pandas
    pip3 install pytz

"""

import sys
import os
import argparse
from datetime import datetime, timedelta
from pytz import timezone
import codecs
import time
import subprocess
import csv
import pandas as pd

from ambient_api.ambientapi import AmbientAPI
from ambient_aprs.ambient_aprs import AmbientAPRS

AMBIENT_ENDPOINT = 'https://api.weather.com/v2'
# AMBIENT_ENDPOINT = 'https://api.ambientweather.net/v1'
AMBIENT_API_KEY = '35c8a41b05324137a0bc3d220d17c6182df7184953d148c4b8fc8cafe6e06192'
AMBIENT_APPLICATION_KEY = '6461626a535b439a93d828840b0a392aea18784125504f729e8e6e83b7dcaef4'
# CSV_FILES_PATH = 'weather-data/'
OUTPUT_PATH = '.'
DEBUG_MODE = True
#%%
##########################################################################
##  generate_csv()                                                      ##
##      Create CSV file                                                 ##
##                                                                      ##
##########################################################################
def generate_csv(content, lower, upper):
    lowerDate = datetime.fromtimestamp(lower).strftime('%Y%m%d')
    upperDate = datetime.fromtimestamp(upper).strftime('%Y%m%d')

    outputfile = open('{}/{}-{}.csv'.format(OUTPUT_PATH, lowerDate, upperDate), 'w', encoding="utf-8")
    outputfile.write('DateTime,Temp(℉),RelPressure(in),AbsPressure(in)\n')

    for element in content:
        strTime = datetime.fromtimestamp(element['dateutc'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
        temperature = element['tempinf']
        relpressure = element['baromrelin']
        abspressure = element['baromabsin']

        op = '{}'.format(strTime)
        op = '{},{}'.format(op, temperature)
        op = '{},{}'.format(op, relpressure)
        op = '{},{}'.format(op, abspressure)
        op = '{}\n'.format(op)
        outputfile.write(op)

    outputfile.close()
## EndDef generate_csv() ###

##########################################################################
##  generate_txt()                                                      ##
##      Create Text file                                                ##
##                                                                      ##
##########################################################################
def generate_txt(content, lower, upper):
    lowerDate = datetime.fromtimestamp(lower).strftime('%Y%m%d')
    upperDate = datetime.fromtimestamp(upper).strftime('%Y%m%d')

    outputfile = open('{}/{}-{}.txt'.format(OUTPUT_PATH, lowerDate, upperDate), 'w', encoding="utf-8")
    outputfile.write('DateTime\t\tTemp(℉)\tRelPressure(in)\tAbsPressure(in)\n')

    for element in content:
        strTime = datetime.fromtimestamp(element['dateutc'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
        temperature = element['tempinf']
        relpressure = element['baromrelin']
        abspressure = element['baromabsin']

        op = '{}'.format(strTime)
        op = '{}\t{}'.format(op, temperature)
        op = '{}\t{}'.format(op, relpressure)
        op = '{}\t{}'.format(op, abspressure)
        op = '{}\n'.format(op)
        outputfile.write(op)

    outputfile.close()
### EndDef generate_txt() ###

##########################################################################
##  amb_log()                                                           ##
##      Log to file                                                     ##
##                                                                      ##
##########################################################################
def amb_log(content):
    # print (content)
    logfile = open('amb_process.log', 'a+', encoding="utf-8")
    time = datetime.now().timestamp()
    strTime = datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
    logfile.write('{}  {}\n'.format(strTime, content))
    logfile.close()
### EndDef amb_log() ###

def amb_info(content):
    amb_log(content)
### EndDef amb_info() ###

def amb_debug(content):
    if DEBUG_MODE == False:
        return
    amb_log(content)
### EndDef amb_debug() ###

##########################################################################
##  clear_log()                                                         ##
##      Removing old log files processed already                        ##
##                                                                      ##
##########################################################################
def clear_log():
    files = os.listdir('.')

    for fname in files:
        fext = fname.split('.')[1]

        if fext == 'log':
            os.remove(fname)
### EndDef clear_log() ###

##########################################################################
##  parse_args()                                                        ##
##      Parse command arguments                                         ##
##                                                                      ##
##########################################################################
def parse_args():
    parser = argparse.ArgumentParser(description='')

    parser.add_argument("lower")
    parser.add_argument("upper")
    parser.add_argument("api_key")

    args = parser.parse_args()
    
    lower = int(datetime.strptime(args.lower, '%Y-%m-%d').timestamp())
    upper = int(datetime.strptime(args.upper, '%Y-%m-%d').timestamp())

    return lower, upper, args.api_key
### EndDef parse_args() ###

def main():
    # Time for process start
    process_started = datetime.now()

    #
    # Parse args and build params
    #
    lower, upper, api_key = parse_args()
    # print ("Start Date:\t", lower)
    # print ("End Date:\t", upper)

    AMBIENT_API_KEY = api_key

    #
    # Get station devices
    #
    # amb_debug("")
    # amb_debug("=================================================")
    # amb_debug("               Get Station Devices")
    # amb_debug("=================================================")
    print ("Get Station Devices ...")
    api = AmbientAPI()
    api.api_key = AMBIENT_API_KEY
    api.application_key = AMBIENT_APPLICATION_KEY

    devices = api.get_devices()
    device = devices[0]
    time.sleep(1)
    # Station Info
    station_api_instance = device.api_instance
    station_name = device.info['name']
    station_location = device.info['location']
    station_mac_address = device.mac_address
    station_last_data = device.last_data
    time.sleep(1)
    #
    # Get station data
    #
    # amb_debug("")
    # amb_debug("=================================================")
    # amb_debug("               Get Station Data")
    # amb_debug("=================================================")
    #%%
    print ("Get Station Data ...")
    total = []
    end_date = upper
    while True:
        weather_data = device.get_data(end_date=end_date * 1000)

        if len(weather_data) == 0:
            break

        time.sleep(1)
        print(datetime.fromtimestamp(end_date).strftime('%Y-%m-%d %H:%M:%S'))
        last_data = weather_data[-1]

        if last_data['dateutc'] < lower * 1000:
            total = total + list(filter(lambda data: data['dateutc'] >= lower * 1000, weather_data))
            break
        else:
            total = total + weather_data
            end_date = int(last_data['dateutc'] / 1000)
    
    # aprs = AmbientAPRS(
    #     station_id='KUTSYRAC22'
    # )
    # weather_data = aprs.get_weather_data()

    #%%
    # Process CSV files
    #
    # amb_debug("")
    # amb_debug("=================================================")
    # amb_debug("               Process Data")
    # amb_debug("=================================================")
    print ("Process Data ...")
    generate_csv(total, lower, upper)
    generate_txt(total, lower, upper)

    # Evaluate Process Duration    
    process_ended = datetime.now()
    duration = process_ended - process_started
    mins = int(duration.seconds / 60)
    secs = duration.seconds - mins * 60
    print ("""
=================================================
***
*** Completed
***

Process Started :     {}
Files Unzipped :      {}
-------------------------------------------------
Taken Time (mm:ss) :  {} mins {}  seconds\n
    """.format(process_started, process_ended, mins, secs))


if __name__ == "__main__":
    main()
