
import dateutil.parser as dtparser
import urllib.request

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import re
import datetime
import pytz

from obs_scraper.wind_util import degrees_to_cardinal, get_average_wind_speeds

DATE_TIME_FMT = "%d %b %Y %I:%M:%S %p %Z"


class ObsResource(object):
    def __init__(self, url):
        self.url = url

    def load(self):
        result = urllib.request.urlopen(self.url)
        return self.parse(result.read())

class NDBCResource(ObsResource):

    def __init__(self, url, name, position):
        super(NDBCResource, self).__init__(url)
        self.name = name
        self.position = position

    def parse(self, html):
        try:
            soup = BeautifulSoup(html, 'html.parser')
            raw_string = soup.body.find_all('b')[0].next.next
            time_string = soup.body.find_all('p')[1].next

            wind_speed = None
            wind_direction = None

            # Wind direction
            match = re.search(r'(\d+\xb0)', unicode(raw_string))
            if match:
                wind_direction = int(re.search(r'\d+', match.group()).group())

            # Wind speed
            match = re.search(r'\d+ kts', raw_string)
            if match:
                wind_speed = int(re.search(r'\d+', match.group()).group())

            date_time = dtparser.parse(time_string)
        except:
            return None

        result = {'wind_speed': wind_speed,
                  'time': date_time.strftime(DATE_TIME_FMT),
                  'station_name': self.name,
                  'position': self.position,
                  'station_type': 'ndbc'}
        if wind_direction != None and isinstance(wind_direction, int):
            result['wind_direction'] = degrees_to_cardinal(wind_direction)
        return result


class WSFFerryResource(ObsResource):

    def __init__(self, url, vessel_name):
        super(WSFFerryResource,self).__init__(url)
        self.vessel_name = vessel_name

    areas = [
        {'top': 47.62, 'bottom': 47.6, 'left': -122.475, 'right': -122.4275, 'name': "Seattle / Bainbridge Island Ferry"},
        {'top': 47.82, 'bottom': 47.785, 'left': -122.467, 'right': -122.42, 'name': "Edmonds / Kingston Ferry"},
        {'top': 48.5371, 'bottom': 48.51, 'left': -122.76, 'right': -122.729, 'name': "Anacortes Ferry (Rosario Strait)"},
        {'top': 47.587, 'bottom': 47.57, 'left': -122.4716, 'right': -122.4383, 'name': "Seatte / Bremerton Ferry"}
    ]

    def parse(self, html):
        soup = BeautifulSoup(html)
        rows = soup.findAll('tr')[2:]
        rows = [row.text.split('\n') for row in rows]

        position = None
        ferry_time = None
        area_name = None

        found_rows = False
        valid_rows = []
        for area in self.areas:
            for row in rows:
                try:
                    lat, lon = [float(x) for x in row[2].split()]
                except:
                    continue
                if lat > area['bottom'] and lat < area['top'] and lon > area['left'] and lon < area['right']:
                    found_rows = True
                    if not ferry_time:
                        ferry_time = row[1]
                    wind_speed = row[6]
                    wind_dir = row[5]
                    valid_rows.append((int(wind_speed),int(wind_dir)))
                    position = (lat,lon)
                    area_name = area['name']
                else:
                    if found_rows:
                        break
            if found_rows:
                break

        if 0 == len(valid_rows) or not found_rows:
            return None
            
        pacific = pytz.timezone('US/Pacific')
        date_time = dtparser.parse(ferry_time)
        date_time = pacific.localize(date_time)

        wind_speed, wind_dir = get_average_wind_speeds(valid_rows)

        results = {'wind_speed': round(wind_speed,2),
                   'wind_direction': degrees_to_cardinal(wind_dir),
                   'position': {'lat': position[0],
                                'lon': position[1]},
                   'time': date_time.strftime(DATE_TIME_FMT),
                   'station_name': area_name,
                   'vessel_name': self.vessel_name,
                   'station_type': 'ferry'}

        return results

class CGRResource(ObsResource):

    stations = [{'name':'POINT WILSON', 'position': {'lat':48.143, 'lon': -122.754}},
                {'name':'POINT NO POINT', 'position': {'lat': 47.9119, 'lon': -122.5258}},
                {'name': 'POINT ROBINSON', 'position': {'lat': 47.3881, 'lon': -122.3742}},
                {'name': 'ALKI POINT', 'position': {'lat': 47.5763, 'lon': -122.4208}}]

    def parse(self, html):
        results = []
        lines = html.split('\n')

        time_line = filter(lambda line: re.match(r'.*KSEW.*',line), lines)[0]
        time_chunk = time_line.split(' ')[2]
        day = int(time_chunk[0:2])
        hour = int(time_chunk[2:4])
        minutes = int(time_chunk[4:6])

        now = datetime.datetime.utcnow()
        try:
            date_time = datetime.datetime(now.year,now.month,day,hour,minutes)
        except:
            now = now - datetime.timedelta(hours=12)
        date_time = datetime.datetime(now.year,now.month,day,hour,minutes,tzinfo=pytz.utc)
        
        pacific = pytz.timezone('US/Pacific')
        date_time = date_time.astimezone(pacific)
        

        for station in self.stations:
            station_line = filter(lambda line: re.match(r'.*{name}.*'.format(name=station['name']), line), lines)
            conditions = station_line[0].split('/')[1].strip() # NW11, S04, etc.

            try:
                match = re.match(r'([A-Z]+)(\d+)', conditions)
                wind_dir = match.group(1)
                wind_speed = int(match.group(2))
            except:
                wind_dir = None
                wind_speed = None

            results.append({'wind_speed': wind_speed,
                            'wind_direction': wind_dir,
                            'station_name': station['name'].title(),
                            'position': station['position'],
                            'time': date_time.strftime(DATE_TIME_FMT),
                            'station_type': 'cgr'
                        })
        return results

class ObsScraper:
    def __init__(self):
        return

    def is_valid_result(self, result):
        return isinstance(result,dict) and result.has_key('position') and result.has_key('wind_speed')

    def fetch_urls(self):

        resources = [NDBCResource('http://www.ndbc.noaa.gov/mobile/station.php?station=sisw1',
                                  "Smith Island", 
                                  {'lat':48.318,'lon':-122.843}),
                     NDBCResource('http://www.ndbc.noaa.gov/mobile/station.php?station=wpow1',
                                  "West Point",
                                  {'lat': 47.662, 'lon':-122.436}),

                     CGRResource('http://tgftp.nws.noaa.gov/data/raw/sx/sxus40.ksew.cgr.sew.txt'),]

        results = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            for resource in resources:
                future = executor.submit(resource.load)
                result = future.result()

                if isinstance(result,dict):
                    results.append(future.result())
                elif isinstance(result, list):
                    results.extend(result)

                results = filter(self.is_valid_result, results)
                
        results.sort(key=lambda obs: obs['position']['lat'], reverse=True)
        return results
