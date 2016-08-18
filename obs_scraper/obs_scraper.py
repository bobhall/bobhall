
import dateutil.parser as dtparser
import urllib2
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import re

DATE_TIME_FMT = "%d %b %Y %I:%M:%S %p %Z"


class ObsResource:
    def __init__(self, url, parser, name, position):
        self.url = url
        self.parser = parser
        self.name = name
        self.position = position

    def load(self):
        result = urllib2.urlopen(self.url)
        html = ''.join(result.readlines())
        return self.parser(html, self.name, self.position)


class ObsScraper:
    def __init__(self):
        return

    def parse_wsf(self, html):
        return {'wind_speed': 'very windy'}

    def parse_ndbc(self, html, name, position):
        soup = BeautifulSoup(html, 'html.parser')
        raw_string = soup.body.find_all('b')[0].next.next
        time_string = soup.body.find_all('p')[1].next
        
        wind_speed = None
        wind_direction = None

        # Wind direction
        print "raw_string", raw_string
        match = re.search(r'(\d+\xb0)', unicode(raw_string))
        if match:
            wind_direction = int(re.search(r'\d+', match.group()).group())

        # Wind speed
        match = re.search(r'\d+ kts', raw_string)
        if match:
            wind_speed = int(re.search(r'\d+', match.group()).group())

        date_time = dtparser.parse(time_string)

        return {'wind_speed': wind_speed,
                'wind_direction': wind_direction,
                'time': date_time.strftime(DATE_TIME_FMT),
                'station_name': name,
                'position': position}



    def fetch_urls(self):
        urls = [ObsResource('http://www.ndbc.noaa.gov/mobile/station.php?station=sisw1',
                            self.parse_ndbc, 
                            "Smith Island", 
                            {'lat':48.318,'lon':-122.843}),
                ObsResource('http://www.ndbc.noaa.gov/mobile/station.php?station=wpow1',
                            self.parse_ndbc,
                            "West Point",
                            {'lat': 47.662, 'lon':-122.436}),]

        results = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            for url in urls:
                future = executor.submit(url.load)
                results.append(future.result())
        return results
