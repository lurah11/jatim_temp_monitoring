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


app2 = DjangoDash('ttest', external_stylesheets=[dbc.themes.BOOTSTRAP],add_bootstrap_links=True)   # replaces dash.Dash

######  BEGIN - PROCESSING THE DATA ####### 
data_from_db = Temp.objects.all()

data = {
    'name':[],
    'tmax':[],
    'tmin':[],
    'humax':[],
    'humin':[]
}

for d in data_from_db:
    data["name"].append(d.city.name)
    data["tmax"].append(d.tmax)
    data["tmin"].append(d.tmin)
    data["humax"].append(d.humax)
    data["humin"].append(d.humin)

res = pd.DataFrame(data)
city_list = res["name"].unique()

####### END - PROCESSING THE DATA ####### 

####### BEGIN - CREATE VISUALIZATION #####

#mapbox_token 
mapbox_token=settings.MAPBOX_TOKEN




#Inline Sytle 

fs_title = {'margin-left':'10px','font-size':'25px','text-align':'center','background-color':'coral'}
fs_p = {'margin-left':'10px','font-size':'12px'}
s_d_down = {'margin-left':'0px','font-size':'12px'}
fig_ttl = {'color':'red', 'text-align':'center'}


today = datetime.now().date()

date_str = today.strftime("%Y-%m-%d")

# App Layout with bootstrap 

app2.layout = dbc.Row([
    dbc.Row(dbc.Col(children='Box Plots and t Test Between Two Cities'),style=fs_title),
    html.Hr(),
    dbc.Row(dbc.Col(children=[
        dbc.Row([
            dbc.Col([
                dbc.Row(children="Kota 1",style=fs_p),
                dbc.Row(dcc.Dropdown(city_list.tolist(),"Kota Mojokerto",id="city1"),style=s_d_down)]),
            dbc.Col([
                dbc.Row(children="Kota 2",style=fs_p),
                dbc.Row(dcc.Dropdown(city_list.tolist(),"Kab. Malang",id="city2"),style=s_d_down)]),
            ])
    ])),
    html.Hr(),
    dbc.Row([
        dbc.Col([dcc.Graph(figure={},id='graph_tmax')],class_name="col-6"),
        dbc.Col([dcc.Graph(figure={}, id='graph_tmin')],class_name="col-6")
    ]),
    dbc.Row([
        dbc.Col([dcc.Graph(figure={},id='graph_humax')],class_name="col-6"),
        dbc.Col([dcc.Graph(figure={}, id='graph_humin')],class_name="col-6")
    ]),
    html.Hr(),
    dbc.Row([
        dbc.Col([html.P("Input Alpha Value here (between 0 to 1):", style={"text-align":"right"})]),
        dbc.Col([dcc.Input(type="number", min=0, max = 1,value=0.05,id="alpha",style=fig_ttl)])
    ]),
    dbc.Row([html.P(['Normality test'],id="norm_ttest",style=fig_ttl)]),
    html.Hr(),
    dbc.Row([
        dbc.Col([],id="data_normal")
    ]),
    html.Hr(),
    dbc.Row([html.P(['Summary of t_test between 2 cities'],id="p_ttest",style=fig_ttl)]),
    html.Hr(),
    dbc.Row([
        dbc.Col([],id="data_table")
    ])
     
])

def create_boxplot(y0,y1,name1,name2): 
    fig = go.Figure()
    fig.add_trace(go.Box(y=y0, name=name1,
                    marker_color = 'indianred'))
    fig.add_trace(go.Box(y=y1, name =name2,
                    marker_color = 'lightseagreen'))
    return fig 



# #Add controls to build the interaction
@app2.callback(
    Output(component_id='graph_tmax', component_property='figure'),
    Output(component_id='graph_tmin', component_property='figure'),
    Output(component_id='graph_humax', component_property='figure'),
    Output(component_id='graph_humin', component_property='figure'),
    Input(component_id='city1', component_property='value'),
    Input(component_id='city2',component_property='value'),
)
def update_graph(city1,city2): 
    city1_data = res[res["name"]==city1] 
    city2_data = res[res["name"]==city2]
    fig_tmax = create_boxplot(city1_data["tmax"],city2_data["tmax"],city1,city2)
    fig_tmin = create_boxplot(city1_data["tmin"],city2_data["tmin"],city1,city2)
    fig_humax = create_boxplot(city1_data["humax"],city2_data["humax"],city1,city2)
    fig_humin = create_boxplot(city1_data["humin"],city2_data["humin"],city1,city2)

    fig_tmax.update_layout(xaxis_title="fig1. Boxplots of Maximum Temperature")
    fig_tmin.update_layout(xaxis_title="fig2. Boxplots of Minimum Temperature")
    fig_humax.update_layout(xaxis_title="fig3. Boxplots of Maximum Humidity")
    fig_humin.update_layout(xaxis_title="fig4. Boxplots of Minimum Humidity")

    return fig_tmax,fig_tmin,fig_humax, fig_humin


@app2.callback(
    Output(component_id='data_table', component_property='children'),
    Output(component_id='data_normal', component_property='children'),
    Input(component_id='city1', component_property='value'),
    Input(component_id='city2',component_property='value'),
    Input(component_id='alpha',component_property='value'),
)
def update_ttest(city1,city2,alpha): 
    df_normal =  {
        "parameter_name":[],
        f"p_val_{city1}":[],
        f"p_val_{city2}":[],
        f"norm_test_{city1}":[],
        f"norm_test_{city2}":[],
    }
    
    df = {
        "parameter_name":[],
        f"avg_{city1}":[],
        f"avg_{city2}":[],
        "t_calc":[],
        "p_val":[],
        "result":[]
    }

    city1_data = res[res["name"]==city1] 
    city2_data = res[res["name"]==city2]
    param_name = ["tmax","tmin","humax","humin"]
    for param in param_name : 
        t_test_res = ttest_ind(city1_data[param],city2_data[param])
        s1,p1= normaltest(city1_data[param])
        s2,p2 = normaltest(city2_data[param])
        # construct dict untuk normality test 
        df_normal["parameter_name"].append(param)
        df_normal[f"p_val_{city1}"].append(p1)
        if p1 < alpha : 
            df_normal[f"norm_test_{city1}"].append("non normal")
        else : 
            df_normal[f"norm_test_{city1}"].append("approx. normal")
        
        df_normal[f"p_val_{city2}"].append(p2)
        if p2 < alpha : 
            df_normal[f"norm_test_{city2}"].append("non normal")
        else : 
            df_normal[f"norm_test_{city2}"].append("approx. normal")
                
        #construct dict untuk ttest
        df["parameter_name"].append(param)
        df[f"avg_{city1}"].append(city1_data[param].mean())
        df[f"avg_{city2}"].append(city2_data[param].mean())
        df["t_calc"].append(t_test_res[0])
        df["p_val"].append(t_test_res[1])
        if t_test_res[1] < alpha : 
            df["result"].append("significantly different")
        else : 
            df["result"].append("not significantly different")
    
    print(df)
    print(df_normal)
    dataframe1 = pd.DataFrame(df)
    dataframe2 = pd.DataFrame(df_normal)
    conditional_style =[
        {
            'if': {
                'filter_query': '{result}="significantly different"',
                'column_id': 'result',
            },
            'color': 'red'
        }
    ]
    return dash_table.DataTable(dataframe1.to_dict('records'), style_data_conditional=conditional_style), dash_table.DataTable(dataframe2.to_dict("records"))

