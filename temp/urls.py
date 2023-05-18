from django.urls import path
from . import views


app_name='temp'

urlpatterns=[
    path('', views.home, name='home-view')
]