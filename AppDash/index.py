import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import json
import re
import numpy as np
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app, cache
from apps import escuelas, regiones, estado, reporte

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
    [Output('page-content', 'children'),
     Output('session', 'data')],
    Input('url', 'pathname'),
    [State('session', 'data'),
     State('url', 'search')]
)
def display_page(pathname, data, search):
    data = data or {'session_active' : False, 'json_data' : None}
    
    pagina = '404'
    
    if pathname == '/' :
        pagina = layout
    if pathname == '/apps/escuelas' :
        pagina = escuelas.cargar_plantilla_formulario()
    elif pathname == '/apps/regiones' :
        pagina = regiones.layout
    elif pathname == '/apps/estado' :
        pagina = estado.layout
    elif pathname == '/apps/reporte' :
        if search :
            llave_y_valor = search[1:].split('&')
            ccts = []
            for item in llave_y_valor :
                llave, valor = item.split('=')
                if valor :
                    ccts.append(valor)
            
            ccts_invalidos = False
            for cct in ccts :
                ccts_invalidos |= cct not in cache['escuelas']
            
            if ccts_invalidos :
                pagina = escuelas.cargar_plantilla_formulario(
                    ccts = ccts, 
                    mensaje_error = "Algunas de las CCT que se ingresaron no son válidas, porfavor, escriba adecuadamente las CCT e inténtelo de nuevo"
                )
            elif not ccts :
                pagina = escuelas.cargar_plantilla_formulario(
                    ccts = ccts, 
                    mensaje_error = "Porfavor, ingresa al menos una CCT para generar un reporte"
                )
            else :
                # Activar la sesión
                data['session_active'] = True
                
                __escuelas = dict()
                for cct in ccts :
                    __escuelas[cct] = cache['escuelas'][cct]
                data['escuelas'] = __escuelas
                
                pagina = reporte.cargar_plantilla_reporte(
                    contenido = reporte.cargar_layout_reporte_general(
                        escuelas = reporte.ordenar_escuelas(data['escuelas'])
                    )
                )
        
        elif data['session_active'] :
            pagina = reporte.cargar_plantilla_reporte(
                contenido = reporte.cargar_layout_reporte_general(
                    escuelas = reporte.ordenar_escuelas(data['escuelas'])
                )
            )
        
    elif re.search('^/apps/reporte/32[A-Z]{3}[0-9]{4}[A-Z]{1}', pathname) and data['session_active'] :
        # Verificar que exista una sesión, si no, regresar 404
        escuelas_reporte = data['escuelas']
        cct = pathname[-10:]
        
        if cct in escuelas_reporte :
            pagina = reporte.cargar_plantilla_reporte(
                contenido = reporte.cargar_layout_reporte_individual(
                    escuelas = escuelas_reporte, 
                    cct = cct
                )
            )
    
    return pagina, data

if __name__ == '__main__' :
    app.run_server(debug=True)
