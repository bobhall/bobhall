
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render


def home(request):
    return render(request, 'home.html')

def pugetsoundwind(request):
    return render(request, 'pugetsoundwind.html')

def ferries(request):
    return render(request, 'ferries.html')

def obs(request):
    return JsonResponse({'conditions':'stormy'})
