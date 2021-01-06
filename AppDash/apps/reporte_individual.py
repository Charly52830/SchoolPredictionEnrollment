# -*- coding: utf-8 -*-
import pandas as pd
from collections import OrderedDict

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State, MATCH
from dash_extensions.snippets import send_data_frame
from dash_extensions import Download
from dash.exceptions import PreventUpdate

from app import app

from apps.utilidades_reporte import GeneradorDeGraficas

METODOS = {
    "EP" : u"opinión de expertos",
    "NF" : u"proyección ingenua",
    "SLR" : u"regresión lineal simple",
    "ARIMA" : u"el modelo ARIMA"
}

def cargar_contenido_reporte_individual(escuelas, cct) :
    """
    Función que carga el contenido de un reporte individual.
    
    Args:   
        escuelas (:obj: `OrderedDict`): diccionario ordenado con los datos de las
            escuelas del reporte.
        cct (str): cct de la escuela a generar el reporte individual.

    Returns:
        Layout del reporte individual para mostrarlo en la plantilla del reporte.
    
    """
    # Gráficas del reporte
    scatterplot = GeneradorDeGraficas.generar_scatterplot(
        {cct : escuelas[cct]}, 
        show_legend = False, 
        title = u"Proyección de matrícula de %s" % (cct)
    )
    
    boxplot = GeneradorDeGraficas.generar_boxplot(
        {cct : escuelas[cct]},
        show_legend = False,
        title = u"Medidas de tendencia central (matrícula)"
    )
    
    tabla_metricas = GeneradorDeGraficas.generar_tabla_metricas(
        {cct : escuelas[cct]},
        links_requeridos = False
    )
    tabla_matricula = GeneradorDeGraficas.generar_tabla_matricula(
        {cct : escuelas[cct]},
        links_requeridos = False
    )
	
    correlograma_acf = GeneradorDeGraficas.generar_correlograma(
        escuelas[cct]['matricula'], 
        cct = cct,
        es_acf = True
    )
    correlograma_pacf = GeneradorDeGraficas.generar_correlograma(
        escuelas[cct]['matricula'],
        cct = cct,
        es_acf = False
    )
    
    mapa = GeneradorDeGraficas.generar_mapa(
        {cct : escuelas[cct]},
        titulo = u'Ubicación de %s' % (cct)
    )
	
    # Crear layout de la página
    layout_reporte_individual = dbc.Container([
        # Renglón de las tarjetas
        dbc.Row([
            # Layout del nombre de la escuela
            dbc.Col(
                dbc.Card(dbc.CardBody(dbc.Container(dbc.Row([
                    dbc.Col([
                        html.H6(u"Nombre de la escuela", className = "card-title", style = {"font-weight":"bold"}),
                        html.P(
                            escuelas[cct]["nombre"],
                            className = "card-text"
                        )], 
                        width = 10, 
                        style = {"margin":"0", "padding":"0"}
                    ),
                    dbc.Col(
                        html.I(className="fas fa-user-circle"),
                        width = 2,
                        style = {
                            "margin" : "0", "padding" : "0",
                            "margin-top" : "auto", "margin-bottom" : "auto",
                            "font-size" : "2rem"
                        }, 
                        className = "d-flex justify-content-center"
                    )]))),
                    style = {"margin-top" : "1rem"}
                ),
                md = 3
            ),
            # Layout de la clave del centro de trabajo
            dbc.Col(
                dbc.Card(dbc.CardBody(dbc.Container(dbc.Row([
                    dbc.Col([
                        html.H6(u"Clave del centro de trabajo", className = "card-title", style = {"font-weight" : "bold"}),
                        html.P(
                            cct,
                            className = "card-text"
                        )], 
                        width = 10, 
                        style = {"margin":"0", "padding":"0"}
                    ),
                    dbc.Col(
                        html.I(className="fas fa-graduation-cap"),
                        width = 2,
                        style = {
                            "margin" : "0", "padding" : "0",
                            "margin-top" : "auto", "margin-bottom" : "auto",
                            "font-size" : "2rem"
                        }, 
                        className = "d-flex justify-content-center"
                    )]))),
                    style = {"margin-top" : "1rem"}
                ),
                md = 4
            ),
            # Layout del municipio
            dbc.Col(
                dbc.Card(dbc.CardBody(dbc.Container(dbc.Row([
                    dbc.Col([
                        html.H6(u"Municipio", className = "card-title", style = {"font-weight":"bold"}),
                        html.P(
                            escuelas[cct]["mun"],
                            className = "card-text"
                        )], 
                        width = 10, 
                        style = {"margin":"0", "padding":"0"}
                    ),
                    dbc.Col(
                        html.I(className="fas fa-map-marker-alt"),
                        width = 2,
                        style = {
                            "margin" : "0", "padding" : "0",
                            "margin-top" : "auto", "margin-bottom" : "auto",
                            "font-size" : "2rem"
                        }, 
                        className = "d-flex justify-content-center"
                    )]))),
                    style = {"margin-top" : "1rem"}
                ),
                md = 3
            ),
            # Layout del nivel
            dbc.Col(
                dbc.Card(dbc.CardBody(dbc.Container(dbc.Row([
                    dbc.Col([
                        html.H6(u"Nivel", className = "card-title", style = {"font-weight":"bold"}),
                        html.P(
                            escuelas[cct]["nivel"],
                            className = "card-text"
                        )], 
                        width = 10, 
                        style = {"margin":"0", "padding":"0"}
                    ),
                    dbc.Col(
                        html.I(className="fas fa-book-reader"),
                        width = 2,
                        style = {
                            "margin" : "0", "padding" : "0",
                            "margin-top" : "auto", "margin-bottom" : "auto",
                            "font-size" : "2rem"
                        }, 
                        className = "d-flex justify-content-center"
                    )]))),
                    style = {"margin-top" : "1rem"}
                ),
                md = 2
            )],
        ),
        # Renglón del scatterplot y el mapa
        dbc.Row([
            # Layout del scatterplot
            dbc.Col([
                dcc.Graph(figure = scatterplot),
                html.P(
                    u"* Proyección realizada utilizando %s" % (METODOS[escuelas[cct]['metodo']]),
                    className = "text-secondary",
                    style = {"font-size" : "0.5rem", "margin" : "0 0 0 4rem", "padding" : "0"}
                ),
                html.P(
                    u"* Fuente: estadística 911",
                    className = "text-secondary",
                    style = {"font-size" : "0.5rem", "margin" : "0 0 0 4rem", "padding" : "0"}
                )],
                md = 6
            ),
            # Layout del mapa
            dbc.Col([
                dcc.Graph(figure = mapa)],
                md = 6
            )]
        ),
        # Renglón del correlograma y el boxplot
        dbc.Row([
            # Layout del correlograma
            dbc.Col([
                dcc.Graph(figure = correlograma_acf)],
                md = 6
            ),
            # Layout del boxplot
            dbc.Col([
                dcc.Graph(figure = boxplot)],
                md = 6
            )]
        ),
        # Renglón de las tablas de métricas y matrícula
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
                            "padding" : "0.2rem", "margin" : "0 0.2rem 0.2rem 0.2rem", 
                            "background" : "#1199EE"
                        },
                        id = {
                            'type' : 'boton-descargar-csv-individual',
                            'index' : cct
                        }
                    ),
                    Download(
                        id = {
                            'type' : 'descargar-csv-individual',
                            'index' : cct
                        }
                    )]
                )),
                tabla_matricula],
                md = 6,
            ),
            # Layout de la tabla de métricas
            dbc.Col([
                html.H4(u"Métricas de la proyección"),
                tabla_metricas],
                md = 6,
            )],
        )],
        # Estilos del layout general
        style = {"background" : "#FFFFFF"},
        fluid = True
    )
    return layout_reporte_individual

@app.callback( 
    Output({'type' : 'descargar-csv-individual', 'index' : MATCH}, 'data'),
    Input({'type' : 'boton-descargar-csv-individual', 'index' : MATCH}, 'n_clicks'),
    [State("session", "data"),
     State({'type' : 'descargar-csv-individual', 'index' : MATCH}, 'id')]
)
def generar_csv(n_clicks, data, id_escuela) :
    """
    Callback para generar un archivo csv con los datos de la matrícula de la escuela
    del reporte.
    
    Args:
        n_clicks (int): número de veces que se ha dado click al botón de descargar
            csv, o None si no se a presionado ninguna vez.
        data (dict): diccionario que contiene los datos de la sesión, incluidos 
            los de las escuelas.
        id_escuela (dict): diccionario que contiene el id del objeto para descargar
            el archivo csv, que a su vez contiene la cct de la escuela.
    
    Returns:
        Genera y descarga un archivo csv con los datos de la matrícula y la predicción
            de todas las escuelas con el nombre de la cct de la escuela.
    """
    if n_clicks :
        cct = id_escuela['index']
        escuelas = data['escuelas']
        primer_anio = escuelas[cct]['primer_anio']
        ultimo_anio = len(escuelas[cct]['matricula']) + escuelas[cct]['primer_anio'] + 5
        nombre_columnas = ["cct"] + ["%d-%d" % (anio, anio + 1) for anio in range(primer_anio, ultimo_anio)]
        
        matricula = [cct] + [
                (escuelas[cct]['matricula'] + escuelas[cct]['pred'])[anio - primer_anio] for anio in range(primer_anio, ultimo_anio)]
        
        dataframe = pd.DataFrame([matricula], columns = nombre_columnas)
        return send_data_frame(dataframe.to_csv, filename = "%s.csv" % (cct))
    else :
        raise PreventUpdate
