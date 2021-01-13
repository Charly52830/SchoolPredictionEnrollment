# -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH
from dash.exceptions import PreventUpdate

from app import app, cache
REGIONES = cache['regiones']

def cargar_plantilla_formulario(mensaje_error = '') :
    """
    Genera el formulario por el que se ingresan las cct de las escuelas de las que
    se quiere generar un reporte.
    
    Args :
        mensaje_error (str, opcional): mensaje de error a mostrar en el formulario en caso
            de que haya uno.
    
    Returns:
        página que contiene la pantalla previa al reporte de escuelas que contiene
            un formulario para ingresar los ccts.
    """
    form = html.Form([
        # Tipo de reporte
        dcc.Input(name = "tipo_reporte", value = "reporte_region", type = "hidden"),
        # Select con la clave de las regiones
        dbc.Row([
            dbc.Col(
                html.Select(
                    [html.Option("Selecciona una región", value = "None")] +
                    [html.Option(REGIONES[clave_region]['nombre'], value = clave_region) for clave_region in REGIONES],
                    name = 'region',
                    id = 'select-region',
                    className = 'form-control',
                ),
                style = {"margin-top" : "1rem", "margin-bottom" : "3rem"},
                className = "d-flex justify-content-center",
                md = 3,
                xs = 6
            )],
            justify="center",
        ),
        # Renglón para los botones de continuar o regresar
        dbc.Row([
            # Botón para regresarse
            dbc.Col(
                html.A(
                    dbc.Button(
                        u"Regresar",
                        type = "button",
                        style = {"background" : "#FF0055", "border-color" : "#FF0055"}
                    ),
                    href = "/"
                ),
                xs = 2,
                style = {"margin-bottom" : "3rem", "margin-right" : "1rem", "margin-top" : "1rem"},
                className = "d-flex justify-content-center"
                
            ),
            # Botón para continuar
            dbc.Col(
                dbc.Button(
                    u"Continuar",
                    type = "submit",
                    style = {"background" : "#1199EE", "border-color" : "#1199EE"}
                ),
                xs = 2,
                style = {"margin-bottom" : "3rem", "margin-left" : "1rem", "margin-top" : "1rem"},
                className = "d-flex justify-content-center",
            )],
            justify="center",
        )],
        action = "/apps/reporte",
        id = "formulario-escuelas"
    )
    
    layout = dbc.Container([
        # Texto de encabezado
        dbc.Row(
            dbc.Col([
                html.H1(
                    u"Proyección de matrícula de escuelas de educación básica por región del estado de Zacatecas",
                    style = {"text-align" : "center", "margin-top" : "3rem", "margin-bottom" : "3rem"}
                ),
                html.H3(
                    u"Selecciona la región que quieres consultar",
                    style = {"text-align" : "center", "margin-top" : "2rem", "margin-bottom" : "2rem"}
                )] + [
                html.H4(
                    mensaje_error,
                    style = {"text-align" : "center", "margin-top" : "2rem", "margin-bottom" : "2rem"}
                ) if mensaje_error else ''
                ],
                md = 6,
            ),
            className = "justify-content-center"
        ),
        form],
        fluid = True,
    )
    
    return layout
