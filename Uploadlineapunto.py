import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash import no_update
#import dash_table
from dash import dash_table

import pandas as pd
#import shapely.geometry
import numpy as np
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import base64
import datetime
import io
import re
import io
import os
#import requests
#--------------------------

token = 'pk.eyJ1Ijoicm1vcHl0aG9uIiwiYSI6ImNrbmZ6MGZyMDF3Yncyd2s4ODVoMmR1Z3EifQ.FCGeYHLeHwjRkksgEyIrSw'

# ------------------------------------------------------------------
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                suppress_callback_exceptions=True
                )
server = app.server
# ------------------------------------------------------------------

app.layout = html.Div([

    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Presentación  ',
            html.A('seleccione el archivo')
        ]),
        style={
            'width': '90%',
            'height': '40px',
            'lineHeight': '40px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px',
            'color': '#1F618D',
            'fontSize': 20
        },
        # Multiples archivos se pueden cargar
        multiple=True
    ),
    #html.Div(id='output-div'),
    html.Div(id='output-datatable'),
    ])

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded), sheet_name='bd', dtype={"CAPA_GEOGRAFICA": str})
            radioitems = list(df.columns)
            radioitems = radioitems[9:(len(radioitems)-1)]

            # Flechas Redes
            df['S_lon'] = 0.000000000000
            df['S_lat'] = 0.000000000000
            df['T_lon'] = 0.000000000000
            df['T_lat'] = 0.000000000000

            l = 0.00004  # the arrow length
            widh = 0.02  # 2*widh is the width of the arrow base as triangle

            for i in range(0, len(df)):
                A = np.array([df['X_INICIO'][i], df['Y_INICIO'][i]])  # start inicio tramo i
                B = np.array([df['X_FIN'][i], df['Y_FIN'][i]])  # end fin tramo i
                v = B - A
                w = v / np.linalg.norm(v)
                u = np.array([-v[1], v[0]])
                P = B - l * w
                S = P - widh * u
                df['S_lon'][i] = S[0]  # 0 corresponde a longitud
                df['S_lat'][i] = S[1]  # 1 corresponde a latitud
                T = P + widh * u
                df['T_lon'][i] = T[0]
                df['T_lat'][i] = T[1]

    except Exception as e:
        print(e)
        return html.Div([
            'error al procesar este archivo'
        ])

    return html.Div([ # inicio

        html.Div(
            [

        html.Label("Clasificación Geográfica", style={'fontSize': 15, 'text-align': 'left', 'padding': '0px 30px 0px 15px',
                                  'color': '#1A5276', "font-weight": "bold"}),
        dcc.Dropdown(id='geografica',
                     options=[{'label': c, 'value': c} for c in sorted(df.CAPA_GEOGRAFICA.unique())], multi=True, value=[],
                             clearable=False),

        html.Label("Clasificación por línea", style={'fontSize': 15, 'text-align': 'left', 'padding': '0px 30px 0px 15px',
                                  'color': '#1A5276', "font-weight": "bold"}),
        dcc.RadioItems(id='clasificacion',
                       options=[{'label': i, 'value': i} for i in radioitems], value=radioitems[0],
                       labelStyle={'display': 'inline-block'}),

        html.Label("Nivel de transparencia", style={'fontSize': 15, 'text-align': 'left', 'padding': '0px 30px 0px 15px',
                                  'color': '#1A5276', "font-weight": "bold"}),
        dcc.Slider(id='transparencia',
                   min=0, max=1, step=0.1, value=0.4,
                   marks={
                       0: {'label': '0', 'style': {'color': '#77b0b1'}},
                       0.2: {'label': '0.2'}, 0.4: {'label': '0.4'}, 0.6: {'label': '0.6'},
                       0.8: {'label': '0.8'},
                       1: {'label': 'Sin Transparencia', 'style': {'color': '#f50'}}
                   }, ),

        html.Label("Dirección de la línea", style={'fontSize': 15, 'text-align': 'left', 'padding': '0px 30px 0px 15px',
                                  'color': '#1A5276', "font-weight": "bold"}),

        dcc.RadioItems(id='visibleflecha',
                    options=[
                        {'label': 'Con flecha', 'value': 'True'},
                        {'label': 'Sin flecha', 'value': 'False'}],
                    value='True',
                    labelStyle={'display': 'inline-block'}
                       ),  # 'block' 'inline-block'),

        #html.Br(),
        html.Label("Clasificación por punto",
                           style={'fontSize': 15, 'text-align': 'left', 'padding': '0px 30px 0px 15px',
                                  'color': '#1A5276', "font-weight": "bold"}),
        dcc.RadioItems(id='clasificacionpunto',
                               options=[{'label': i, 'value': i} for i in radioitems], value=radioitems[0],
                               labelStyle={'display': 'inline-block'}),

        html.Label("Mapas de fondo", style={'fontSize': 15, 'text-align': 'left', 'padding': '0px 30px 0px 15px',
                                  'color': '#1A5276', "font-weight": "bold"}),
        dcc.RadioItems(id='estilomapa',
            options=[{'label': i, 'value': i} for i in ['carto-positron', 'streets', 'satellite', 'satellite-streets']],
            value='carto-positron',
            labelStyle={'display': 'inline-block'}
        ),
        html.Br(),
        html.Button(id="submit-button", children="Crear Gráfico",  style={'fontSize': 10, 'text-align': 'center', 'color': '#154360',
                                                                          'padding': '0px 30px 0px 15px'}),
        html.Label("Contacto:rmopython@gmail.com, WhatsApp (+57) 3017565982, fecha:2021.",
        style={'fontSize': 10, 'text-align': 'left', 'padding': '0px 1px 0px 5px', 'color': '#1A5276', "font-weight": "bold"}),

            ],
            style={'width': '20%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='grafica0')
        ], style={'width': '78%', 'float': 'right', 'display': 'block'}),

        html.Hr(),

        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            page_size=3
        ),
        dcc.Store(id='stored-data', data=df.to_dict('records')),
        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ]) # Final

@app.callback(Output('output-datatable', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))

def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

@app.callback(Output('grafica0', 'figure'),
              Input('submit-button','n_clicks'),
              State('stored-data','data'),
              State('geografica','value'),
              State('clasificacion', 'value'),
              State('transparencia', 'value'),
              State('visibleflecha', 'value'),
              State('clasificacionpunto', 'value'),
              State('estilomapa', 'value'),
              )
def make_graphs(n, data, opc_geografica, opc_clasificacion, opc_transparencia, opc_flecha, opc_clasificacionpto, opc_estilomapa):
    if n is None:
        return no_update
    else:
        df0 = pd.DataFrame(data)
        dfl = df0[df0['ELEMENTO'] == 'linea']
        df1 = dfl[(dfl.CAPA_GEOGRAFICA.isin(opc_geografica))]
        dfp = df0[df0['ELEMENTO'] == 'punto']
        df2 = dfp[(dfp.CAPA_GEOGRAFICA.isin(opc_geografica))]

        lonst1 = []
        latst1 = []

        lonst1 = np.empty(3 * len(df1))
        lonst1[::3] = df1['X_INICIO']
        lonst1[1::3] = df1['X_FIN']
        lonst1[2::3] = None
        latst1 = np.empty(3 * len(df1))
        latst1[::3] = df1['Y_INICIO']
        latst1[1::3] = df1['Y_FIN']
        latst1[2::3] = None
        myvar1 = opc_clasificacion
        colorlineas = ['text'] * (3 * len(df1))
        colorlineas[::3] = df1[myvar1]
        colorlineas[1::3] = df1[myvar1]
        colorlineas[2::3] = df1[myvar1]

        # Flechas

        lons2 = []
        lats2 = []

        lons2 = np.empty(5 * len(df1))
        lons2[::5] = df1['S_lon']
        lons2[1::5] = df1['T_lon']
        lons2[2::5] = df1['X_FIN']
        lons2[3::5] = df1['S_lon']
        lons2[4::5] = None

        lats2 = np.empty(5 * len(df1))
        lats2[::5] = df1['S_lat']
        lats2[1::5] = df1['T_lat']
        lats2[2::5] = df1['Y_FIN']
        lats2[3::5] = df1['S_lat']
        lats2[4::5] = None

        # Nodos con informacion de redes

        lons = []
        lats = []

        lons = np.empty(len(df1))
        lons = df1['X_INICIO']
        lats = np.empty(len(df1))
        lats = df1['Y_INICIO']

        text_ = []
        text_ = np.empty(len(df1), dtype=object)
        text_ = df1['text']

        fig = px.line_mapbox(df1, lat=latst1, lon=lonst1, color=colorlineas, )
        if opc_flecha == 'True':
            visible1 = True
        else:
            visible1 = False

        fig.add_trace(go.Scattermapbox(lon=lons2, hoverinfo='none', showlegend=False, opacity=opc_transparencia, lat=lats2,
                             mode='lines', fill='toself', fillcolor='#750D86', line_color='#750D86', visible = visible1))

        fig.add_trace(go.Scattermapbox(mode='markers', lon=lons, lat=lats, name='información de líneas',
                                       hovertext=text_, opacity=opc_transparencia,
                                       marker=dict(size=3,
                                                   color='#99A3A4',
                                                   )))

        # Nodos del proyecto

        df3 = pd.unique(df2[opc_clasificacionpto])
        a = 8 + 2 * len(df3)
        marker_size = np.arange(8, a, 2)
        marker_color = ['#E74C3C', '#F1C40F', '#2ECC71', '#A569BD', '#D35400', '#943126', '#515A5A', '#1ABC9C',
                        '#DC7633', '#616A6B']

        for i in range(0, len(df3)):
            df4 = df2[df2[opc_clasificacionpto] == df3[i]]
            # Nodos del proyecto
            lons3 = []
            lats3 = []

            lons3 = np.empty(len(df4))
            lons3 = df4['X_INICIO']
            lats3 = np.empty(len(df4))
            lats3 = df4['Y_INICIO']

            text2 = []
            text2 = np.empty(len(df4), dtype=object)
            text2 = df4['text']

            fig.add_trace(go.Scattermapbox(mode='markers', lon=lons3, lat=lats3, name=df3[i],
                                       hovertext=text2, opacity=opc_transparencia,
                                       marker=dict(size=marker_size[i],
                                                   color=marker_color[i],
                                                   )))

        fig.update_layout(margin={'l': 0, 't': 30, 'b': 0, 'r': 0}, showlegend=True,
                          mapbox_style=opc_estilomapa, mapbox_accesstoken='pk.eyJ1Ijoicm1vcHl0aG9uIiwiYSI6ImNrbmZ6MGZyMDF3Yncyd2s4ODVoMmR1Z3EifQ.FCGeYHLeHwjRkksgEyIrSw',
                          mapbox_zoom=13.5, mapbox_center={'lat': df0['Y_INICIO'].mean(), 'lon': df0['X_INICIO'].mean()},
                          width=1050, height=550,
                          )


        return fig

# ------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)