import json
import pandas as pd
import numpy as np
from datetime import date

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash_extensions.snippets import send_data_frame
from dash_extensions import Download
import plotly.graph_objs as go

from app import app

botones_sidebar = dbc.Col(
    [
        dbc.Button([html.I(className="fas fa-arrow-left")], id = 'previous_button', style = {"margin-top" : "1rem"}),
        html.Br(),
        dbc.Button([html.I(className="fas fa-arrow-right")], id = 'next_button', style = {"margin-top" : "1rem"}),
        html.Br(),
        dbc.Button([html.I(className="fas fa-share-alt")], id = 'share_button', style = {"margin-top" : "1rem"}),
        html.Br(),
        dbc.Button([html.I(className="fas fa-file-pdf")], id = 'pdf_button', style = {"margin-top" : "1rem"}),
        html.Br(),
        dbc.Button([html.I(className="fas fa-file-excel")], id = 'excel_button', style = {"margin-top" : "1rem"}),
        html.Br(),
        dbc.Button([html.I(className="fas fa-question-circle")], id = 'help_button', style = {"margin-top" : "1rem"}),
    ],
)

sidebar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(dbc.Button([html.I(className="fas fa-home")], id = 'home_button')),
                ],
                align="center",
                no_gutters=True,
            ),
            href="/",
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(botones_sidebar, id="navbar-collapse", navbar=True),
    ],
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

layout = html.Div([
    # Content
    html.Div(
        [
            # Navbar
            dbc.Navbar(
                [
                    dbc.Row(
                        dbc.Col(dbc.Input(type="text", placeholder="Reporte sin titulo", style = {"text-align":"center"} )),
                        no_gutters=True,
                        className="d-flex justify-content-center",
                        align="center",
                    ),
                    dbc.Row(
                        dbc.Col(
                            "%02d/%02d/%d" % (date.today().day, date.today().month, date.today().year), 
                            style = {"font-size" : "small", "color" : "#5a6268", "margin-top" : "3px"}
                        ),
                        no_gutters=True,
                        className="d-flex justify-content-center",
                        align="center",
                    ),
                ],
                className = "d-flex justify-content-center flex-column",
                style = {
                    "border-style" : "solid none solid none", 
                    "border-width" : "thin", 
                    "border-color" : "#e6e6e6", 
                    "padding-top" : "5px",
                    "padding-bottom" : "3px",
                }
            ),
            html.Div(id = 'contenido-reporte'),
        ],
        style = {"margin-left" : "5rem"},
    ),
    # Sidebar
    sidebar,
])

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

def generar_scatterplot(escuelas, show_legend = True, title = "Proyección de marícula") :

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

    scatterplot = go.Figure()
    
    # Add traces
    for cct in escuelas :
        matricula = escuelas[cct]['matricula'] + escuelas[cct]['pred']
        
        # Agregar matricula
        add_trace(
            fig = scatterplot,
            cct = cct,
            data = matricula
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
            t=100,
            b=100
        ),
    )
    
    return scatterplot

def generar_boxplot(escuelas, show_legend = True, title = 'Box plot de la matrícula escolar') :
    # Ordenar escuelas
    CCTS_ordenados = [(np.array(escuelas[cct]["matricula"]).mean(), cct) for cct in escuelas]
    CCTS_ordenados.sort()

    # Create figure
    boxplot = go.Figure()
    
    # Add traces
    for _, cct in CCTS_ordenados :
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
        margin=dict(
            t=100,
            b=100
        ),
    )
    
    boxplot.update_layout(
	    title = title,
	    title_font = dict(size = 20),	# Tamaño del titulo
	    title_x = 0.5,	# Centrar el titulo
    )
    
    return boxplot

def generar_tabla_metricas(escuelas) :
    CCTS = list(escuelas.keys())
    MAE = [escuelas[cct]["mae"] for cct in CCTS]
    RMSE = [escuelas[cct]["rmse"] for cct in CCTS]
    MAPE = [escuelas[cct]["mape"] for cct in CCTS]
    RP = [escuelas[cct]["rp"] for cct in CCTS]

    dataframe = pd.DataFrame({
        "cct" : CCTS,
        "MAE" : MAE,
        "RMSE" : RMSE,
        "MAPE" : MAPE,
        "RP" : RP,
    })
    
    return dbc.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(len(dataframe))
        ])
    ])

def generar_tabla_matricula(escuelas) :
    CCTS = list(escuelas.keys())
    matricula = [[cct] + (escuelas[cct]["matricula"] + escuelas[cct]["pred"])[-10:] for cct in CCTS]
    anio_actual = date.today().year
    nombre_columnas = ["cct"] + ["%d\n%d" % (anio, anio + 1) for anio in range(anio_actual - 5, anio_actual + 5)]
    nombre_central = nombre_columnas[len(nombre_columnas) // 2]
    dataframe = pd.DataFrame(matricula, columns = nombre_columnas)
    
    return dbc.Table([
        html.Thead(
            html.Tr([html.Th(col, style = {"padding-left" : "0"}) for col in dataframe.columns]),
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col], style = {"padding-left" : "0", "color" : ("#1199EE" if col == nombre_central else "black")}) for col in dataframe.columns
            ]) for i in range(len(dataframe))
        ])
    ],
    #className = "table table-sm",
    className = "table-responsive",
    style = {"font-size" : "small"}
    )

def cargar_layout_reporte_general(escuelas) :
    scatterplot = generar_scatterplot(escuelas)
    boxplot = generar_boxplot(escuelas)
    tabla_metricas = generar_tabla_metricas(escuelas)
    tabla_matricula = generar_tabla_matricula(escuelas)
    
    # Crear layout de la página
    layout_reporte = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col([
                            dcc.Graph(
                                figure = scatterplot, 
                                id = 'scatterplot-general',
                                style = {"margin-bottom" : "0", "padding-bottom": "0"},
                            ),
                            html.P(
                                "* Proyección realizada utilizando opinión de expertos",
                                className = "text-secondary",
                                style = {"font-size" : "0.5rem", "margin" : "0", "padding" : "0"}
                            ),
                            html.P(
                                "* Fuente: estadística 911",
                                className = "text-secondary",
                                style = {"font-size" : "0.5rem", "margin-top" : "0", "padding" : "0"}
                            )
                        ],
                        md = 6,
                    ),
                    dbc.Col(
                        dcc.Graph(figure = boxplot, id = 'boxplot-general'),
                        md = 6,
                    ),
                ],
                justify = "center"
            ),
            dbc.Row(
                [
                    dbc.Col([
                            dbc.Container(dbc.Row([
                                html.H4("Matrícula por ciclo escolar"), 
                                dbc.Button([
                                        "Descargar csv ",
                                        html.I(className="far fa-arrow-alt-circle-down")
                                    ],
                                    color = "info",
                                    style = {"padding" : "0.2rem", "margin" : "0 0.2rem 0.2rem 0.2rem", "background" : "#1199EE"},
                                    id = "descargar_csv_button"
                                ),
                                Download(id = "descargar_csv"),
                            ])),
                            tabla_matricula,
                        ],
                        md = 6,
                    ),
                    dbc.Col([
                            html.H4("Métricas de la proyección"),
                            tabla_metricas,
                        ],
                        md = 6,
                    ),
                ],
            ),
        ],    
    )
    return layout_reporte
    
def cargar_layout_reporte_individual(escuelas, cct) :

    scatterplot = generar_scatterplot(
        {cct : escuelas[cct]}, 
        show_legend = False, 
        title = "Proyección de matrícula de %s" % (cct)
    )
    
    boxplot = generar_boxplot(
        {cct : escuelas[cct]},
        show_legend = False,
        title = "Box plot de %s" % (cct)
    )

    # Crear layout de la página
    layout_reporte_individual = dbc.Container([
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody(dbc.Container(dbc.Row([
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
                )])))),
                md = 3
            ),
            dbc.Col(dbc.Card(dbc.CardBody(dbc.Container(dbc.Row([
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
                )])))),
                md = 4
            ),
            dbc.Col(dbc.Card(dbc.CardBody(dbc.Container(dbc.Row([
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
                )])))),
                md = 3
            ),
            dbc.Col(dbc.Card(dbc.CardBody(dbc.Container(dbc.Row([
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
                )])))),
                md = 2
            )],
            style = {"margin-top": "1rem"}
        ),
        dbc.Row([
            dbc.Col([
                    dcc.Graph(figure = scatterplot)
                ],
                md = 6
            ),
            dbc.Col([
                    dcc.Graph(figure = boxplot)
                ],
                md = 6
            )]
        )]
    )
    
    return layout_reporte_individual

@app.callback(
    [Output("contenido-reporte", "children"),
     Output("next_button", "disabled"),
     Output("previous_button", "disabled")],
    [Input("next_button", "n_clicks"),
     Input("previous_button", "n_clicks")],
    [State("session", "data")]
)
def mostrar_contenido_reporte(clicks_next, clicks_previous, data) :
    escuelas = json.loads(data['json_data'])
    n = len(escuelas) + 1
    
    previous_button_disabled = False
    next_button_disabled = False
    
    indice_escuela = 0
    if clicks_next :
        indice_escuela = (clicks_next + indice_escuela) % n
    if clicks_previous :
        indice_escuela = (indice_escuela - clicks_previous + n) % n
    
    if indice_escuela == 0 :
        previous_button_disabled = True
        layout_reporte = cargar_layout_reporte_general(escuelas)
    else :
        keys = list(escuelas.keys())
        layout_reporte = cargar_layout_reporte_individual(escuelas, keys[indice_escuela - 1])
        
    if indice_escuela == n - 1 :
        next_button_disabled = True
    
    return layout_reporte, next_button_disabled, previous_button_disabled

@app.callback(Output("descargar_csv", "data"), [Input("descargar_csv_button", "n_clicks")], [State("session", "data")])
def generar_csv(n_clicks, data) :
    if n_clicks :
        escuelas = json.loads(data['json_data'])
        CCTS = list(escuelas.keys())
        matricula = [[cct] + escuelas[cct]["matricula"] + escuelas[cct]['pred'] for cct in CCTS]
        primer_anio = min((escuelas[cct]['primer_anio'] for cct in CCTS))
        num_anios = len(matricula[0]) - 1
        nombre_columnas = ["cct"] + ["%d-%d" % (anio, anio + 1) for anio in range(primer_anio, primer_anio + num_anios)]
        dataframe = pd.DataFrame(matricula, columns = nombre_columnas)
        return send_data_frame(dataframe.to_csv, filename = "matricula_escuelas.csv")
