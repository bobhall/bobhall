
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import urllib2
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

from obs_scraper import ObsScraper

import dateutil.parser as dtparser
import datetime
import pytz

def home(request):
    return render(request, 'home.html')

def pugetsoundwind(request):
    scraper = ObsScraper()
    obs = scraper.fetch_urls()

    now = datetime.datetime.now(pytz.timezone('US/Pacific'))
    for observation in obs:
        if (now - dtparser.parse(observation['time'])) > datetime.timedelta(hours=2):
            observation['late'] = True

    return render(request, 
                  'pugetsoundwind.html', 
                  context={'observations': obs})

def ferries(request):
    return render(request, 'ferries.html')

def obs(request):
    scraper = ObsScraper()
    obs = scraper.fetch_urls()
    return JsonResponse(obs, safe=False)


def aboutpugetsoundwind(request):
    return render(request, 'aboutpugetsoundwind.html')

def aboutferryvisualization(request):
    return render(request, 'aboutferryvisualization.html')
