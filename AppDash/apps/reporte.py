import json
import pandas as pd
import numpy as np
import re
from collections import OrderedDict

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from datetime import date
from dash.dependencies import Input, Output, State, MATCH
from dash_extensions.snippets import send_data_frame
from dash_extensions import Download
from statsmodels.tsa.stattools import acf, pacf
from dash.exceptions import PreventUpdate

from app import app

METODOS = {
    "EP" : "opinión de expertos",
    "NF" : "proyección ingenua",
    "SLR" : "regresión lineal simple",
    "ARIMA" : "el modelo ARIMA"
}

def ordenar_escuelas(escuelas) :
    escuelas_ordenadas = OrderedDict()
    CCTS_ordenados = [(np.array(escuelas[cct]["matricula"]).mean(), cct) for cct in escuelas]
    CCTS_ordenados.sort()
    
    for _, cct in CCTS_ordenados :
        escuelas_ordenadas[cct] = escuelas[cct]
    
    return escuelas_ordenadas

botones_sidebar = dbc.Col([
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
    dbc.Button([
        html.I(className="fas fa-share-alt")], 
        id = 'share_button', 
        style = {"margin-top" : "1rem"}
    ),
    html.Br(),
    dbc.Button([
        html.I(className="fas fa-file-pdf")],
        id = 'pdf_button',
        style = {"margin-top" : "1rem"}
    ),
    html.Br(),
    dbc.Button([
        html.I(className="fas fa-file-excel")], 
        id = 'excel_button', 
        style = {"margin-top" : "1rem"}
    ),
    html.Hr(style = {"margin-bottom" : "0"}),
    dbc.Button([
        html.I(className="fas fa-question-circle")],
        id = 'help_button',
        style = {"margin-top" : "1rem"}
    )],
)

sidebar = dbc.Navbar([
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
    dbc.Collapse(
        botones_sidebar, 
        id = "navbar-collapse", 
        navbar = True
    )],
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

def cargar_plantilla_reporte(contenido) :
    """
    """
    layout = html.Div([
        # Content
        html.Div([
            # Navbar
            dbc.Navbar([
                dbc.Row(
                    dbc.Col(dbc.Input(
                        type = "text",
                        placeholder = "Reporte sin titulo", 
                        style = {"text-align":"center"}
                    )),
                    no_gutters = True,
                    className = "d-flex justify-content-center",
                    align = "center",
                ),
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
            html.Div(contenido, id = 'contenido-reporte')],
            style = {"margin-left" : "5rem"},
        ),
        # Sidebar
        sidebar,
    ])
    return layout

# Callback para que salga el botón en la barra de navegación cuando la pantalla es pequeña
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

def generar_mapa_general(escuelas) :
    """
    """
    escuelas_por_nivel = {
        "Preescolar" : [],
        "Primaria" : [],
        "Secundaria" : []
    }
    
    for cct in escuelas :
        escuelas_por_nivel[escuelas[cct]["nivel"]].append(cct)
    
    mapa = go.Figure()
    mapa.add_trace(go.Scattermapbox(
        lat = [escuelas[cct]["lat"] for cct in escuelas_por_nivel["Primaria"]],
        lon = [escuelas[cct]["lng"] for cct in escuelas_por_nivel["Primaria"]],
        name = "Primarias",
        mode = 'markers',
        marker = go.scattermapbox.Marker(size = 7),
        text = ["%s (%d alumnos)" % (cct, escuelas[cct]["matricula"][-1]) for cct in escuelas_por_nivel["Primaria"]]
    ))
    
    mapa.add_trace(go.Scattermapbox(
        lat = [escuelas[cct]["lat"] for cct in escuelas_por_nivel["Preescolar"]],
        lon = [escuelas[cct]["lng"] for cct in escuelas_por_nivel["Preescolar"]],
        name = "Preescolares",
        mode = 'markers',
        marker = go.scattermapbox.Marker(size = 7),
        text = ["%s (%d alumnos)" % (cct, escuelas[cct]["matricula"][-1]) for cct in escuelas_por_nivel["Preescolar"]]
    ))
    
    mapa.add_trace(go.Scattermapbox(
        lat = [escuelas[cct]["lat"] for cct in escuelas_por_nivel["Secundaria"]],
        lon = [escuelas[cct]["lng"] for cct in escuelas_por_nivel["Secundaria"]],
        name = "Secundarias",
        mode = 'markers',
        marker = go.scattermapbox.Marker(size = 7),
        text = ["%s (%d alumnos)" % (cct, escuelas[cct]["matricula"][-1]) for cct in escuelas_por_nivel["Secundaria"]]
    ))
    
    # Update layout
    mapa.update_layout(
        mapbox_style = "carto-positron",
        mapbox = {
            # Centro de Zacatecas
            'center': go.layout.mapbox.Center(lat = 23.1719, lon = -102.861),
            'zoom': 5.65
        },
        title = "Ubicación de las escuelas",
	    title_font = dict(size = 20),	# Tamaño del titulo
	    title_x = 0.5,	# Centrar el titulo,
	    margin=dict(b = 15),
    )
    
    return mapa

def generar_mapa_individual(escuela, cct) :
    """
    """
    mapa = go.Figure(go.Scattermapbox(
        lat = [escuela["lat"]],
        lon = [escuela["lng"]],
        mode = 'markers',
        marker=go.scattermapbox.Marker(
            size=14
        ),
        text = [cct]
    ))
    
    # Update layout
    mapa.update_layout(
        mapbox_style = "carto-positron",
        mapbox = {
            # Centro de Zacatecas
            'center': go.layout.mapbox.Center(lat = 23.1719, lon = -102.861),
            'zoom': 5.65
        },
        title = 'Ubicación de %s' % (cct),
	    title_font = dict(size = 20),	# Tamaño del titulo
	    title_x = 0.5,	# Centrar el titulo
	    margin=dict(b = 15),
    )
    
    return mapa

def generar_correlograma(escuela, cct, es_acf = True) :
    """
    """
    if es_acf :
        title = "ACF de %s" % (cct)
        if len(escuela) == 1 :
            correlacion = np.array([1])
        else :
            correlacion = np.array(acf(escuela, nlags = len(escuela) - 1))
    else :
        title = "PACF de %s" % (cct)
        if len(escuela) == 1 :
            correlacion = np.array([1])
        else :
            correlacion = np.array(pacf(escuela, nlags = len(escuela) - 1))
    
    # Create figure
    correlograma = go.Figure(data=[go.Bar(y=correlacion)])
    
    # Update axes
    correlograma.update_layout(
	    xaxis = dict(
		    autorange = True,
		    rangeslider = dict(
			    autorange = True,
			    range = [0, len(escuela)]
		    ),
	    ),
	    title = title,
	    title_font = dict(size = 20),	# Tamaño del titulo
	    title_x = 0.5,	# Centrar el titulo
	    #height = 700,	# Pixeles de altura
    )
    
    correlograma.update_xaxes(
	    title_text = "Lag",
	    title_font = {"size": 20}
    )

    correlograma.update_yaxes(
	    title_text = "ACF" if es_acf else "PACF",
	    title_font = {"size": 20}
    )
    
    # Update layout
    correlograma.update_layout(
        #dragmode="zoom",
        hovermode="x",
        #height=600,
        template="plotly_white",
    )
    
    return correlograma

def generar_scatterplot(escuelas, show_legend = True, title = "Proyección de matrícula") :
    """
    """
    def add_trace(fig, cct, data, seed_year = 1998) :
        scatter = go.Scatter(
            x = ["%d-08-01" % (seed_year + i) for i in range(len(data))],
            y = [str(i) for i in data],
            name = cct,
            text = [str(i) for i in data],
            yaxis="y",
            mode = 'lines+markers',
        )
        fig.add_trace(scatter)
    
    # Create figure
    scatterplot = go.Figure()
    
    # Add traces
    for cct in escuelas :
        matricula = escuelas[cct]['matricula'] + escuelas[cct]['pred']
        
        # Agregar matricula
        add_trace(
            fig = scatterplot,
            cct = cct,
            data = matricula,
            seed_year = escuelas[cct]['primer_anio']
        )
    
    # Add shapes
    scatterplot.update_layout(
        shapes = [
            dict(
                fillcolor="rgba(77, 213, 0, 0.2)",
                line={"width": 0},
                type="rect",
                x0="2020-01-01",
                x1="2021-01-01",
                xref="x",
                y0=0,
                y1=1.0,
                yref="paper"
            ),
            dict(
                fillcolor="rgba(144, 217, 0, 0.3)",
                line={"width": 0},
                type="rect",
                x0="2021-01-01",
                x1="2022-01-01",
                xref="x",
                y0=0,
                y1=1.0,
                yref="paper"
            ),
            dict(
                fillcolor="rgba(213, 221, 0, 0.3)",
                line={"width": 0},
                type="rect",
                x0="2022-01-01",
                x1="2023-01-01",
                xref="x",
                y0=0,
                y1=1.0,
                yref="paper"
            ),
            dict(
                fillcolor="rgba(225, 165, 0, 0.3)",
                line={"width": 0},
                type="rect",
                x0="2023-01-01",
                x1="2024-01-01",
                xref="x",
                y0=0,
                y1=1.0,
                yref="paper"
            ),
            dict(
                fillcolor="rgba(229, 99, 0, 0.3)",
                line={"width": 0},
                type="rect",
                x0="2024-01-01",
                x1="2025-01-01",
                xref="x",
                y0=0,
                y1=1.0,
                yref="paper"
            ),
        ]
    )
    
    # Style all the traces
    scatterplot.update_traces(
        hoverinfo = "name+x+text",
        showlegend = show_legend
    )
    
    # Update axes
    scatterplot.update_layout(
	    xaxis = dict(
		    autorange = True,
		    range = ["1998-08-01", "2025-08-01"],
		    rangeslider = dict(
			    autorange = True,
			    range = ["1998-08-01", "2025-08-01"]
		    ),
		    type = "date",
	    ),
	    title = title,
	    title_font = dict(size = 20),	# Tamaño del titulo
	    title_x = 0.5,	# Centrar el titulo
	    #height = 700,	# Pixeles de altura
    )
    
    scatterplot.update_xaxes(
	    title_text = "Ciclo escolar",
	    title_font = {"size": 20}
    )

    scatterplot.update_yaxes(
	    title_text = "Alumnos",
	    title_font = {"size": 20}
    )
    
    # Update layout
    scatterplot.update_layout(
        dragmode="zoom",
        hovermode="x",
        #height=600,
        template="plotly_white",
        margin=dict(
            b=50
        ),
    )
    
    return scatterplot

def generar_boxplot(escuelas, show_legend = True, title = 'Box plot de la matrícula escolar') :
    """
    """
    # Create figure
    boxplot = go.Figure()
    
    # Add traces
    for cct in escuelas :
        matricula = escuelas[cct]['matricula'] + escuelas[cct]['pred']
        
        boxplot.add_trace(go.Box(
            y = matricula,
            name = cct,
        ))
    
    # Style all the traces
    boxplot.update_traces(showlegend = show_legend)
    
    # Update axes
    boxplot.update_xaxes(
	    title_text = "Escuelas",
	    title_font = {"size": 20}
    )

    boxplot.update_yaxes(
	    title_text = "Alumnos",
	    title_font = {"size": 20}
    )
    
    # Update layout
    boxplot.update_layout(
        dragmode="zoom",
        hovermode="x",
        #height=600,
        template="plotly_white",
    )
    
    boxplot.update_layout(
	    title = title,
	    title_font = dict(size = 20),	# Tamaño del titulo
	    title_x = 0.5,	# Centrar el titulo
    )
    
    return boxplot

def generar_tabla_metricas(escuelas, links_requeridos = True) :
    """
    """
    return dbc.Table([
        html.Thead(
            html.Tr([
                html.Th("cct"),
                html.Th("MAE"),
                html.Th("RMSE"),
                html.Th("MAPE"),
                html.Th("RP")]
            )
        ),
        html.Tbody([
            html.Tr([
                html.Td(
                    html.A(cct, href = "reporte/%s" % (cct), id = "link-escuela") if links_requeridos else cct, 
                    style = {
                        "padding-left" : "0"
                    }
                ),
                html.Td(escuelas[cct]["mae"]),
                html.Td(escuelas[cct]["rmse"]),
                html.Td(escuelas[cct]["mape"]),
                html.Td(escuelas[cct]["rp"])] 
            ) for cct in escuelas]
        )]
    )

def generar_tabla_matricula(escuelas, links_requeridos = True) :
    """
    """
    # Cabecera de la tabla
    anio_actual = date.today().year
    nombre_columnas = ["cct"] + ["%d\n%d" % (anio, anio + 1) for anio in range(anio_actual - 5, anio_actual + 5)]
    cabecera = html.Thead(
        html.Tr([
            html.Th(
                nombre_col,
                style = {"padding-left" : "0"}
            ) for nombre_col in nombre_columnas]
        )
    )
    
    # Cuerpo de la tabla
    cuerpo = html.Tbody([
        html.Tr(
            # cct
            [html.Td(
                html.A(cct, href = "reporte/%s" % (cct), id = "link-escuela") if links_requeridos else cct,
                style = {"padding-left" : "0"}
            )] + 
            # Últimos 4 años
            [html.Td(
                escuelas[cct]["matricula"][-(5 - i)] if len(escuelas[cct]["matricula"]) >= 5 - i else '',
                style = {"padding-left" : "0"}
            ) for i in range(4)] + 
            # Último año de color rojo
            [html.Td(
                escuelas[cct]["matricula"][-1],
                style = {
                    "padding-left" : "0",
                    "color" : "#FF0055"
                }
            )] + 
            # Predicción
            [html.Td(
                pred,
                style = {"padding-left" : "0"}
            ) for pred in escuelas[cct]["pred"]]
        )
    for cct in escuelas])
    
    # Tabla
    tabla = dbc.Table([
        cabecera,
        cuerpo],
        className = "table-responsive",
        style = {"font-size" : "small"}
    )
    return tabla

def cargar_layout_reporte_general(escuelas) :
    """
    """
    scatterplot = generar_scatterplot(escuelas)
    boxplot = generar_boxplot(escuelas)
    tabla_metricas = generar_tabla_metricas(escuelas)
    tabla_matricula = generar_tabla_matricula(escuelas)
    mapa = generar_mapa_general(escuelas)
    
    # Crear layout de la página
    layout_reporte = dbc.Container([
        dbc.Row([
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
                    "* Fuente: estadística 911",
                    className = "text-secondary",
                    style = {
                        "font-size" : "0.5rem", 
                        "margin" : "0", 
                        "padding" : "0"
                    }
                )],
                md = 6,
            ),
            dbc.Col(
                dcc.Graph(figure = mapa, id = 'mapa-general'),
                md = 6,
            )],
            justify = "center"
        ),  # Final primer renglón
        dbc.Row(
            dbc.Col(
                dcc.Graph(figure = boxplot, id = 'boxplot-general'),
                md = 12
            )
        ),  # Final segundo renglón
        dbc.Row([
            dbc.Col([
                dbc.Container(dbc.Row([
                    html.H4("Matrícula por ciclo escolar"), 
                    dbc.Button([
                        "Descargar csv ",
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
            dbc.Col([
                html.H4("Métricas de la proyección"),
                tabla_metricas],
                md = 6,
            )]
        )],  # Final tercer renglón
        style = {"background" : "#FFFFFF"},
        fluid = True
    )
    return layout_reporte
    
def cargar_layout_reporte_individual(escuelas, cct) :
    """
    """
    scatterplot = generar_scatterplot(
        {cct : escuelas[cct]}, 
        show_legend = False, 
        title = "Proyección de matrícula de %s" % (cct)
    )
    
    boxplot = generar_boxplot(
        {cct : escuelas[cct]},
        show_legend = False,
        title = "Medidas de tendencia central (matrícula)"
    )
    
    tabla_metricas = generar_tabla_metricas(
        {cct : escuelas[cct]},
        links_requeridos = False
    )
    tabla_matricula = generar_tabla_matricula(
        {cct : escuelas[cct]},
        links_requeridos = False
    )
	
    correlograma_acf = generar_correlograma(
        escuelas[cct]['matricula'], 
        cct = cct,
        es_acf = True
    )
    correlograma_pacf = generar_correlograma(
        escuelas[cct]['matricula'],
        cct = cct,
        es_acf = False
    )
    
    mapa = generar_mapa_individual(escuelas[cct], cct)
	
    # Crear layout de la página
    layout_reporte_individual = dbc.Container([
        dbc.Row([
            dbc.Col(
                dbc.Card(dbc.CardBody(dbc.Container(dbc.Row([
                    dbc.Col([
                        html.H6("Nombre de la escuela", className = "card-title", style = {"font-weight":"bold"}),
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
            dbc.Col(
                dbc.Card(dbc.CardBody(dbc.Container(dbc.Row([
                    dbc.Col([
                        html.H6("Clave del centro de trabajo", className = "card-title", style = {"font-weight" : "bold"}),
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
            dbc.Col(
                dbc.Card(dbc.CardBody(dbc.Container(dbc.Row([
                    dbc.Col([
                        html.H6("Municipio", className = "card-title", style = {"font-weight":"bold"}),
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
            dbc.Col(
                dbc.Card(dbc.CardBody(dbc.Container(dbc.Row([
                    dbc.Col([
                        html.H6("Nivel", className = "card-title", style = {"font-weight":"bold"}),
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
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure = scatterplot),
                html.P(
                    "* Proyección realizada utilizando %s" % (METODOS[escuelas[cct]['metodo']]),
                    className = "text-secondary",
                    style = {"font-size" : "0.5rem", "margin" : "0 0 0 4rem", "padding" : "0"}
                ),
                html.P(
                    "* Fuente: estadística 911",
                    className = "text-secondary",
                    style = {"font-size" : "0.5rem", "margin" : "0 0 0 4rem", "padding" : "0"}
                )],
                md = 6
            ),
            dbc.Col([
                dcc.Graph(figure = mapa)],
                md = 6
            )]
        ),
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure = correlograma_acf)],
                md = 6
            ),
            dbc.Col([
                dcc.Graph(figure = boxplot)],
                md = 6
            )]
        ),
        dbc.Row([
            dbc.Col([
                dbc.Container(dbc.Row([
                    html.H4("Matrícula por ciclo escolar"), 
                    dbc.Button([
                        "Descargar csv ",
                        html.I(className="far fa-arrow-alt-circle-down")],
                        color = "info",
                        style = {
                            "padding" : "0.2rem", "margin" : "0 0.2rem 0.2rem 0.2rem", 
                            "background" : "#1199EE"
                        },
                        id = "descargar_csv_button"
                    ),
                    Download(id = "descargar_csv")]
                )),
                tabla_matricula],
                md = 6,
            ),
            dbc.Col([
                html.H4("Métricas de la proyección"),
                tabla_metricas],
                md = 6,
            )],
        )],
        style = {"background" : "#FFFFFF"},
        fluid = True
    )
    return layout_reporte_individual

@app.callback(
    [Output("previous_button", "disabled"),
     Output("next_button", "disabled"),
     Output("previous-link", "href"),
     Output("next-link", "href")],
    [Input('url', 'pathname')],
    [State("session", "data"),
     State("next-link", "href")]
)
def controlar_botones_de_navegacion(pathname, data, napadas) :
    data = data or {'session_active' : False, 'json_data' : None}
    CCTS = list(ordenar_escuelas(data['escuelas']).keys())
    
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

@app.callback(Output("descargar_csv", "data"), [Input("descargar_csv_button", "n_clicks")], [State("session", "data")])
def generar_csv(n_clicks, data) :
    if n_clicks :
        escuelas = ordenar_escuelas(data['escuelas'])
        primer_anio = min((escuelas[cct]['primer_anio'] for cct in escuelas))
        ultimo_anio = max((len(escuelas[cct]['matricula']) + escuelas[cct]['primer_anio'] for cct in escuelas)) + 5
        nombre_columnas = ["cct"] + ["%d-%d" % (anio, anio + 1) for anio in range(primer_anio, ultimo_anio)]
        matricula = [
            [cct] + [
                (escuelas[cct]['matricula'] + escuelas[cct]['pred'])[anio - escuelas[cct]['primer_anio']] if anio >= escuelas[cct]['primer_anio'] else ''
                for anio in range(primer_anio, ultimo_anio)]
        for cct in escuelas]
        dataframe = pd.DataFrame(matricula, columns = nombre_columnas)
        return send_data_frame(dataframe.to_csv, filename = "matricula_escuelas.csv")
