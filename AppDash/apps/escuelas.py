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
        # TODO: obtener los datos necesarios del orient DB
    return data
        
