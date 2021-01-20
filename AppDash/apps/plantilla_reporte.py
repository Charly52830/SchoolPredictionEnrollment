# -*- coding: utf-8 -*-
import re

from datetime import date
from collections import OrderedDict

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app

# Botones del sidebar (navbar de la izquierda).
botones_sidebar = dbc.Col([
    # Sección relacionada con la navegación
    html.A(
        dbc.Button(
            html.I(className = "fas fa-chart-line"),
            style = {"margin-top" : "1rem"},
        ),
        href="/apps/reporte"
    ),
    html.Br(),
    dcc.Link(
        dbc.Button(
            html.I(className = "fas fa-arrow-left"), 
            id = 'previous_button', 
            style = {"margin-top" : "1rem"}
        ),
        href = "#",
        id = "previous-link"
    ),
    html.Br(),
    dcc.Link(
        dbc.Button(
            html.I(className="fas fa-arrow-right"), 
            id = 'next_button',
            style = {"margin-top" : "1rem"},
        ),
        href = "#",
        id = "next-link"
    ),
    html.Hr(style = {"margin-bottom" : "0"}),
    # Sección relacionada con la descarga de elementos
    dbc.Button([
        html.I(className="fas fa-share-alt")], 
        id = 'share_button', 
        style = {"margin-top" : "1rem"},
        disabled = True
    ),
    html.Br(),
    dbc.Button([
        html.I(className="fas fa-file-pdf")],
        id = 'pdf_button',
        style = {"margin-top" : "1rem"},
        disabled = True
    ),
    html.Br(),
    dbc.Button([
        html.I(className="fas fa-file-excel")], 
        id = 'excel_button', 
        style = {"margin-top" : "1rem"},
        disabled = True
    ),
    html.Hr(style = {"margin-bottom" : "0"}),
    # Sección relacionada con la ayuda.
    html.A(
        dbc.Button(
            html.I(className="fas fa-question-circle"),
            id = 'help_button',
            style = {"margin-top" : "1rem"},
        ),
        href = 'https://github.com/Charly52830/SchoolPredictionEnrollment'
    )],
)

# Layout del sidebar (barra de navegación izquierda)
sidebar = dbc.Navbar([
    # Botón para regresar a la pantalla principal
    html.A(
        dbc.Row([
            dbc.Col(dbc.Button([
                html.I(className="fas fa-home")], 
                id = 'home_button')
            )],
            align="center",
            no_gutters=True,
        ),
        href="/",
    ),
    dbc.NavbarToggler(id = "navbar-toggler"),
    # Botones del sidebar
    dbc.Collapse(
        botones_sidebar, 
        id = "navbar-collapse", 
        navbar = True
    )],
    # Estilos
    color="#e6e6e6",
    style = {
        "position" : "fixed",
        "top" : 0,
        "left" : 0,
        "bottom" : 0,
        "width" : "5rem",
        "padding-top" : "1rem",
    },
    className = "nav flex-column",
)

def cargar_plantilla_reporte(contenido, titulo_reporte = None) :
    """
    Función para cargar una página que usa como plantilla el layout del reporte.
    
    Args:
        contenido (:obj:): layout a desplegar en la página junto con los elementos
            de las barras de navegación.
            
    Returns:
        layout de una página con la plantilla del reporte.
    """
    layout = html.Div([
        # Content
        html.Div([
            # Navbar
            dbc.Navbar([
                # Input para el título del reporte
                dbc.Row(
                    dbc.Col(dbc.Input(
                        type = "text",
                        placeholder = u"Reporte sin título", 
                        style = {"text-align" : "center"},
                        id = 'input-titulo-reporte',
                        value = titulo_reporte
                    )),
                    no_gutters = True,
                    className = "d-flex justify-content-center",
                    align = "center",
                ),
                # Texto para mostrar la fecha actual
                dbc.Row(
                    dbc.Col(
                        "%02d/%02d/%d" % (date.today().day, date.today().month, date.today().year), 
                        style = {
                            "font-size" : "small",
                            "color" : "#5a6268", 
                            "margin-top" : "3px"
                        }
                    ),
                    no_gutters = True,
                    className = "d-flex justify-content-center",
                    align = "center",
                )],
                className = "d-flex justify-content-center flex-column",
                style = {
                    "border-style" : "solid none solid none", 
                    "border-width" : "thin", 
                    "border-color" : "#e6e6e6", 
                    "padding-top" : "5px",
                    "padding-bottom" : "3px",
                }
            ),
            # Contenido del reporte
            html.Div(contenido, id = 'contenido-reporte')],
            style = {"margin-left" : "5rem"},
        ),
        # Sidebar
        sidebar,
    ])
    return layout

@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    """"
    Callback para que salga el botón en el sidebar cuando la pantalla 
    es pequeña.
    
    Args:
        n (int): número de veces que se a dado click al botón para mostrar el 
            resto de los botones del sidebar, o None si no se le ha dado click.
        is_open(bool) : True si los botones se están mostrando, False si no.
    
    Returns:
        Muestra u oculta los botones del sidebar dependiendo del estado.
    """
    if n:
        return not is_open
    return is_open

@app.callback(
    [Output("previous_button", "disabled"),
     Output("next_button", "disabled"),
     Output("previous-link", "href"),
     Output("next-link", "href")],
    [Input('url', 'pathname')],
    [State("session", "data")]
)
def controlar_botones_de_navegacion(pathname, data) :
    """
    Callback que controla los botones de navegación en el reporte para avanzar al
    siguiente reporte individual o regresar al reporte individual anterior.
    
    En cada llamada actualiza los href correspondientes para avanzar o retroceder
    en los reportes, y desactiva los botones correspondientes en caso de que
    se encuentre en alguno de los límites.
    
    Args:
        pathname (str): ruta de la página de la aplicación que se quiere visitar.
            Para este callback una ruta es válida si contiene el prefijo /apps/reporte
            para el reporte general o el mismo prefijo + una cct para avanzar a 
            un reporte individual.
        data (dict): diccionario con los datos de la sesión, si es None entonces
            no se encuentra ninguna sesión activa.
    
    Returns:
        actualiza el href y el estatus de los botones de navegación.
    
    """
    data = data or {'session_active' : False, 'escuelas' : None}
    CCTS = list(data['escuelas'].keys())
    
    if pathname == '/apps/reporte' and data['session_active'] :
        return True, False, "#", "reporte/%s" % (CCTS[0])
    elif re.search('^/apps/reporte/32[A-Z]{3}[0-9]{4}[A-Z]{1}', pathname) :
        cct = pathname[-10:]
        
        try :        
            cct_index = CCTS.index(cct)
        except ValueError :
            raise PreventUpdate
        
        if cct_index == len(CCTS) - 1 :
            next_disabled = True
            next_href = "#"
        else :
            next_disabled = False
            next_href = CCTS[cct_index + 1]
        
        if cct_index == 0 :
            previous_href = "/apps/reporte"
        else :
            previous_href = CCTS[cct_index - 1]
        
        return False, next_disabled, previous_href, next_href
    else :
        raise PreventUpdate

@app.callback(
    Output('data-titulo-reporte', 'data'),
    Input('input-titulo-reporte', 'value')
)
def actualizar_nombre_reporte(nombre_reporte) :
    """
    Callback para actualizar el título del reporte.
    Se activa cuando cambia el valor del input-titulo-reporte, la actualización
    se realiza en un Dcc.Storage exclusivo del nombre del reporte.
    
    Args:
        nombre_reporte (str): valor con el que se actualiza el input
    
    Returns:
        data (dict): diccionario con la llave titulo-reporte actualizada
    """
    data = {'titulo-reporte': nombre_reporte}
    return data
