# -*- coding: utf-8 -*-
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_extensions.snippets import send_data_frame
from dash_extensions import Download

from app import app, cache
from apps.utilidades_reporte import GeneradorDeGraficas, UtilidadesTablaMetricas
from apps.FabricasNodos import municipios_de_regiones
from apps.FabricasNodos import ElementosLayoutPrincipal
from apps.FabricasNodos import Nodo
from apps.FabricasNodos import FabricaNodosRegion
from apps.FabricasNodos import FabricaNodosMunicipio

REGIONES = cache['regiones']
HIJOS_POR_PAGINA = 10

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
    Función que devuelve todas las escuelas que pertenecen al estado, a una
    región o a un municipio.
    
    Args:
        id_campo (str): identificador del elemento del que se quieren obtener las
            escuelas en su conjunto. Es la llave con la que se identifican en el
            diccionario del cache.

    Returns:
        escuelas_elemento (dict): subconjunto de escuelas de las escuelas en el
            cache['escuelas'], que pertenecen al elemento en cuestión.
    """
    escuelas = cache['escuelas']
    
    # Caso especial: regresar todas las escuelas del estado
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
    Función que genera el layout de la parte superior de la página, la cual contiene
    el scatterplot general del nodo, el dropdown con los hijos del nodo y los botones
    zoom-in, zoom-out y descargar_csv.
    
    Args:
        nodo (:obj: `FabricaNodos.Nodo`): nodo del que se quiere mostrar el layout.
        hijo (str, optional): nombre de hijo del nodo con el que se quiere iniciar
            el dropdown y el layout secundario. Si no se especifica entonces el
            hijo por defecto será el primero que aparezca en la lista de hijos.

    Returns:
        layout (:obj: `dash_html_components.Div`): layout principal de la página.
    """
    # Datos necesarios del layout (FabricaNodos.ElementosLayout)
    layout_nodo = nodo.layout
    
    # Obtener el hijo del nodo para mostrar en el dropdown
    if nodo.hijos :
        hijo = hijo or list(nodo.hijos.keys())[0]
    
    # Obtener el scatterplot general del nodo
    scatterplot = nodo.generar_scatterplot_general()
    
    # Layout de la barra de título
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
    
    # Layout que contiene a los botones y al dropdown
    tarjeta_botones = dbc.Card(
        dbc.CardBody([
            # Layout de la etiqueta del dropdown
            html.Label(
                layout_nodo.label_dropdown,
                htmlFor = 'num-hijo'
            ),
            # Layout del dropdown
            dcc.Dropdown(
                id = 'num-hijo',
                options = [
                    {'label': hijo, 'value': hijo}
                for hijo in nodo.hijos],
                value = hijo,
                style = {"margin" : "0 0.2rem 0.2rem 0.2rem"},
            ),
            # Formulario para generar un reporte por municipios. Se activa solo
            # con los nodos de regiones, cuyo botón zoom-out no tiene hijos
            # y es del tipo submit.
            html.Form([
                # Tipo de reporte
                dcc.Input(name = "tipo_reporte", value = "reporte_municipio", type = "hidden"),
                # Identificador del municipio
                dcc.Input(name = "id_municipio", id = 'input-municipio', type = "hidden"),
                # Layout del botón para descargar el csv
                dbc.Button([
                    u"Descargar csv ",
                    html.I(className="far fa-arrow-alt-circle-down")],
                    color = "info",
                    style = {
                        "padding" : "0.2rem", 
                        "margin" : "0.2rem 0.2rem 0.2rem 0.2rem", 
                        "background" : "#1199EE"
                    },
                    id = "boton-descargar-csv-estado",
                    type = "button"
                ),
                Download(id = "generar-csv-hijos"),
                # Botón zoom-in
                layout_nodo.boton_regresar,
                # Botón zoom-out
                layout_nodo.boton_avanzar],
                action = "/apps/reporte"
            )]
        ),
        style = {"margin": "0 1rem 1rem 1rem"}
    )
    
    num_paginas = 1
    series_hijos = dict()
    for hijo in nodo.hijos :
        series_hijos[hijo] = nodo.hijos[hijo].serie_individual
    
    if len(series_hijos) <= HIJOS_POR_PAGINA :
        # Hack para no mostrar el slider si existe una sola página
        slider = dcc.Input(
            type = 'hidden', 
            value = 1,
            id = 'slider-paginacion-estado'
        )
    else :
        num_paginas = len(series_hijos) // HIJOS_POR_PAGINA + (1 if len(series_hijos) % HIJOS_POR_PAGINA != 0 else 0)
        
        marcas = dict()
        for i in range(1, num_paginas + 1) :
            marcas[i] = {'label': "%d" % (i)}
        
        slider = dcc.Slider(
            min = 1,
            max = num_paginas,
            value = 1,
            marks = marcas,
            included = False, 
            id = 'slider-paginacion-estado'
        )
    
    renglon_tablas = dbc.Row([
        # Layout de la tabla de matrícula
        dbc.Col([
            html.H4(u"Matrícula por ciclo escolar"),
            html.Div(
                #tabla_matricula,
                id = 'div-tabla-matricula-estado'
            )],
            md = 7,
        ),
        # Layout de la tabla de métricas
        dbc.Col([
            html.H4(u"Métricas de la proyección"),
            html.Div(
                #tabla_metricas,
                id = 'div-tabla-metricas-estado'
            )],
            md = 5,
        )]
    )
    
    # Layout principal
    layout = html.Div([
        navbar,
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(figure = scatterplot),
                slider,
                renglon_tablas]
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
    Función que genera el layout de la parte inferior de la página, la cual contiene
    las gráficas de scatterplot, boxplot, correlograma y mapa, generadas con datos
    del hijo del nodo actual, el cual es seleccionado en el dropdown que aparece
    en el layout principal.
    
    Args:
        serie_de_tiempo (dict): datos de la serie de tiempo individual que guarda
            el nodo hijo (ver Nodos en FabricasNodos.py).
        escuelas (dict): escuelas con su ubicación que se encuentran dentro del
            nodo hijo. Las escuelas se obtienen utilizando la función obtener_escuelas
            que recibe el identificador de la serie de tiempo individual del nodo hijo.
    
    Returns:
        layout (:obj: `dash_html_components.Div`): layout de la parte inferior de
            la página.
    """
    
    # Generar gráficas de la serie de tiempo
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

    # Layout del scatterplot
    tarjeta_scatterplot = dbc.Card(
        dcc.Graph(figure = scatterplot),
        style = {"margin": "0 1rem 1rem 1rem"}
    )
    
    # Layout del mapa y el boxplot
    renglon_mapa_y_boxplot = dbc.Row([
        # Layout del boxplot
        dbc.Col(
            dbc.Card(
                dcc.Graph(figure = boxplot),
                style = {"margin": "0 0.5rem 1rem 0"}
                
            ),
            xs = 6,
            style = {"padding-right": "0"}
        ),
        # Layout del mapa
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
    
    # Layout del correlograma
    tarjeta_correlograma = dbc.Card(
        dcc.Graph(figure = correlograma_acf),
        style = {"margin": "0 1rem 1rem 1rem"}
    )
    
    # Layout secundario
    layout = html.Div([
        tarjeta_scatterplot,
        renglon_mapa_y_boxplot,
        tarjeta_correlograma]
    )
    
    return layout
    
# Crear los nodos del árbol
# Elementos a mostrar en el layout del nodo raíz, el cual contiene la información
# del estado de Zacatecas.
layout_root = ElementosLayoutPrincipal(
    titulo = "Matrícula por municipios",
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

# Nodo que contiene al estado de Zacatecas
ROOT = Nodo(
    layout = layout_root,
    id = None,
    grafica_general = GeneradorDeGraficas.generar_scatterplot(
        cache['municipios'],
        title = 'Matrícula por municipios',
        titulo_leyenda = 'Municipios'
    ),
    nombre_hijos = 'Estados'
)

# Elementos a mostrar en el layout del nodo estado, el cual contiene la 
# información las regiones de Zacatecas
layout_estado = ElementosLayoutPrincipal(
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

# Nodo que contiene a las regiones de Zacatecas
nodo_estado = Nodo(
    layout = layout_estado,
    id = 'Estado',
    serie_individual = cache['estados']['Zacatecas'],
    nombre_hijos = 'Regiones'
)

TREE = [ROOT, nodo_estado]

# Asignar aristas
ROOT.agregar_hijo(nodo_estado)
for region in REGIONES :
    # Generar un nodo por cada región
    nodo_region = FabricaNodosRegion.generar_nodo(id_region = region) 
    TREE.append(nodo_region)
    nodo_estado.agregar_hijo(nodo_region)
    
    # Para cada región, generar un nodo por cada municipio que contiene
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
    Callback para controlar el layout que se muestra en la parte superior de la
    página (scatterplot general, dropdown y botones). Funciona con nodos en
    una estructura de datos de un árbol (ver FabricaNodos.py). 
    
    El nodo raíz es el objeto llamado ROOT, y todos los nodos se encuentran 
    guardados en una lista llamada TREE. El diccionario local-data guarda el 
    índice del nodo actual en la lista TREE. Actualiza el índice del nodo actual 
    cuando se desplaza hacia el nodo padre o hacia alguno de los nodos hijos. 
    
    Este callback al actualizar el layout con la función cargar_plantilla_principal, 
    activa el callback controlar_contenido_individual que controla el layout de 
    la parte inferior de la pantalla.
    
    Args:
        click_regresar (int): número de veces que se ha dado click al botón
            zoom-out (para subir un nivel en el árbol y mostrar el layout del 
            nodo padre).
        click_avanzar (int): número de veces que se ha dado click al botón zoom-in
            (para bajar un nivel en el árbol y mostrar el layout de uno de los 
            hijos del nodo).
        data (dict): diccionario que contiene el índice en el arreglo TREE del nodo 
            del que se está mostrando el layout.
        data_hijo (dict): diccionario que contiene el nombre del hijo que se
            encuentra actualmente seleccionado en el dropdown.

    Returns:
        contenido-principal (:obj: `dash_html_components.Div`): layout generado 
            por la función cargar_plantilla_principal utilizando los datos del 
            nodo actual.
        local-data (dict): diccionario con la información actualizada del nodo
            actual. Contendrá el índice en el arreglo TREE en caso de haber dado
            click sobre el botón zoom-in, o el índice de alguno de los hijos del
            nodo en caso de haber dado click sobre el botón zoom-out.
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
    """
    Callback para controlar el layout que se muestra sobre la serie de tiempo
    individual en la parte inferior de la página (scatteplot, correlograma, boxplot
    y mapa).
    
    Args:
        nombre_hijo (str): nombre del hijo del nodo actual del que se mostrarán
            las gráficas.
        data (dict): diccionario que contiene el índice en el arreglo TREE del nodo 
            del que se está mostrando el layout.
    
    Returns:
        contenido-individual (:obj: `dash_html_components.Div`): layout generado 
            por la función cargar_plantilla_secundaria utilizando los datos del 
            hijo del nodo.
        loading-output-1 (:obj:): salida del loading para mostrar el gif de carga
            en lo que el callback se termina de ejecutar. No hace falta regresar
            un valor específico, por lo que se regresa None.
        nombre-hijo (dict): se actualiza diccionario que guarda el nombre del hijo
            que se está consultando.
        input-municipio (str): se actualiza el nombre del municipio en el formulario.
    """
    # Obtener los datos del nodo actual
    data = data or {'index-nodo': 0}
    index = data['index-nodo']
    nodo = TREE[index]
    
    # Si el nodo no tiene ningún hijo entonces no hay gráficas que mostrar
    if not nodo.hijos :
        print("No tiene hijos")
        raise PreventUpdate
    
    # Obtener el hijo del que se quieren mostrar las gráficas
    nodo = nodo.hijos[nombre_hijo]
    escuelas = obtener_escuelas(nodo.id)
    
    # Si el hijo representa a un municipio, actualizar el input del formulario
    input_municipio = ''
    if nombre_hijo in cache['municipios'] :
        input_municipio = list(cache['municipios'].keys()).index(nombre_hijo)
    
    return (
        cargar_plantilla_secundaria(nodo.serie_individual, obtener_escuelas(nodo.id)), 
        None, 
        {'nombre-hijo': nombre_hijo}, 
        input_municipio
    )

def generar_tabla_metricas(series, nombre_elementos) :
    """
    Versión de la función GeneradorDeGraficas.generar_tabla_metricas
    pero ajustada al layout de la aplicación de estado, la cual omite las columnas
    de PAG y PR y lleva menos colores.
    
    Args:
        series (:obj: `OrderedDict`): diccionario ordenado con los datos de
            todas las series que se quieren agregar a la tabla.
        nombre_elementos(str, optional): nombre de los elementos en la primer
            columna.
            
    Returns:
        objeto con el layout de la tabla.
    """
    color_por_porcentage = UtilidadesTablaMetricas.color_por_porcentage
    generar_layout_cabecera = UtilidadesTablaMetricas.generar_layout_cabecera
    
    encabezados = [
        (u"Mean Absolute Error", "MAE", "-10rem"),
        (u"Root Mean Squared Error", "RMSE", "-12rem"),
        (u"Mean Absolute Percentage Error", "MAPE", "-16rem"),
    ]
    
    # Cabecera de la tabla
    cabecera = html.Thead(html.Tr([
        html.Th(nombre_elementos)] +
        [generar_layout_cabecera(*encabezado) for encabezado in encabezados]
    ))
    
    # Cuerpo de la tabla
    cuerpo = html.Tbody([
        html.Tr([
            # Layout del nombre del campo
            html.Td(serie),
            # Layout de MAE
            html.Td(round(series[serie]["mae"], 2)),
            # Layout de RMSE
            html.Td(round(series[serie]["rmse"], 2)),
            # Layout de MAPE
            html.Td(
                round(series[serie]["mape"], 2),
                style = {
                    "color" : color_por_porcentage(
                        error = series[serie]["mape"]
                    ),
                }
            )]
        )
        for serie in series]
    )
    
    # Tabla completa
    tabla = dbc.Table([
        cabecera,
        cuerpo],
        # Estilos del layout general de la tabla.
        style = {
            "text-align" : "center",
        },
        className = "tabla-metricas"
    )
    
    return tabla

@app.callback(
    [Output('div-tabla-matricula-estado', 'children'),
     Output('div-tabla-metricas-estado', 'children')],
    Input('slider-paginacion-estado', 'value'),
    State('local-data', 'data')
)
def controlar_paginacion_tablas(num_pagina, data) :
    """
    Callback para controlar el número de series que se muestran en las tablas de
    métricas y de matrícula en la aplicación de estado. Se activa cuando el valor
    del slider-paginacion-estado cambia.
    
    Args:
        num_pagina (int): número de página a mostrar
        data (dict): diccionario que contiene el índice en el arreglo TREE del nodo 
            del que se está mostrando el layout.
    
    Returns:
        tabla_matricula (:obj: `dash_html_components.Table`): layout de una tabla
            con la matrícula de las serie sde la página.
        tabla_metricas (:obj: `dash_html_components.Table`): layout de una tabla
            con las métricas de predicción de las series de la página
    """
    # Obtener los datos del nodo actual
    data = data or {'index-nodo': 0}
    index = data['index-nodo']
    nodo = TREE[index]
    
    # Si el nodo no tiene ningún hijo entonces no hay gráficas que mostrar
    if not nodo.hijos :
        print("No tiene hijos")
        raise PreventUpdate
    
    # Obtener las series individuales de los hijos
    series_hijos = dict()
    for hijo in nodo.hijos :
        series_hijos[hijo] = nodo.hijos[hijo].serie_individual
    
    # Obtener las paginas
    llaves = list(series_hijos.keys())
    
    # Obtener los elementos de la pagina
    elementos_pagina = dict()
    primer_indice_pagina = (num_pagina - 1) * HIJOS_POR_PAGINA
    ultimo_indice_pagina = min(num_pagina * HIJOS_POR_PAGINA, len(series_hijos))
    for i in range(primer_indice_pagina, ultimo_indice_pagina) :
        llave = llaves[i]
        elementos_pagina[llave] = series_hijos[llave]
        

    # Crear tablas
    tabla_matricula = GeneradorDeGraficas.generar_tabla_matricula(
        elementos_pagina,
        links_requeridos = False,
        nombre_elementos = nodo.nombre_hijos
    )
    
    tabla_metricas = generar_tabla_metricas(elementos_pagina, nodo.nombre_hijos)
    return tabla_matricula, tabla_metricas

@app.callback(
    Output("generar-csv-hijos", "data"), 
    Input("boton-descargar-csv-estado", "n_clicks"),
    State('local-data', 'data')
)
def generar_csv(n_clicks, data) :
    """
    Callback para generar un archivo csv con los datos de la matrícula de todas
    las escuelas del reporte.
    
    Args:
        n_clicks (int): número de veces que se ha dado click al botón de descargar
            csv, o None si no se a presionado ninguna vez.
        data (dict): diccionario que contiene los datos de la sesión, incluidos 
            los de las escuelas.
    
    Returns:
        Genera y descarga un archivo csv con los datos de la matrícula y la predicción
            de los hijos del nodo.
    """
    
    if n_clicks :
        # Obtener los datos del nodo actual
        data = data or {'index-nodo': 0}
        index = data['index-nodo']
        nodo = TREE[index]
        
        # Si el nodo no tiene ningún hijo entonces no hay gráficas que mostrar
        if not nodo.hijos :
            print("No tiene hijos")
            raise PreventUpdate
        
        # Obtener las series individuales de los hijos
        series_hijos = dict()
        for hijo in nodo.hijos :
            series_hijos[hijo] = nodo.hijos[hijo].serie_individual
        
        # Obtener los años en los que se observaron las series así como los años futuros
        primer_anio = min((series_hijos[hijo]['primer_anio'] for hijo in nodo.hijos))
        ultimo_anio = max((len(series_hijos[hijo]['matricula']) + series_hijos[hijo]['primer_anio'] for hijo in nodo.hijos)) + 5
        
        # Cabecera del archivo
        nombre_columnas = [nodo.nombre_hijos] + ["%d-%d" % (anio, anio + 1) for anio in range(primer_anio, ultimo_anio)]
        
        # Contenido del archivo
        matricula = [
            [hijo] + [
                (series_hijos[hijo]['matricula'] + 
                series_hijos[hijo]['pred'])[anio - series_hijos[hijo]['primer_anio']] if anio >= series_hijos[hijo]['primer_anio'] else ''
                for anio in range(primer_anio, ultimo_anio)]
        for hijo in nodo.hijos]

        # Asignar un nombre al archivo
        if nodo.serie_individual :
            filename = "%s de %s.csv" % (nodo.nombre_hijos, nodo.serie_individual['nombre'])
        else :
            filename = "%s.csv" % (nodo.nombre_hijos)
        
        # Crear dataframe
        dataframe = pd.DataFrame(matricula, columns = nombre_columnas)
        
        return send_data_frame(dataframe.to_csv, filename = filename)
    else :
        raise PreventUpdate
