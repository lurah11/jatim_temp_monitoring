from django.shortcuts import render
from django.views.decorators.cache import cache_page



# Create your views here.
def home(request):
    context = {
        'introduction':True
    }
    return render(request,'temp/home.html',context)


def dashboard(request): 
    context = {
        'dashboard':True,
    }
    return render (request,'temp/dashboard.html',context)

