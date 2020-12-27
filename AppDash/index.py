import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import json
import re
import numpy as np
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from apps import escuelas, regiones, estado, reporte, reporte_escuela

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Store(id='session', storage_type='session'),
])

layout = html.Div([
    html.H3('Index'),
    dcc.Link('Escuelas', href='/apps/escuelas'),
    html.Br(),
    dcc.Link('Regiones', href='/apps/regiones'),
    html.Br(),
    dcc.Link('Estado', href='/apps/estado'),
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('session', 'data'),
)
def display_page(pathname, data):
    data = data or {'session_active' : False, 'json_data' : None}
    
    if pathname == '/' :
        return layout
    if pathname == '/apps/escuelas' :
        return escuelas.layout
    elif pathname == '/apps/regiones' :
        return regiones.layout
    elif pathname == '/apps/estado' :
        return estado.layout
    elif pathname == '/apps/reporte' and data['session_active'] :
        # Verificar que exista una sesión, si no, regresar 404
        
        return reporte.cargar_plantilla_reporte(
            contenido = reporte.cargar_layout_reporte_general(
                escuelas = reporte.ordenar_escuelas(json.loads(data['json_data']))
            )
        )
    elif re.search('^/apps/reporte/32[A-Z]{3}[0-9]{4}[A-Z]{1}', pathname) and data['session_active'] :
        # Verificar que exista una sesión, si no, regresar 404
        escuelas_reporte = json.loads(data['json_data'])
        cct = pathname[-10:]
        
        if not cct in escuelas_reporte :
            return '404'
        
        return reporte.cargar_plantilla_reporte(
            contenido = reporte.cargar_layout_reporte_individual(
                escuelas = escuelas_reporte, 
                cct = cct
            )
        )
    else :
        return '404'

if __name__ == '__main__' :
    app.run_server(debug=True)
