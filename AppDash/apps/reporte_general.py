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

ESCUELAS_POR_PAGINA = 20

def cargar_contenido_reporte_general(escuelas) :
    """
    Carga el layout del reporte general dados los datos de las escuelas.
    
    Args:
        escuelas (:obj: `OrderedDict`): diccionario ordenado con los datos de las
            escuelas del reporte.
    Returns:
        Layout del reporte general para mostrarlo en la plantilla del reporte.
    """
    
    mapa = GeneradorDeGraficas.generar_mapa(escuelas)
    
    contador_escuelas = {
        "Preescolar": 0,
        "Primaria": 0,
        "Secundaria": 0
    }
    
    for cct in escuelas :
        contador_escuelas[escuelas[cct]['nivel']] += 1
    
    num_paginas = 1
    if len(escuelas) <= ESCUELAS_POR_PAGINA :
        # Hack para no mostrar el slider si existe una sola página
        slider = dcc.Input(
            type = 'hidden', 
            value = 1,
            id = 'slider-paginacion'
        )
    else :
        num_paginas = len(escuelas) // ESCUELAS_POR_PAGINA + (1 if len(escuelas) % ESCUELAS_POR_PAGINA != 0 else 0)
        
        marcas = dict()
        for i in range(1, num_paginas + 1) :
            marcas[i] = {'label': "%d" % (i)}
        
        slider = dcc.Slider(
            min = 1,
            max = num_paginas,
            value = 1,
            marks = marcas,
            included = False, 
            id = 'slider-paginacion'
        )
    
    # Crear layout de la página
    layout_reporte = dbc.Container([
        # Renglón del mapa y el scatterplot
        dbc.Row([
            # Layout del Scatterplot
            dbc.Col([
                html.H5(
                    "Reporte general",
                    style = {
                        "color": "#1199EE",
                        "font-weight": "bold"
                    },
                ),
                html.H3(
                    "Resumen con la información general de las escuelas",
                    style = {"font-weight": "bold"}
                ),
                html.P(
                    "Explora la proyección, medidas de tendencia central y la " +
                    "función de autocorrelación de la matrícula de las escuelas, " + 
                    "así como su ubicación en el mapa. Da click sobre la clave " + 
                    "del centro de trabajo de una escuela para obtener más detalles de ella.",
                    style = {
                        "text-align": "justify"
                    }
                ),
                html.P("Este reporte contiene:", style = {"font-weight": "bold"}),
                html.P([
                    html.B("Preescolar: "),
                    "%d %s" % (contador_escuelas['Preescolar'], "escuela" if contador_escuelas['Preescolar'] == 1 else "escuelas")],
                    style = {"margin": "0"}
                ),
                html.P([
                    html.B("Primarias: "),
                    "%d %s" % (contador_escuelas['Primaria'], "escuela" if contador_escuelas['Primaria'] == 1 else "escuelas")],
                    style = {"margin": "0"}
                ),
                html.P([
                    html.B("Secundarias: "),
                    "%d %s" % (contador_escuelas['Secundaria'], "escuela" if contador_escuelas['Secundaria'] == 1 else "escuelas")],
                    style = {"margin": "0"}
                )],
                md = 6,
                style = {
                    "margin-top": "4rem",
                }
            ),
            # Layout del mapa
            dbc.Col(
                dcc.Graph(figure = mapa, id = 'mapa-general'),
                md = 6,
            )],
            justify = "center",
            style = {"padding-left": "1rem"}
        ),
        # Renglón del scatterplot
        dbc.Row(
            dbc.Col([
                dcc.Graph(
                    #figure = scatterplot, 
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
                md = 12
            )
        ),
        # Renglón del boxplot
        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    #figure = boxplot, 
                    id = 'boxplot-general'
                ),
                md = 12
            )
        ),
        # Controles de paginación
        dcc.Loading(
            id = "loading-graficas",
            type = "default",
            children = html.Div(id = "salida-loading-graficas"),
            #style = {"margin-top": "-5rem"}
        ),
        slider,
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
                html.Div(
                    #tabla_matricula,
                    id = 'div-tabla-matricula'
                )],
                md = 6,
            ),
            # Layout de la tabla de métricas
            dbc.Col([
                html.H4(u"Métricas de la proyección"),
                html.Div(
                    #tabla_metricas,
                    id = 'div-tabla-metricas'
                )],
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

@app.callback(
    [Output('div-tabla-matricula', 'children'),
     Output('div-tabla-metricas', 'children'),
     Output('scatterplot-general', 'figure'),
     Output('boxplot-general', 'figure'),
     Output('salida-loading-graficas', 'children')],
    Input('slider-paginacion', 'value'),
    State("session", "data")
)
def controlar_paginacion(num_pagina, data) :
    """
    Callback que controla cuáles son las escuelas que se muestran en el reporte.
    Se activa cuando cambia el valor del slider-paginacion.
    
    El número de escuelas que se muestran está definido por la constante
    ESCUELAS_POR_PAGINA.
    
    Args:
        num_pagina (int): número de página que se desea mostrar.
        data (dict): diccionario que contiene los datos de las escuelas.
    
    Returns:
        tabla_matricula (:obj: `dash_bootstrap_components.Table`): layout de una
            tabla con la matrícula de las escuelas que le corresponden a esa página.
        tabla_metricas (:obj: `dash_bootstrap_components.Table`): layout de una
            tabla con las métricas de predicción de las escuelas que le corresponden 
            a esa página.
        scatterplot (:obj: `plotly.express.line`): gráfica que contiene los 
            scatterplot de las escuelas que le corresponden a esa página.
        boxplot (:obj: `plotly.graph_objs.Figure`): gráfica que contiene los 
            boxplot de las escuelas que le corresponden a esa página.
        salida-loading-graficas (:obj:): salida del loading para mostrar el gif 
            de carga en lo que el callback se termina de ejecutar. No hace falta 
            regresar un valor específico, por lo que se regresa None.
    """
    if not num_pagina :
        raise PreventUpdate

    # Obtener escuelas
    escuelas = data['escuelas']
    escuelas_pagina = dict()
    ccts = list(escuelas.keys())
    
    # Obtener los índices que le corresponden a la página
    primer_indice_pagina = (num_pagina - 1) * ESCUELAS_POR_PAGINA
    ultimo_indice_pagina = min(num_pagina * ESCUELAS_POR_PAGINA, len(escuelas))
    
    # Crear un subconjunto de las escuelas
    for i in range(primer_indice_pagina, ultimo_indice_pagina) :
        cct = ccts[i]
        escuelas_pagina[cct] = escuelas[cct]
    
    # Crear gráficas
    tabla_matricula = GeneradorDeGraficas.generar_tabla_matricula(escuelas_pagina)
    tabla_metricas = GeneradorDeGraficas.generar_tabla_metricas(escuelas_pagina)
    scatterplot = GeneradorDeGraficas.generar_scatterplot(escuelas_pagina)
    boxplot = GeneradorDeGraficas.generar_boxplot(escuelas_pagina)
    
    return tabla_matricula, tabla_metricas, scatterplot, boxplot, None
