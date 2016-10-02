
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import urllib2
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

from obs_scraper import ObsScraper

def home(request):
    return render(request, 'home.html')

def pugetsoundwind(request):

    scraper = ObsScraper()
    obs = scraper.fetch_urls()

    return render(request, 
                  'pugetsoundwind.html', 
                  context={'observations': obs})

def ferries(request):
    return render(request, 'ferries.html')

def obs(request):
    scraper = ObsScraper()
    obs = scraper.fetch_urls()
    return JsonResponse(obs, safe=False)
