import json
import urllib.request

from bs4 import BeautifulSoup

import constants
import util

def fetch():
    try:
        response = urllib.request.urlopen(constants.NWAC_URL)
    except Exception as e:
        raise Exception('urlopen failed with exception: {}'.format(e))

    if response.getcode() != 200:
        raise Exception('Page load failed with status code: {}'.format(response.getcode()))

    soup = BeautifulSoup(response.read(), 'html.parser')
    
    table = soup.find('div', 'new-weather-content').find('table')
    rows = table.find_all('tr')

    results = []
    
    for row in rows[3:27]:
        cols = row.find_all('td')
        
        # Construct a fully qualified timestamp.  Converts from their 2 column representation
        # that has date (ie 10/17) and time (ie 1400).
        date = cols[0].string.split('/')
        nwac_time = '{}-{:02}-{:02} '.format(util.currentTime().year, int(date[0]), int(date[1]))
        if len(cols[1].string) == 1:
            nwac_time += '00:00:00 UTC'
        elif len(cols[1].string) == 3:
            nwac_time += '0' + cols[1].string[0] + ':00:00 UTC'
        elif len(cols[1].string) == 4:
            nwac_time += cols[1].string[0:2] + ':00:00 UTC'

        # Handle the pre-season case of no snowfall total
        if len(cols) == 12:
            cols.append(0)
            cols.append(0)

        # Construct the JSON object        
        results.append({
            'nwac_time': nwac_time,
            'temperature_5000': int(cols[2].string),
            'temperature_4200': int(cols[3].string),
            'humidity_5000': int(cols[4].string),
            'humidity_4200': int(cols[5].string),
            'wind_min_5000': int(cols[6].string),
            'wind_avg_5000': int(cols[7].string),
            'wind_max_5000': int(cols[8].string),
            'wind_dir_5000': int(cols[9].string),
            'hour_precipitation_4200': float(cols[10].string),
            'total_precipitation_4200': float(cols[11].string),
            'snow_24_hours_4200': int(cols[12].string),
            'snow_total_4200': int(cols[13].string)
        })

    return json.dumps({'nwac_data': results})

