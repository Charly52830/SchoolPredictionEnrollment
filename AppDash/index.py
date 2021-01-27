# -*- coding: utf-8 -*-
import re

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State

from app import app, server, cache
from apps import escuelas, regiones, estado, plantilla_reporte, reporte_individual, reporte_general
from apps.utilidades_reporte import ordenar_escuelas

app.title = 'Matrícula SEDUZAC'
app.layout = html.Div([
    dcc.Location(id = 'url', refresh = False),
    html.Div(id = 'page-content'),
    dcc.Store(id = 'session', storage_type = 'session'),
    dcc.Store(id = 'data-titulo-reporte', storage_type = 'session'),
])

MENSAJES_ERROR = {
    "ccts_invalidos" : u"Algunas de las CCT que se ingresaron no son válidas, porfavor, escriba adecuadamente las CCT e inténtelo de nuevo",
    "ccts_vacios" : u"Porfavor, ingresa al menos una CCT para generar un reporte",
    "region_invalida" : u"La región que seleccionaste no es válida, porfavor, selecciona una región disponible."
}

REGIONES = cache['regiones']
MUNICIPIOS = cache['municipios']

def ccts_en_mayusculas(GET) :
    """
    Función que transforma a mayúsculas todas las letras de los ccts que aparecen
    en el diccionario GET.
    
    Args:
        GET (dict): diccionario que contiene los parámetros de una petición GET.
            Solo modifica los valores de la llave con formato cct%d.
            
    Returns:
        GET (dict): mismo diccionario pero con los campos de cct%d modificados.
    """
    for parametro in GET :
        if re.search("^cct\d+", parametro) :
            # Se encontró un cct como parámetro
            GET[parametro] = GET[parametro].upper()

    return GET

def delete_repeated_values(GET) :
    """
    Función que elimina las llaves de un diccionario en caso de que el valor que
    guardan se encuentre repetido.
    
    Args:
        GET (dict): diccionario a eliminar elementos.
    
    Returns:
        GET (dict): mismo diccionario pero con los elementos repetidos eliminados.
    """
    valores = set()
    
    llaves = list(GET.keys())
    for llave in llaves :
        valor = GET[llave]
        if valor in valores :
            GET.pop(llave)
        valores.add(valor)
    
    return GET

def parser_multiples_ccts(GET) :
    """
    Función que obtiene de un solo parámetro múltiples ccts que se encuentran
    separadas por coma o por espacio en un string. 
    
    Args:
        GET (dict): diccionario que contiene los parámetros de una petición GET.
            Busca por el string en la llave ccts y lo separa en los múltiples
            ccts que contiene.
    
    Returns:
        GET (dict): mismo diccionario pero con el campo ccts eliminado. En su 
            lugar contiene múltiples llaves en la forma cct%d, una por cada
            cct que contenía el parámetro ccts.
    """
    # Si el diccionario no contiene al parámetro de múltiples ccts entonces 
    # regresar de inmediato
    if 'ccts' not in GET :
        return GET
    ccts = GET['ccts']
    
    # Reemplazar las comas por simbolos de +
    ccts = ccts.replace('%2C', '+')
    
    # Separar los ccts por simbolos de +
    ccts = ccts.split('+')
    
    # Obtener el número de ccts ingresados individualmente
    ultimo_cct = 0
    for parametro in GET :
        if re.search("^cct\d+", parametro) :
            # Se encontró un cct como parámetro
            ultimo_cct = max(ultimo_cct, int(parametro[3:]))
    ultimo_cct += 1
    
    # Agregar nuevos ccts como parametros
    for cct in ccts :
        # Si el cct se encuentra vacío omitirlo
        if cct :
            GET["cct%d" % (ultimo_cct)] = cct
            ultimo_cct += 1
    
    # Eliminar parámetro de múltiples ccts
    GET.pop('ccts')
    
    return GET

def cargar_parametros(parametros) :
    """
    Función que realiza un parsing de un string para obtener los parámetros que
    se pasan por una petición GET.
    
    Args:
        parametros (str): string con los parámetros separados por &
    
    Returns:
        GET (dict): diccionario con los parámetros como llave con su valor.
    """
    GET = dict()
    
    # Separar los parámetros individuales
    llave_y_valor = parametros[1:].split('&')
    for item in llave_y_valor :
        llave, valor = item.split('=')
        GET[llave] = valor
    
    # Eliminar parámetros sin valor
    parametros = list(GET.keys())
    for parametro in parametros :
        if not GET[parametro] :
            GET.pop(parametro)
    
    return GET
    
# Layout de la página principal
layout = dbc.Container([
    # Texto de encabezado
    dbc.Row(
        dbc.Col([
            html.H2(
                u"Consulta la matrícula escolar en Zacatecas y crea reportes con su proyección",
                style = {"text-align" : "center", "margin-top" : "4rem", "margin-bottom" : "3rem"}
            )],
            md = 8,
        ),
        className = "justify-content-center"
    ),
    # Renglón con Botones
    dbc.Row([
        # Botón de escuelas
        dbc.Col(
            dbc.Container([
                # Renglón con botón de escuelas
                dbc.Row(
                    html.A(
                        dbc.Button(
                            html.I(
                                className = "fas fa-book",
                                style = {"font-size" : "7rem", "margin" : "1.5rem", "color" : "black"}
                            ),
                            type = "button",
                            style = {"background" : "#1199EE", "border-color" : "#1199EE"}
                        ),
                        href = "/apps/escuelas"
                    ),
                    justify="center"
                ),
                # Texto del botón de escuelas
                dbc.Row(
                    html.H5(u"Por escuelas"),
                    justify="center",
                    style = {"margin-top" : "0.5rem"}
                )]
            ),
            md = 3,
            style = {"margin-bottom" : "3rem", "margin-right" : "1rem", "margin-top" : "1rem"},
            className = "d-flex justify-content-center"
        ),
        # Botón de regiones
        dbc.Col(
            dbc.Container([
                # Renglón con botón de regiones
                dbc.Row(
                    html.A(
                        dbc.Button(
                            html.I(
                                className = "fas fa-chart-bar",
                                style = {"font-size" : "7rem", "margin" : "1.5rem", "color" : "black"}
                            ),
                            type = "button",
                            style = {"background" : "#1199EE", "border-color" : "#1199EE"}
                        ),
                        href = "/apps/regiones"
                    ),
                    justify="center"
                ),
                # Renglón con texto de regiones
                dbc.Row(
                    html.H5(u"Por región"),
                    justify="center",
                    style = {"margin-top" : "0.5rem"}
                )]
            ),
            md = 3,
            style = {"margin-bottom" : "3rem", "margin-right" : "1rem", "margin-top" : "1rem"},
            className = "d-flex justify-content-center"
        ),
        # Botón de estado
        dbc.Col(
            dbc.Container([
                # Renglón con botón de estado
                dbc.Row(
                    html.A(
                        dbc.Button(
                            html.I(
                                className = "fas fa-map-marker-alt",
                                style = {"font-size" : "7rem", "margin" : "1.5rem 2rem 1.5rem 2rem", "color" : "black"}
                            ),
                            type = "button",
                            style = {"background" : "#1199EE", "border-color" : "#1199EE"}
                        ),
                        href = "apps/estado"
                    ),
                    justify="center"
                ),
                # Renglón con texto de estado
                dbc.Row(
                    html.H5(u"Por municipio"),
                    justify="center",
                    style = {"margin-top" : "0.5rem"}
                )]
            ),
            md = 3,
            style = {"margin-bottom" : "3rem", "margin-right" : "1rem", "margin-top" : "1rem"},
            className = "d-flex justify-content-center"
        )],
        justify="center",
    )]
)

@app.callback(
    [Output('page-content', 'children'),
     Output('session', 'data')],
    Input('url', 'pathname'),
    [State('url', 'search'),
     State('session', 'data'),
     State('data-titulo-reporte', 'data')]
)
def display_page(pathname, parametros, data, data_titulo_reporte):
    """
    Función que administra todos los cambios de dirección URL que ocurren en la
    aplicación.
    
    Args :
        pathname (str): ruta de la página de la aplicación que se quiere visitar.
            Algunas páginas no se mostrarán a menos de que se encuentre una sesión
            activa, por ejemplo, el reporte de escuelas.
        data (dict): diccionario con los datos de la sesión, si es None entonces
            no se encuentra ninguna sesión activa.
            
            Sirve para acceder a aplicaciones y almacenar datos importantes de la
            sesión.
        parametros (str): parametros o 'query string' del URL en caso de que se
            realice una consulta.
        data_titulo_reporte (dict): nombre del reporte de la sesión activa.
    Returns :
        pagina : componente de dash core, dash bootstrap o dash html con el layout
            de la página solicitada en caso de que se encuentre alguna, si no,
            regresa simplemente 404.
        data (dict): diccionario con los datos de la sesión actualizados.
    """
    data = data or {'session_active' : False, 'escuelas' : None}
    
    pagina = None
    
    if pathname == '/' :
        pagina = layout
    if pathname == '/apps/escuelas' :
        pagina = escuelas.cargar_plantilla_formulario()
    elif pathname == '/apps/regiones' :
        pagina = regiones.cargar_plantilla_formulario()
    elif pathname == '/apps/estado' :
        pagina = estado.layout
    # Reporte general
    elif pathname == '/apps/reporte' :
        titulo_reporte = None
        
        if parametros :
            # Solicitud de nuevo reporte
            GET = cargar_parametros(parametros)
            
            # Reporte de una región
            if GET['tipo_reporte'] == 'reporte_region' :
                # Validar parámetros
                parametros_validos = 'region' in GET
                
                # Si la estructura de los parámetros no es válida regresar 404
                if not parametros_validos :
                    pagina = '404'
                # Si la región es inválida volver al formulario
                elif GET['region'] not in REGIONES :
                    pagina = regiones.cargar_plantilla_formulario(
                        mensaje_error = MENSAJES_ERROR['region_invalida']
                    )
                # Si la región existe generar un reporte
                else :
                    # Obtener las escuelas de la región
                    region = GET['region']
                
                    # Activar la sesión
                    data['session_active'] = True
                    titulo_reporte = "Escuelas en la región %s" % (REGIONES[region]['nombre'])
                    
                    __escuelas = dict()
                    for cct in cache['escuelas'] :
                        if cache['escuelas'][cct]['region'] == region :
                            __escuelas[cct] = cache['escuelas'][cct]
                    
                    # Ordenar las escuelas
                    data['escuelas'] = ordenar_escuelas(__escuelas)
                
            # Reporte de escuelas
            elif GET['tipo_reporte'] == 'reporte_escuelas' :
                # Verificar si contiene al parámetro de múltiples escuelas
                if 'ccts' in GET :
                    GET = parser_multiples_ccts(GET)
                
                # Poner todos los ccts en mayúsculas
                GET = ccts_en_mayusculas(GET)
                
                # Eliminar ccts repetidos
                GET = delete_repeated_values(GET)
            
                GET.pop('tipo_reporte')
                
                # Validar parámetros
                parametros_validos = True
                
                # Validar ccts
                ccts_invalidos = False
                ccts = []
                for llave in GET :
                    # Validar que tenga el formato de un cct seguido de un número
                    parametros_validos &= re.search("^cct\d+", llave) is not None
                    
                    if parametros_validos :
                        ccts.append(GET[llave])
                    else :
                        break
                    
                    # Validar si el cct existe
                    ccts_invalidos |= GET[llave] not in cache['escuelas']
                    
                
                # Si la estructura de los parámetros no es válida regresar 404
                if not parametros_validos :
                    pagina = '404'
                # Si los ccts no son válidos volver al formulario
                elif ccts_invalidos :
                    pagina = escuelas.cargar_plantilla_formulario(
                        ccts = ccts, 
                        mensaje_error = MENSAJES_ERROR['ccts_invalidos']
                    )
                # Si no se proporcionó ningún cct volver al formulario
                elif not ccts :
                    pagina = escuelas.cargar_plantilla_formulario(
                        ccts = ccts, 
                        mensaje_error = MENSAJES_ERROR['ccts_vacios']
                    )
                 # Si los ccts son válidos generar un reporte
                else :
                    # Activar la sesión
                    data['session_active'] = True
                    
                    # Obtener la información de las escuelas
                    __escuelas = dict()
                    
                    for cct in ccts :
                        __escuelas[cct] = cache['escuelas'][cct]
                    
                    # Ordenar las escuelas
                    data['escuelas'] = ordenar_escuelas(__escuelas)
                    
            # Reporte de municipio
            elif GET['tipo_reporte'] == 'reporte_municipio' :
                # Validar parámetros
                parametros_validos = 'id_municipio' in GET
                
                id_municipio = int(GET['id_municipio'])
                
                # Si la estructura de los parámetros no es válida regresar 404
                if not parametros_validos :
                    pagina = '404'
                # Si el municipio es inválido regresar 404
                elif id_municipio < 0 or id_municipio >= len(MUNICIPIOS) :
                    pagina = '404'
                # Si el municipio existe generar un reporte
                else :
                    # Obtener las escuelas de la región
                    municipio = list(MUNICIPIOS.keys())[id_municipio]
                
                    # Activar la sesión
                    data['session_active'] = True
                    titulo_reporte = 'Escuelas en el municipio de %s' % (municipio)
                    
                    __escuelas = dict()
                    for cct in cache['escuelas'] :
                        if cache['escuelas'][cct]['mun'] == municipio :
                            __escuelas[cct] = cache['escuelas'][cct]
                    
                    # Ordenar las escuelas
                    data['escuelas'] = ordenar_escuelas(__escuelas)
                
        # Solicitud de volver a la página del reporte
        elif data['session_active'] :
            # Obtener el titulo del reporte
            data_titulo_reporte = data_titulo_reporte or {'titulo_reporte': None}
            titulo_reporte = data_titulo_reporte['titulo-reporte']
        
        # Si se llega en este punto y la pagina sigue siendo None significa que 
        # todo salió bien. En este punto los datos del reporte se encuentran en
        # data['escuelas'] y ya se encuentran ordenados
        if not pagina :
            # Si el reporte contiene múltiples escuelas cargar el reporte general
            if len(data['escuelas']) > 1 :
                pagina = plantilla_reporte.cargar_plantilla_reporte(
                    contenido = reporte_general.cargar_contenido_reporte_general(
                        escuelas = data['escuelas']
                    ),
                    titulo_reporte = titulo_reporte
                )
            # Si el reporte contiene solo una escuela cargar el reporte individual
            else :
                cct = list(data['escuelas'])[0]
                if not titulo_reporte :
                    titulo_reporte = cct
                
                pagina = plantilla_reporte.cargar_plantilla_reporte(
                    contenido = reporte_individual.cargar_contenido_reporte_individual(
                        escuelas = data['escuelas'], 
                        cct = cct
                    ),
                    titulo_reporte = titulo_reporte
                )
    
    # Reporte individual
    elif re.search('^/apps/reporte/32[A-Z]{3}[0-9]{4}[A-Z]{1}', pathname) and data['session_active'] :
        # Verificar que exista una sesión, si no, regresar 404
        escuelas_reporte = data['escuelas']
        cct = pathname[-10:]
        
        # Obtener el titulo del reporte
        data_titulo_reporte = data_titulo_reporte or {'titulo_reporte': None}
        titulo_reporte = data_titulo_reporte['titulo-reporte']
        
        if cct in escuelas_reporte :
            pagina = plantilla_reporte.cargar_plantilla_reporte(
                contenido = reporte_individual.cargar_contenido_reporte_individual(
                    escuelas = escuelas_reporte, 
                    cct = cct
                ),
                titulo_reporte = titulo_reporte
            )
    
    if not pagina :
        pagina = '404'
    
    return pagina, data

if __name__ == '__main__' :
    app.run_server(debug=True)
