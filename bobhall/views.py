
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import urllib2
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

def home(request):
    return render(request, 'home.html')

def pugetsoundwind(request):
    return render(request, 'pugetsoundwind.html')

def ferries(request):
    return render(request, 'ferries.html')

def parse_wsf(html):
    return html[:100]

def parse_cgr(html):
    return html[:100]

def parse_ndbc(html):
    soup = BeautifulSoup(html,'html.parser')
    raw_string = soup.body.find_all('b')[0].next.next
    time_string = soup.body.find_all('p')[1].next

    wind_speed = None
    wind_direction = None

#    if 1 == len(time_string.split(',')):
#    import pdb; pdb.set_trace();
    
    return html[:100]

def fetch_url(url,parser):
    result = urllib2.urlopen(url)
    html = ''.join(result.readlines())
    return parser(html)

def obs(request):

    urls = [ #('http://www.ndbc.noaa.gov/mobile/station.php?station=wpow1', parse_ndbc),
           ('http://www.ndbc.noaa.gov/mobile/station.php?station=sisw1', parse_ndbc),
            ('http://i90.atmos.washington.edu/ferry/tabular/FP.htm', parse_wsf)]

    results = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        for url in urls:
            future = executor.submit(fetch_url, url[0], url[1])
            results.append(future.result())
            print "\n................Done...................\n"

    return JsonResponse({'conditions': results})
