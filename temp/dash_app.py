import dash
from django_plotly_dash import DjangoDash
from .models import Temp,City
from dash import  html, dash_table,dcc,Output, Input
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import json

app = DjangoDash('SimpleExample')   # replaces dash.Dash

# Incorporate data


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
city_code = pd.read_csv('./maps_data/cities_code.csv')

res = res.merge(city_code, on='name', how='left')

with open ('./maps_data/jatim.json') as jatim_json:
    jatim = json.load(jatim_json)

mapbox_token="pk.eyJ1IjoibHVyYWgxMSIsImEiOiJjbGNlZW9rYmg0YXliM3JxbXpjZ2VtZ2dwIn0.KX3xp016xE5VDxpxdb2KSQ"



# App layout
app.layout = html.Div([
    html.Div(children='Temperature & Humidity Data in East Java'),
    html.Hr(),
    dash_table.DataTable(data=res.to_dict('records'), page_size=6),
    dcc.Dropdown(['tmax_avg','tmin_avg','humax_avg','humin_avg'],'tmax_avg',id='parameter'),
    dcc.Graph(figure={}, id='controls-and-graph')
])
print("batubara")

# Add controls to build the interaction
@app.callback(
    Output(component_id='controls-and-graph', component_property='figure'),
    Input(component_id='parameter', component_property='value')
)
def update_graph(col_chosen):
    fig = px.choropleth_mapbox(res, geojson=jatim, color=col_chosen, 
                    locations="code",
                    featureidkey="properties.Code",
                    color_continuous_scale="thermal",
                    center = {'lat':-7.648346,'lon':112.459124}, 
                    zoom = 8
                   )
    fig.update_layout(mapbox={"accesstoken":mapbox_token})
    fig.update_layout(mapbox_style="light")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig 

