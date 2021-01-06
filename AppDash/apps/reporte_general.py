# -*- coding: utf-8 -*-
import pandas as pd
from collections import OrderedDict

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State
from dash_extensions.snippets import send_data_frame
from dash_extensions import Download
from dash.exceptions import PreventUpdate

from app import app
from apps.utilidades_reporte import GeneradorDeGraficas

def cargar_contenido_reporte_general(escuelas) :
    """
    Carga el layout del reporte general dados los datos de las escuelas.
    
    Args:
        escuelas (:obj: `OrderedDict`): diccionario ordenado con los datos de las
            escuelas del reporte.

    Returns:
        Layout del reporte general para mostrarlo en la plantilla del reporte.
    """
    scatterplot = GeneradorDeGraficas.generar_scatterplot(escuelas)
    boxplot = GeneradorDeGraficas.generar_boxplot(escuelas)
    tabla_metricas = GeneradorDeGraficas.generar_tabla_metricas(escuelas)
    tabla_matricula = GeneradorDeGraficas.generar_tabla_matricula(escuelas)
    mapa = GeneradorDeGraficas.generar_mapa(escuelas)
    
    # Crear layout de la página
    layout_reporte = dbc.Container([
        # Renglón del mapa y el scatterplot
        dbc.Row([
            # Layout del Scatterplot
            dbc.Col([
                dcc.Graph(
                    figure = scatterplot, 
                    id = 'scatterplot-general',
                    style = {
                        "margin-bottom" : "0", 
                        "padding-bottom": "0"
                    },
                ),
                html.P(
                    u"* Fuente: estadística 911",
                    className = "text-secondary",
                    style = {
                        "font-size" : "0.5rem", 
                        "margin" : "0", 
                        "padding" : "0"
                    }
                )],
                md = 6,
            ),
            # Layout del mapa
            dbc.Col(
                dcc.Graph(figure = mapa, id = 'mapa-general'),
                md = 6,
            )],
            justify = "center"
        ),
        # Renglón del boxplot
        dbc.Row(
            dbc.Col(
                dcc.Graph(figure = boxplot, id = 'boxplot-general'),
                md = 12
            )
        ),
        # Renglón de las tablas de métricas y de matrícula
        dbc.Row([
            # Layout de la tabla de matrícula
            dbc.Col([
                dbc.Container(dbc.Row([
                    html.H4(u"Matrícula por ciclo escolar"), 
                    dbc.Button([
                        u"Descargar csv ",
                        html.I(className="far fa-arrow-alt-circle-down")],
                        color = "info",
                        style = {
                            "padding" : "0.2rem", 
                            "margin" : "0 0.2rem 0.2rem 0.2rem", 
                            "background" : "#1199EE"
                        },
                        id = "descargar_csv_button"
                    ),
                    Download(id = "descargar_csv")]
                )),
                tabla_matricula],
                md = 6,
            ),
            # Layout de la tabla de métricas
            dbc.Col([
                html.H4(u"Métricas de la proyección"),
                tabla_metricas],
                md = 6,
            )]
        )],
        # Estilos del layout general
        style = {"background" : "#FFFFFF"},
        fluid = True
    )
    return layout_reporte

@app.callback(
    Output("descargar_csv", "data"), 
    Input("descargar_csv_button", "n_clicks"),
    [State("session", "data"),
     State('input-titulo-reporte', 'value')]
)
def generar_csv(n_clicks, data, titulo_reporte) :
    """
    Callback para generar un archivo csv con los datos de la matrícula de todas
    las escuelas del reporte.
    
    Args:
        n_clicks (int): número de veces que se ha dado click al botón de descargar
            csv, o None si no se a presionado ninguna vez.
        data (dict): diccionario que contiene los datos de la sesión, incluidos 
            los de las escuelas.
        titulo_reporte (str): título del reporte o None si no se a escrito nada
            en el input del título del reporte.
    
    Returns:
        Genera y descarga un archivo csv con los datos de la matrícula y la predicción
            de todas las escuelas con el nombre del título del reporte.
    """
    titulo_reporte = titulo_reporte or 'Reporte sin titulo'
    
    if n_clicks :
        escuelas = data['escuelas']
        primer_anio = min((escuelas[cct]['primer_anio'] for cct in escuelas))
        ultimo_anio = max((len(escuelas[cct]['matricula']) + escuelas[cct]['primer_anio'] for cct in escuelas)) + 5
        nombre_columnas = ["cct"] + ["%d-%d" % (anio, anio + 1) for anio in range(primer_anio, ultimo_anio)]
        matricula = [
            [cct] + [
                (escuelas[cct]['matricula'] + escuelas[cct]['pred'])[anio - escuelas[cct]['primer_anio']] if anio >= escuelas[cct]['primer_anio'] else ''
                for anio in range(primer_anio, ultimo_anio)]
        for cct in escuelas]
        dataframe = pd.DataFrame(matricula, columns = nombre_columnas)
        return send_data_frame(dataframe.to_csv, filename = "%s.csv" % (titulo_reporte))
    else :
        raise PreventUpdate
