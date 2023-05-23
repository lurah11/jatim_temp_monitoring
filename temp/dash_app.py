import dash
from django_plotly_dash import DjangoDash
from .models import Temp,City
from dash import  html, dash_table,dcc,Output, Input
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import json
import dash_bootstrap_components as dbc
import os
from django.core.cache import cache
from datetime import datetime
from dash.dependencies import State

app = DjangoDash('SimpleExample', external_stylesheets=[dbc.themes.BOOTSTRAP],add_bootstrap_links=True)   # replaces dash.Dash

######  BEGIN - PROCESSING THE DATA ####### 
data_from_db = Temp.objects.all()

data = {
    'date':[],
    'name':[],
    'latitude':[],
    'longitude':[],
    'tmax':[],
    'tmin':[],
    'humax':[],
    'humin':[]
}

for d in data_from_db:
    data["date"].append(d.date)
    data["name"].append(d.city.name)
    data["latitude"].append(d.city.latitude)
    data["longitude"].append(d.city.longitude)
    data["tmax"].append(d.tmax)
    data["tmin"].append(d.tmin)
    data["humax"].append(d.humax)
    data["humin"].append(d.humin)

df = pd.DataFrame(data)

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

# with open ('./maps_data/jatim.json') as jatim_json:
#     jatim = json.load(jatim_json)

with open('./maps_data/simple-jatim.json') as simple_jatim_json: 
    simple_jatim = json.load(simple_jatim_json)


####### END - PROCESSING THE DATA ####### 

####### BEGIN - CREATE VISUALIZATION #####

#mapbox_token 
mapbox_token="pk.eyJ1IjoibHVyYWgxMSIsImEiOiJjbGNlZW9rYmg0YXliM3JxbXpjZ2VtZ2dwIn0.KX3xp016xE5VDxpxdb2KSQ"




#Inline Sytle 

fs_title = {'margin-left':'10px','font-size':'25px','text-align':'center','background-color':'lime'}
fs_p = {'margin-left':'10px','font-size':'12px'}
s_d_down = {'margin-left':'0px','font-size':'12px'}
fig_ttl = {'color':'red', 'text-align':'center'}

today = datetime.now().date()

date_str = today.strftime("%Y-%m-%d")

# App Layout with bootstrap 

app.layout = dbc.Row([
    dbc.Row(dbc.Col(children='Temperature and Humidity Distribution Map'),style=fs_title),
    html.Hr(),
    dbc.Row(dbc.Col(children=[
        dbc.Row([
            dbc.Col([
                dbc.Row(children="Plot Parameter:",style=fs_p),
                dbc.Row(dcc.Dropdown([{'label':'Average of Maximum Temperature', 'value':'tmax_avg'},{'label':'Average of Minimum Temperature', 'value':'tmin_avg'},{'label':'Average of Maximum Humidity', 'value':'humax_avg'},{'label':'Average of Minimum Humdity', 'value':'humin_avg'}],"tmax_avg",id="parameter"),style=s_d_down)]),
            dbc.Col([
                dbc.Row(children="Map Polygon Detail:",style=fs_p),
                dbc.Row(dcc.Dropdown([{'label':'HIGH (detailed city border, but slow rendering)', 'value':'high'},{'label':'LOW (Crappy city border, but fast rendering)','value':'low'}],"low",id="polygon"),style=s_d_down)]),
            dbc.Col([
                dbc.Row(children="Map Style:",style=fs_p),
                dbc.Row(dcc.Dropdown(["light","stamen-watercolor","satellite"],"light",id="mb_style"),style=s_d_down)])
            ])
            ])
        ),
    html.Hr(),
    html.Hr(),
    dbc.Row([html.P(children=[''],id='fig_title')],style=fig_ttl),
    html.Hr(),
    dbc.Row(children=[
         dcc.Loading(children=[html.Div(children=[dcc.Graph(figure={},id='controls-and-graph')])],
            id="loading-1",
            type="circle"
        )
    ]),
    html.Hr(),
    html.Hr(),
    dbc.Row([html.P(children=[f'Summary of BMKG data up to {date_str}'])], style=fig_ttl),
    dbc.Row(children=[
        dash_table.DataTable(res.to_dict('records'),page_size=10)
    ])
])




#Add controls to build the interaction
@app.callback(
    Output(component_id='controls-and-graph', component_property='figure'),
    Input(component_id='parameter', component_property='value'),
    Input(component_id='polygon',component_property='value'),
    Input(component_id='mb_style',component_property='value')
)
def update_graph(parameter,polygon,mb_style):
    if polygon == "high": 
        with open ('./maps_data/jatim.json') as jatim_json:
            detail = json.load(jatim_json)
    else : 
        detail=simple_jatim

    fig = px.choropleth_mapbox(res, geojson=detail, color=parameter, 
                    locations="code",
                    featureidkey="properties.Code",
                    color_continuous_scale="thermal",
                    center = {'lat':-7.648346,'lon':112.459124}, 
                    zoom = 8, 
                    hover_data=[res["name"]]
                   )
    fig.update_layout(mapbox={"accesstoken":mapbox_token})
    fig.update_layout(mapbox_style=mb_style)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_layout(title_xref='paper')
    return fig 

@app.callback(
    Output(component_id='fig_title',component_property='children'),
    Input(component_id='parameter', component_property='value'),
    [State("parameter","options")]
)
def update_title(parameter,options): 
    res = ""
    for opt in options : 
        if opt["value"] == parameter: 
            res = opt["label"]
    return f"figure of {res} distribution in east java"
