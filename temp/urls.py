from django.urls import path
from . import views
from temp.dash_app import app


app_name='temp'

urlpatterns=[
    path('', views.home, name='home-view'),
    path('dashboard',views.dashboard, name='dashboard-view')
]