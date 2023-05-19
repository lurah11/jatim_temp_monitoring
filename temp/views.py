from django.shortcuts import render




# Create your views here.
def home(request):
    context = {
        'introduction':True
    }
    return render(request,'temp/home.html',context)


def tech(request): 
    context = {
        'tech':True,
    }
    return render (request,'temp/tech.html',context)
