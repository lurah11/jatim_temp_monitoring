import dash
from django_plotly_dash import DjangoDash
from .models import Temp,City
from dash import  html, dash_table,dcc,Output, Input
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import os
from django.core.cache import cache
from datetime import datetime
from dash.dependencies import State
from scipy.stats import ttest_ind, normaltest
from django.conf import settings


app3 = DjangoDash('dataset', external_stylesheets=[dbc.themes.BOOTSTRAP],add_bootstrap_links=True)   # replaces dash.Dash

######  BEGIN - PROCESSING THE DATA ####### 
data_from_db = Temp.objects.all()

data = {
    'date':[],
    'name':[],
    'tmax':[],
    'tmin':[],
    'humax':[],
    'humin':[],
    'latitude':[],
    'longitude':[],
    'code':[]
}

for d in data_from_db:
    data["date"].append(d.date)
    data["name"].append(d.city.name)
    data["tmax"].append(d.tmax)
    data["tmin"].append(d.tmin)
    data["humax"].append(d.humax)
    data["humin"].append(d.humin)
    data["latitude"].append(d.city.latitude)
    data["longitude"].append(d.city.longitude)
    data["code"].append(d.city.code)


df = pd.DataFrame(data)
print(df.tail())

df = df.astype({'date':'datetime64[ns]'})
df["date"] = df["date"].dt.date

res = gb_area = df.groupby(['name','longitude','latitude']).agg(tmax_avg=('tmax','mean'),tmin_avg=('tmin','mean'),humax_avg=('humax','mean'),humin_avg=('humin','mean')).reset_index()

#rounding parameter to 2 digit 
res["tmax_avg"]=res['tmax_avg'].round(2)
res["tmin_avg"]=res['tmin_avg'].round(2)
res["humax_avg"]=res['humax_avg'].round(2)
res["humin_avg"]=res['humin_avg'].round(2)

## join city code data 
city_code = pd.read_csv('./maps_data/cities.csv')

city_code = city_code[["code","name"]]

res = res.merge(city_code, on='name', how='left')


fs_title = {'margin-left':'10px','font-size':'25px','text-align':'center','background-color':'fuchsia'}
fs_p = {'margin-left':'10px','font-size':'12px'}
s_d_down = {'margin-left':'0px','font-size':'12px'}
fig_ttl = {'color':'red', 'text-align':'center'}


today = datetime.now().date()

date_str = today.strftime("%Y-%m-%d")

# App Layout with bootstrap 

app3.layout = dbc.Row([
    dbc.Row(dbc.Col(children='DATASETS'),style=fs_title),
    html.Hr(),
    dbc.Row([html.P(['Table 1. Raw Dataset obtained from scheduled ETL(Airflow)'],id="raw",style=fig_ttl)]),
    dbc.Row([
        dbc.Col([dash_table.DataTable(df.to_dict("records"), page_size=10)],id="data_table")
    ]),
    dbc.Row([html.P([f'Table 2. Summary of average data up to {date_str}'],id="raw",style=fig_ttl)]),
    dbc.Row([
        dbc.Col([dash_table.DataTable(res.to_dict("records"),page_size=10)],id="data_table_2")
    ]),
    html.Hr(),  
    html.Hr(),
    dbc.Row([html.P(['Notes: I do not convert the dataframe to excel nor provide link to download the collected raw datasets as csv or excel. I think i  need to make sure that BMKG allows such action. Therefore, in this particular project i only show the data in html table format. Data is manually downloaded from May 09 to May 21, then automatically downloaded as part of workflow orchestration since May 23,2023'],id="raw",style=fig_ttl)])

])

