import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from app import app, cache

layout = html.Div([
    html.H3('Escuelas'),
    dbc.Input(type = "text", placeholder = "Ingresa los cct separados por coma", id = "entrada-cct"),
    dcc.Link('Regresar', href='/'),
    html.Br(),
    dcc.Link('Reporte', href='/apps/reporte'),
    html.Button('set_session', id='session-button'),
])

@app.callback(
    Output('session', 'data'),
    Input('session-button', 'n_clicks'),
    [State('session', 'data'),
     State('entrada-cct', 'value')]
)
def start_session(n_clicks, data, entrada_ccts) :
    data = data or {'session_active' : False, 'json_data' : None}
    if n_clicks :
        data['session_active'] = True
        # TODO: formulario para obtener los cct correctos
        # TODO: obtener los datos necesarios del orient DB
        ccts = entrada_ccts.split(',')
        escuelas = dict()
        
        for cct in ccts :
            if cct in cache['escuelas'] :
                escuelas[cct] = cache['escuelas'][cct]
            else :
                print("No se encontró el cct %s" % (cct))
        data['escuelas'] = escuelas
        print("Número total de escuelas:", len(data['escuelas']))
    return data
