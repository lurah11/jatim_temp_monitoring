from django.urls import path
from . import views
from temp.dash_dist import app
from temp.dash_ttest import app2


app_name='temp'

urlpatterns=[
    path('', views.welcome, name='welcome-view'),
    path('<str:home>', views.home, name='home-view'),
    path('dashboard/<str:viz>',views.dashboard, name='dashboard-view')
]