from django.urls import path
from . import views
from temp.dash_app import app


app_name='temp'

urlpatterns=[
    path('', views.home, name='home-view'),
    path('tech_detail',views.tech, name='tech-view')
]