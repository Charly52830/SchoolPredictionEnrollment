# -*- coding: utf-8 -*-
import json
import re
import numpy as np

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State

from app import app, cache
from apps import escuelas, regiones, estado, plantilla_reporte, reporte_individual, reporte_general
from apps.utilidades_reporte import ordenar_escuelas

app.layout = html.Div([
    dcc.Location(id = 'url', refresh = False),
    html.Div(id = 'page-content'),
    dcc.Store(id = 'session', storage_type = 'session'),
])

MENSAJES_ERROR = {
    "ccts_invalidos" : u"Algunas de las CCT que se ingresaron no son válidas, porfavor, escriba adecuadamente las CCT e inténtelo de nuevo",
    "ccts_vacios" : u"Porfavor, ingresa al menos una CCT para generar un reporte"
}

# Layout de la página principal
layout = dbc.Container([
    # Texto de encabezado
    dbc.Row(
        dbc.Col([
            html.H2(
                u"Consulta la matrícula escolar en Zacatecas y crea reportes con la proyección de matrícula",
                style = {"text-align" : "center", "margin-top" : "4rem", "margin-bottom" : "3rem"}
            )],
            md = 8,
        ),
        className = "justify-content-center"
    ),
    # Renglón con Botones
    dbc.Row([
        # Botón de escuelas
        dbc.Col(
            dbc.Container([
                # Renglón con botón de escuelas
                dbc.Row(
                    html.A(
                        dbc.Button(
                            html.I(
                                className = "fas fa-book",
                                style = {"font-size" : "7rem", "margin" : "1.5rem", "color" : "black"}
                            ),
                            type = "button",
                            style = {"background" : "#1199EE", "border-color" : "#1199EE"}
                        ),
                        href = "/apps/escuelas"
                    ),
                    justify="center"
                ),
                # Texto del botón de escuelas
                dbc.Row(
                    html.H5(u"Por escuelas"),
                    justify="center",
                    style = {"margin-top" : "0.5rem"}
                )]
            ),
            md = 3,
            style = {"margin-bottom" : "3rem", "margin-right" : "1rem", "margin-top" : "1rem"},
            className = "d-flex justify-content-center"
        ),
        # Botón de regiones
        dbc.Col(
            dbc.Container([
                # Renglón con botón de regiones
                dbc.Row(
                    html.A(
                        dbc.Button(
                            html.I(
                                className = "fas fa-chart-bar",
                                style = {"font-size" : "7rem", "margin" : "1.5rem", "color" : "black"}
                            ),
                            type = "button",
                            style = {"background" : "#1199EE", "border-color" : "#1199EE"},
                            disabled = True
                        ),
                        href = "#"
                    ),
                    justify="center"
                ),
                # Renglón con texto de regiones
                dbc.Row(
                    html.H5(u"Por región"),
                    justify="center",
                    style = {"margin-top" : "0.5rem"}
                )]
            ),
            md = 3,
            style = {"margin-bottom" : "3rem", "margin-right" : "1rem", "margin-top" : "1rem"},
            className = "d-flex justify-content-center"
        ),
        # Botón de estado
        dbc.Col(
            dbc.Container([
                # Renglón con botón de estado
                dbc.Row(
                    html.A(
                        dbc.Button(
                            html.I(
                                className = "fas fa-map-marker-alt",
                                style = {"font-size" : "7rem", "margin" : "1.5rem 2rem 1.5rem 2rem", "color" : "black"}
                            ),
                            type = "button",
                            style = {"background" : "#1199EE", "border-color" : "#1199EE"},
                            disabled = True
                        ),
                        href = "#"
                    ),
                    justify="center"
                ),
                # Renglón con texto de estado
                dbc.Row(
                    html.H5(u"Por estado"),
                    justify="center",
                    style = {"margin-top" : "0.5rem"}
                )]
            ),
            md = 3,
            style = {"margin-bottom" : "3rem", "margin-right" : "1rem", "margin-top" : "1rem"},
            className = "d-flex justify-content-center"
        )],
        justify="center",
    )]
)

@app.callback(
    [Output('page-content', 'children'),
     Output('session', 'data')],
    Input('url', 'pathname'),
    [State('url', 'search'),
     State('session', 'data')]
)
def display_page(pathname, parametros, data):
    """
    Función que administra todos los cambios de dirección URL que ocurren en la
    aplicación.
    
    Args :
        pathname (str): ruta de la página de la aplicación que se quiere visitar.
            Algunas páginas no se mostrarán a menos de que se encuentre una sesión
            activa, por ejemplo, el reporte de escuelas.
        data (dict): diccionario con los datos de la sesión, si es None entonces
            no se encuentra ninguna sesión activa.
            
            Sirve para acceder a aplicaciones y almacenar datos importantes de la
            sesión.
        parametros (str): parametros o 'query string' del URL en caso de que se
            realice una consulta.

    Returns :
        pagina : componente de dash core, dash bootstrap o dash html con el layout
            de la página solicitada en caso de que se encuentre alguna, si no,
            regresa simplemente 404.
        data (dict): diccionario con los datos de la sesión actualizados.
    """
    data = data or {'session_active' : False, 'escuelas' : None}
    
    pagina = '404'
    
    if pathname == '/' :
        pagina = layout
    if pathname == '/apps/escuelas' :
        pagina = escuelas.cargar_plantilla_formulario()
    elif pathname == '/apps/regiones' :
        pagina = regiones.layout
    elif pathname == '/apps/estado' :
        pagina = estado.layout
    # Reporte general
    elif pathname == '/apps/reporte' :
        # Solicitud de nuevo reporte
        if parametros :
            # Separar parámetros y obtener su valor
            llave_y_valor = parametros[1:].split('&')
            ccts = []
            for item in llave_y_valor :
                llave, valor = item.split('=')
                if valor :
                    ccts.append(valor)
            
            ccts_invalidos = False
            for cct in ccts :
                ccts_invalidos |= cct not in cache['escuelas']
            
            # Si los ccts no son válidos volver al formulario
            if ccts_invalidos :
                pagina = escuelas.cargar_plantilla_formulario(
                    ccts = ccts, 
                    mensaje_error = MENSAJES_ERROR['ccts_invalidos']
                )
            # Si no se proporcionó ningún cct volver al formulario
            elif not ccts :
                pagina = escuelas.cargar_plantilla_formulario(
                    ccts = ccts, 
                    mensaje_error = MENSAJES_ERROR['ccts_vacios']
                )
            # Si los ccts son válidos generar un reporte
            else :
                # Activar la sesión
                data['session_active'] = True
                
                __escuelas = dict()
                for cct in ccts :
                    __escuelas[cct] = cache['escuelas'][cct]
                data['escuelas'] = ordenar_escuelas(__escuelas)
                
                pagina = plantilla_reporte.cargar_plantilla_reporte(
                    contenido = reporte_general.cargar_contenido_reporte_general(
                        escuelas = ordenar_escuelas(data['escuelas'])
                    )
                )
        # Solicitud de volver a la página del reporte
        elif data['session_active'] :
            pagina = plantilla_reporte.cargar_plantilla_reporte(
                contenido = reporte_general.cargar_contenido_reporte_general(
                    escuelas = ordenar_escuelas(data['escuelas'])
                )
            )
    
    # Reporte individual
    elif re.search('^/apps/reporte/32[A-Z]{3}[0-9]{4}[A-Z]{1}', pathname) and data['session_active'] :
        # Verificar que exista una sesión, si no, regresar 404
        escuelas_reporte = data['escuelas']
        cct = pathname[-10:]
        
        if cct in escuelas_reporte :
            pagina = plantilla_reporte.cargar_plantilla_reporte(
                contenido = reporte_individual.cargar_contenido_reporte_individual(
                    escuelas = escuelas_reporte, 
                    cct = cct
                )
            )
    
    return pagina, data

if __name__ == '__main__' :
    app.run_server(debug=True)
