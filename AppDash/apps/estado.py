# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_extensions.snippets import send_data_frame
from dash_extensions import Download

from app import app, cache
from apps.utilidades_reporte import GeneradorDeGraficas
from apps.FabricasNodos import *

layout = html.Div([
    dcc.Store(id = 'local-data', storage_type = 'local'),
    dcc.Store(id = 'nombre-hijo', storage_type = 'local'),
    # Hack para activar el callback al cargar la página
    html.Button(id = 'zoom-in', hidden = True),
    # Hack para activar el callback al cargar la página
    html.Button(id = 'zoom-out', hidden = True),
    # Hack para activar el callback al cargar la página
    html.Div(id = 'contenido-principal'),
])

def obtener_escuelas(id_campo) :
    """
    """
    escuelas = cache['escuelas']
    
    if id_campo == 'Estado' :
        return escuelas
    
    llave = None
    if id_campo in cache['regiones'] :
        llave = 'region'
    elif id_campo in cache['municipios'] :
        llave = 'mun'
    
    ans = dict()
    for cct in escuelas :
        if escuelas[cct][llave] == id_campo :
            ans[cct] = escuelas[cct]

    return ans

def cargar_plantilla_principal(nodo, hijo = None) :
    """
    """
    layout_nodo = nodo.layout
    if nodo.hijos :
        hijo = hijo or list(nodo.hijos.keys())[0]
    
    scatterplot = nodo.generar_scatterplot_general()
    
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
                    html.H3(layout_nodo.titulo),
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
                #"Selecciona un estado:",
                layout_nodo.label_dropdown,
                htmlFor = 'num-hijo'
            ),
            dcc.Dropdown(
                id = 'num-hijo',
                options = [
                    {'label': hijo, 'value': hijo}
                for hijo in nodo.hijos],
                value = hijo,
                style = {"margin" : "0 0.2rem 0.2rem 0.2rem"},
            ),
            html.Form([
                # Tipo de reporte
                dcc.Input(name = "tipo_reporte", value = "reporte_municipio", type = "hidden"),
                dcc.Input(name = "id_municipio", id = 'input-municipio', type = "hidden"),
                dbc.Button([
                    u"Descargar csv ",
                    html.I(className="far fa-arrow-alt-circle-down")],
                    color = "info",
                    style = {
                        "padding" : "0.2rem", 
                        "margin" : "0.2rem 0.2rem 0.2rem 0.2rem", 
                        "background" : "#1199EE"
                    },
                    id = "boton-generar-csv-individual",
                    type = "button"
                ),
                Download(id = "generar-csv-individual"),
                layout_nodo.boton_regresar,
                layout_nodo.boton_avanzar],
                action = "/apps/reporte"
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
    """
    """
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
    
# Crear nodos
layout_root = ElementosLayoutPrincipal(
    titulo = "Matrícula por estado",
    label_dropdown = "Selecciona un estado:",
    boton_regresar = dbc.Button([
        'Regresar ',
        html.I(className="fas fa-minus")],
        type = "button",
        style = {
            "padding" : "0.2rem",
            "margin" : "0.2rem 0.2rem 0.2rem 0.2rem",
            "background" : "#FF0055",
            "border-color" : "#FF0055"
        },
        id = 'zoom-out',
        disabled = True
    ),
    boton_avanzar = dbc.Button([
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
    ),
)

ROOT = Nodo(
    layout = layout_root,
    id = None,
    grafica_general = GeneradorDeGraficas.generar_scatterplot(
        cache['municipios'],
        title = 'Matrícula por municipios'
    )
)

layout_zacatecas = ElementosLayoutPrincipal(
    titulo = 'Matrícula por regiones',
    label_dropdown = 'Selecciona region:',
    boton_regresar = dbc.Button([
        'Ver estado ',
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
    boton_avanzar = dbc.Button([
        'Ver municipios ',
        html.I(className="fas fa-plus")],
        type = "button",
        style = {
            "padding" : "0.2rem",
            "margin" : "0.2rem 0.2rem 0.2rem 0.2rem",
            "background" : "#1199EE",
            "border-color" : "#1199EE"
        },
        id = 'zoom-in'
    )
)

zacatecas = Nodo(
    layout = layout_zacatecas,
    id = 'Estado',
    serie_individual = cache['estados']['Zacatecas']
)

TREE = [ROOT, zacatecas]
ROOT.agregar_hijo(zacatecas)

#nodo_municipio_guadalupe = FabricaNodosMunicipio.generar_nodo('Guadalupe')
#print(nodo_municipio_guadalupe)

regiones = cache['regiones']
for region in regiones :
    nodo_region = FabricaNodosRegion.generar_nodo(id_region = region) 
    TREE.append(nodo_region)
    zacatecas.agregar_hijo(nodo_region)
    
    for municipio in municipios_de_regiones[region] :
        nodo_municipio = FabricaNodosMunicipio.generar_nodo(id_municipio = municipio)
        TREE.append(nodo_municipio)
        nodo_region.agregar_hijo(nodo_municipio)
    
@app.callback(
    [Output('contenido-principal', 'children'),
     Output('local-data', 'data')],
    [Input('zoom-out', 'n_clicks'),
     Input('zoom-in', 'n_clicks')],
    [State('local-data', 'data'),
     State('nombre-hijo', 'data')]
)
def controlar_contenido_principal(click_regresar, click_avanzar, data, data_hijo) :
    """
    """
    # Identificar cual de los dos botones se activó
    context = dash.callback_context
    boton_activado = context.triggered[0]['prop_id'].split('.')[0]
    
    # Obtener los datos del nodo actual
    data = data or {'index-nodo': 0}
    index = data['index-nodo']
    nodo = TREE[index]

    # Para mostrar el layout el nodo actual debe tener hijos
    if not nodo.hijos :
        print("No tiene hijos")
        raise PreventUpdate
    
    pagina = None
    
    if boton_activado == "zoom-in" :
        # Obtener hijo seleccionado en el dropdown de hijos, 
        # o escoger uno por defecto en caso de que el dropdown no haya sido activado
        primer_hijo = list(nodo.hijos.keys())[0]
        data_hijo = data_hijo or {'nombre-hijo': primer_hijo}
        nombre_hijo = data_hijo['nombre-hijo']
        
        # No se puede mostrar el layout de un hijo inválido
        if nombre_hijo not in nodo.hijos :
            raise PreventUpdate
        
        hijo = nodo.hijos[nombre_hijo]
        
        # No se puede mostrar el layout de un hijo sin hijos
        if not hijo.hijos :
            raise PreventUpdate
        
        # Si el hijo es válido, actualizar el nodo para que se muestre el layout del hijo
        pagina = cargar_plantilla_principal(hijo)
        nodo = hijo
        
    elif boton_activado == "zoom-out" :
        # No se puede mostrar el layout de un padre inexistente
        if not nodo.padre :
            raise PreventUpdate
        
        # Si el padre existe, actualizar el nodo para que se muestre el layout del padre
        pagina = cargar_plantilla_principal(nodo.padre, nodo.serie_individual['nombre'])
        nodo = nodo.padre
    
    # Actualizar el layout y el índice del nodo
    pagina = pagina or cargar_plantilla_principal(nodo)
    data['index-nodo'] = TREE.index(nodo)
        
    return pagina, data

@app.callback(
    [Output('contenido-individual', 'children'),
     Output("loading-output-1", "children"),
     Output('nombre-hijo', 'data'),
     Output('input-municipio', 'value')],
    Input('num-hijo', 'value'),
    State('local-data', 'data')
)
def controlar_contenido_individual(nombre_hijo, data) :
    data = data or {'index-nodo': 0}
    index = data['index-nodo']
    nodo = TREE[index]
    
    if not nodo.hijos :
        print("No tiene hijos")
        raise PreventUpdate
    
    nodo = nodo.hijos[nombre_hijo]
    escuelas = obtener_escuelas(nodo.id)
    
    input_municipio = ''
    if nombre_hijo in cache['municipios'] :
        input_municipio = list(cache['municipios'].keys()).index(nombre_hijo)
    
    return (
        cargar_plantilla_secundaria(nodo.serie_individual, obtener_escuelas(nodo.id)), 
        None, 
        {'nombre-hijo': nombre_hijo}, 
        input_municipio
    )
