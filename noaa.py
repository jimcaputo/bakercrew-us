import logging
import string
import urllib.request
import xml.etree.ElementTree 

from datetime import datetime
from datetime import timedelta

import constants
import util

def fetch():
    try:
        req = urllib.request.Request(constants.NOAA_URL)
        req.add_header('Accept', '*/*')
        req.add_header('User-Agent', 'BakerCrew/v1.0 (http://bakercrew.us; info@bakercrew.us')
        response = urllib.request.urlopen(req)
    except Exception as e:
        raise Exception('urlopen failed with exception: {}'.format(e))

    if response.getcode() != 200:
        raise Exception('Page load failed with status code: {}'.format(response.getcode()))

    root = xml.etree.ElementTree.fromstring(response.read())

    # Parse the date:  'Sun Dec 29 23:13:04 2013 UTC'
    forecast_creation_time = datetime.strptime(
        root.find('forecastCreationTime').text, '%a %b %d %H:%M:%S %Y %Z')
    forecast_creation_time -= timedelta(hours=constants.TZ_OFFSET)
    forecast_creation_time_str = forecast_creation_time.strftime('%Y-%m-%d %H:%M:%S UTC')

    latitude = str.rstrip(root.find('latitude').text, '\n')
    longitude = str.rstrip(root.find('longitude').text, '\n')
    elevation = str.rstrip(root.find('elevation').text, '\n')

    year = util.currentTime().strftime('%Y')

    rows = []
    i = 0
    for day in root.findall('forecastDay'):
        for period in day.findall('period'):
            datetime_str = '{} {}:00:00 {} UTC'.format(
                day.find('validDate').text, period.find('validTime').text, year)
            forecast_time = datetime.strptime(datetime_str, '%b %d %H:%M:%S %Y %Z')
            forecast_time -= timedelta(hours=constants.TZ_OFFSET)

            rows.append({
                'forecast_creation_time': forecast_creation_time_str,
                'latitude': latitude,
                'longitude': longitude,
                'elevation': elevation,
                'forecast_time': forecast_time.strftime('%Y-%m-%d %H:%M:%S UTC'),
                'weather': parseWeather(period.find('wx').text),
                'temperature': period.find('temperature').text,
                'chance_of_precip': period.find('pop').text,
                'snow_level': period.find('snowLevel').text,
                'snow_amount': period.find('snowAmt').text,
                'precip': period.find('qpf').text,
                'wind_speed': period.find('windSpeed').text,
                'wind_gust': period.find('windGust').text,
                'wind_direction': period.find('windDirection').text,
                'dewpoint': period.find('dewpoint').text,
                'relative_humidity': period.find('rh').text,
                'sky_cover': period.find('skyCover').text
            })                
    return rows


def parseWeather(wx):
    if wx == 'Chc R':
        return 'Chance of Rain'
    elif wx == 'Chc S':
        return 'Chance of Snow'
    elif wx == 'Chc SW':
        return 'Chance of Snow Showers'
    elif wx == 'Chc RW':
        return 'Chance of Rain Showers'
        
    elif wx == 'Def R':
        return 'Rain'
    elif wx == 'Def RW':
        return 'Rain Showers'
    elif wx == 'Def S':
        return 'Snow'
    elif wx == 'Def SW':
        return 'Snow Showers'    
    
    elif wx == 'Lkly R':
        return 'Rain Likely'
    elif wx == 'Lkly RW':
        return 'Rain Showers Likely'
    elif wx == 'Lkly S':
        return 'Snow Likely'
    elif wx == 'Lkly SW':
        return 'Snow Showers Likely'
    
    return wx 
