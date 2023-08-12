from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from django.urls import reverse



# Create your views here.
def welcome(request): 
    return redirect(reverse('temp:home-view',kwargs={'home':'welcome'}))



def home(request, home):
    context = {
        'introduction':True, 
        'home':home
    }
    return render(request,'temp/home.html',context)


def dashboard(request,viz): 
    context = {
        'dashboard':True,
        'viz':viz
    }
    return render (request,'temp/dashboard.html',context)

def others(request): 
    context = {
        'others':True
    }
    return render(request,'temp/others.html', context)

