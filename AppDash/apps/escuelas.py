import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from app import app

layout = html.Div([
    html.H3('Escuelas'),
    dcc.Link('Regresar', href='/'),
    html.Br(),
    dcc.Link('Reporte', href='/apps/reporte'),
    html.Button('set_session', id='session-button'),
])

@app.callback(
    Output('session', 'data'),
    Input('session-button', 'n_clicks'),
    State('session', 'data'),
)
def start_session(n_clicks, data) :
    data = data or {'session_active' : False, 'json_data' : None}
    if n_clicks :
        data['session_active'] = True
        # TODO: formulario para obtener los cct correctos
        # TODO: obtener los datos necesarios del orient DB
        data['json_data'] = '{"32DPR2447T":{"matricula":[89,127,134,152,170,172,182,192,197,210,219,222,232,226,222,205,222,229,241,275,330,357],"pred":[171,171,178,184,188],"mae":25.41,"rmse":33.08,"mape":0.1,"rp":0.29,"nombre":"Ricardo Flores Magón","nivel":"Primaria","mun":"Loreto","primer_anio":1998,"lat":22.2639956,"lng":-101.9824938},"32DPR1225C":{"matricula":[99,88,81,77,77,73,67,69,70,63,60,65,63,65,67,65,67,69,70,73,77,72],"pred":[75,73,71,71,71],"mae":3.57,"rmse":4.56,"mape":0.05,"rp":0,"nombre":"Independencia","nivel":"Secundaria","mun":"General Francisco M. Murgia","primer_anio":1998,"lat":24.1652776,"lng":-103.1913887},"32DPR0026X":{"matricula":[39,35,28,23,15,17,17,18,19,21,26,25,24,18,21,19,16,14,16,14,18,21],"pred":[17,18,19,20,21],"mae":2.32,"rmse":2.97,"mape":0.13,"rp":0,"nombre":"20 de Noviembre","nivel":"Preescolar","mun":"General Francisco M. Murgia","primer_anio":1998,"lat":24.0575035,"lng":-102.9429896}}'
    return data
