# -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_extensions.snippets import send_data_frame
from dash_extensions import Download

from app import app, cache
from apps.utilidades_reporte import GeneradorDeGraficas

layout = html.Div([
    dcc.Store(id = 'local-data', storage_type = 'local'),
    # Hack para activar el callback al cargar la página
    html.Button(id = 'zoom-in', hidden = True),
    # Hack para activar el callback al cargar la página
    html.Button(id = 'zoom-out', hidden = True),
    html.Div(id = 'contenido-principal'),
])

def cargar_plantilla_principal(scatterplot, lista_hijos) :
    navbar = dbc.Navbar([
        dbc.Row(
            dbc.Col(
                html.A(
                    dbc.Button(
                        html.I(className="fas fa-home"),
                        id = 'home_button'
                    ),
                    href = '/'
                ),
                className = "d-flex justify-content-center",
            ),
            align = "center",
            className = "d-flex justify-content-center",
        ),
        dbc.Container(
            dbc.Row(
                dbc.Col(
                    html.H3("Matrícula escolar por estado"),
                    style = {"color":"#1199EE"}
                ),
                align = "center"
            ),
            className = "d-flex justify-content-center",
        )],
        style = {
            "border-style" : "solid solid solid solid", 
            "border-width" : "thin", 
            "border-color" : "#FFFFFF",
        }
    )
    
    tarjeta_botones = dbc.Card(
        dbc.CardBody([
            html.Label(
                "Selecciona un estado:",
                htmlFor = 'num-hijo'
            ),
            dcc.Dropdown(
                id = 'num-hijo',
                options = [
                    {'label': hijo, 'value': val}
                for hijo, val in lista_hijos],
                value = lista_hijos[0][1],
                style = {"margin" : "0 0.2rem 0.2rem 0.2rem"},
            ),
            dbc.Button([
                u"Descargar csv ",
                html.I(className="far fa-arrow-alt-circle-down")],
                color = "info",
                style = {
                    "padding" : "0.2rem", 
                    "margin" : "0.2rem 0.2rem 0.2rem 0.2rem", 
                    "background" : "#1199EE"
                },
                id = "boton-generar-csv-individual"
            ),
            Download(id = "generar-csv-individual"),
            dbc.Button([
                'Regresar ',
                html.I(className="fas fa-minus")],
                type = "button",
                style = {
                    "padding" : "0.2rem",
                    "margin" : "0.2rem 0.2rem 0.2rem 0.2rem",
                    "background" : "#FF0055",
                    "border-color" : "#FF0055"
                },
                id = 'zoom-out'
            ),
            dbc.Button([
                'Ver regiones ',
                html.I(className="fas fa-plus")],
                type = "button",
                style = {
                    "padding" : "0.2rem",
                    "margin" : "0.2rem 0.2rem 0.2rem 0.2rem",
                    "background" : "#1199EE",
                    "border-color" : "#1199EE"
                },
                id = 'zoom-in'
            )]
        ),
        style = {"margin": "0 1rem 1rem 1rem"}
    )
    
    layout = html.Div([
        navbar,
        dbc.Card(
            dbc.CardBody(
                dcc.Graph(figure = scatterplot)
            ),
            style = {"margin" : "1rem"}
        ),
        tarjeta_botones,
        dcc.Loading(
            id="loading-1",
            type="default",
            children=html.Div(id="loading-output-1"),
            style = {"margin-top": "-5rem"}
        ),
        html.Div(id = 'contenido-individual')]
    )
    
    return layout

def cargar_plantilla_secundaria(serie_de_tiempo, escuelas) :

    nombre_serie = serie_de_tiempo['nombre']
    scatterplot = GeneradorDeGraficas.generar_scatterplot(
        {nombre_serie : serie_de_tiempo}, 
        show_legend = False, 
        title = u"Matrícula de %s" % (nombre_serie)
    )
    
    boxplot = GeneradorDeGraficas.generar_boxplot(
        {nombre_serie : serie_de_tiempo},
        show_legend = False,
        title = u"Medidas de tendencia central (matrícula)"
    )
    
    mapa = GeneradorDeGraficas.generar_mapa(
        escuelas,
        titulo = u'Escuelas en %s' % (nombre_serie)
    )
    
    correlograma_acf = GeneradorDeGraficas.generar_correlograma(
        serie_de_tiempo['matricula'],
        cct = nombre_serie,
        es_acf = True
    )

    tarjeta_scatterplot = dbc.Card(
        dcc.Graph(figure = scatterplot),
        style = {"margin": "0 1rem 1rem 1rem"}
    )
    
    renglon_mapa_y_boxplot = dbc.Row([
        dbc.Col(
            dbc.Card(
                dcc.Graph(figure = boxplot),
                style = {"margin": "0 0.5rem 1rem 0"}
                
            ),
            xs = 6,
            style = {"padding-right": "0"}
        ),
        dbc.Col(
            dbc.Card(
                dcc.Graph(figure = mapa),
                style = {"margin": "0 0 1rem 0.5rem"}
                
            ),
            xs = 6,
            style = {"padding-left": "0"}
        )],
        style = {"margin": "0"}
    )
    
    tarjeta_correlograma = dbc.Card(
        dcc.Graph(figure = correlograma_acf),
        style = {"margin": "0 1rem 1rem 1rem"}
    )
    
    layout = html.Div([
        tarjeta_scatterplot,
        renglon_mapa_y_boxplot,
        tarjeta_correlograma
        ]
    )
    
    return layout
    
def cargar_contenido_estado() :
    scatterplot = GeneradorDeGraficas.generar_scatterplot(
        cache['municipios'],
        title = 'Matrícula por municipios'
    )
    
    lista_hijos = [
        ('Zacatecas', 'Zacatecas'),
        ('Aguascalientes', 'Aguascalientes')
    ]
    
    return cargar_plantilla_principal(scatterplot, lista_hijos)

def cargar_contenido_regiones() :
    return html.H1("Regiones en construcción")

def cargar_contenido_municipios(id_region) :
    return html.H1("Municipios en construcción")

@app.callback(
    [Output('contenido-principal', 'children'),
     Output('local-data', 'data')],
    [Input('zoom-out', 'n_clicks'),
     Input('zoom-in', 'n_clicks')],
    [State('local-data', 'data')]
)
def controlar_contenido_principal(click_regresar, click_avanzar, data) :
    data = data or {'nivel' : 'estado', 'id' : 'estado'}
    pagina = '404'
    
    if click_avanzar :
        pagina = html.H1("Estas avanzando")
    elif click_regresar :
        pagina = html.H1("Estas retrocediendo")
    else :
        # Cargar página por default
        if data['nivel'] == 'estado' :
            pagina = cargar_contenido_estado()
        elif data['nivel'] == 'regiones' :
            pagina = cargar_contenido_regiones()
        elif data['nivel'] == 'municipios' :
            pagina = cargar_contenido_municipios(id_region = data['id'])
        else :
            raise PreventUpdate
        
    return pagina, data

@app.callback(
    [Output('contenido-individual', 'children'),
     Output("loading-output-1", "children")],
    Input('num-hijo', 'value'),
    State('local-data', 'data')
)
def controlar_contenido_individual(valor, data) :
    data = data or {'nivel' : 'estado', 'id' : 'estado'}
    
    return cargar_plantilla_secundaria(cache['estado'], cache['escuelas']), None
