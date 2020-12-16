import json
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

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
                        dbc.Col("01/01/2021", style = {"font-size" : "small", "color" : "#5a6268", "margin-top" : "3px"}),
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

def cargar_layout_reporte_general(escuelas) :
    #scatterplot = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 1, 2])])
    
    # Create figure
    scatterplot = go.Figure()
    boxplot = go.Figure()
    
    # Add traces
    color = 0
    for cct in escuelas :
        matricula = escuelas[cct]['matricula'] + escuelas[cct]['pred']
        
        # Agregar matricula
        add_trace(
            fig = scatterplot,
            cct = cct,
            data = matricula
        )
        
        boxplot.add_trace(go.Box(
            y = matricula,
            name = cct,
        ))
    
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
        showlegend = True
    )
    
    boxplot.update_traces(showlegend = True)
    
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
	    title = 'Proyección de matrícula',
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
    
    boxplot.update_xaxes(
	    title_text = "Escuelas",
	    title_font = {"size": 20}
    )

    boxplot.update_yaxes(
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
	    title = 'Box plot de la matrícula escolar',
	    title_font = dict(size = 20),	# Tamaño del titulo
	    title_x = 0.5,	# Centrar el titulo
	    #height = 700
    )
    
    # Crear layout de la página
    layout_reporte = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(figure = scatterplot, id = 'scatterplot-general'),
                        md = 6,
                    ),
                    dbc.Col(
                        dcc.Graph(figure = boxplot, id = 'boxplot-general'),
                        md = 6,
                    ),
                ],
                justify = "center"
            )
        ],
    
    )
    
    return layout_reporte
    
def cargar_layout_reporte_individual(data) :
    return html.H1("En construcción")

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
        layout_reporte = cargar_layout_reporte_individual(escuelas[keys[indice_escuela - 1]])
        
    if indice_escuela == n - 1 :
        next_button_disabled = True
    
    return layout_reporte, next_button_disabled, previous_button_disabled
