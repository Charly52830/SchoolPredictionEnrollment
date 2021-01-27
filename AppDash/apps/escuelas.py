# -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH
from dash.exceptions import PreventUpdate

from app import app, cache

def generar_input_cct(index, cct = None) :
    """
    Genera el layout necesario para ingresar una nueva cct en el formulario.
    
    Args :
        index (int): número de cct del formulario que le corresponde al próximo
            cct.
        cct (str, opcional): cct para agregarlo en el input correspondiente en
            caso de que se tenga uno, si no, queda vacío.

    Returns
        layout que se puede agregar al final del formulario para ingresar una nueva
            cct.
    """
    layout = html.Div(
        dbc.Row([
            # Columna del input
            dbc.Col(
                dbc.Input(
                    size = "10",
                    type = "text",
                    placeholder = "Ingresa una cct",
                    name = "cct%d" % (index),
                    id = {
                        'type' : "input-cct",
                        'index' : index,
                    },
                    value = cct,
                    valid = cct in cache['escuelas'],
                    invalid = not cct in cache['escuelas'] and cct,
                ),
                md = 2,
                xs = 4,
                style = {"margin-bottom" : "0.3rem"},
                className = "d-flex justify-content-center"
            ),
            # Columna del botón para eliminar el input del formulario
            dbc.Col(
                dbc.Button(
                    html.I(className = "fas fa-times-circle"),
                    size = "sm",
                    type = "button",
                    id = {
                        'type' : 'boton-borrar-cct',
                        'index' : index
                    },
                    color = "danger",
                    style = {"background" : "red", "border-color" : "red"},
                ),
                xs = 1,
                style = {"margin-bottom" : "0.3rem"},
                className = "d-flex justify-content-center",
            )],
            justify="center",
        ),
        id = {
            "type" : "div-input",
            "index" : index
        }
    )
    
    return layout

def cargar_plantilla_formulario(ccts = [], mensaje_error = '') :
    """
    Genera el formulario por el que se ingresan las cct de las escuelas de las que
    se quiere generar un reporte.
    
    Args :
        ccts (list, opcional): lista de strings que contienen ccts (válidos e inválidos)
            para llenar el formulario con ellas.
        mensaje_error (str, opcional): mensaje de error a mostrar en el formulario en caso
            de que haya uno.
    
    Returns:
        página que contiene la pantalla previa al reporte de escuelas que contiene
            un formulario para ingresar los ccts.
    """
    # Generar un input por cada cct
    input_ccts = [generar_input_cct(i + 1, ccts[i]) for i in range(len(ccts))]
    
    # Si no se proporcionó ningún cct generar un solo input vacío
    if not input_ccts :
        input_ccts = [generar_input_cct(1)]
    
    form = html.Form([
        # Tipo de reporte
        dcc.Input(name = "tipo_reporte", value = "reporte_escuelas", type = "hidden"),
        # 
        dbc.Row(
            dbc.Col(
                html.H3(
                    u"Escribe las claves de centro de trabajo separadas por coma o un espacio",
                    style = {"text-align" : "center", "margin-top" : "2rem", "margin-bottom" : "2rem"}
                ),
                md = 6, xs = 12
            ),
            justify="center",
        ),
        # Input para múltiples ccts
        dbc.Row(
            dbc.Col(
                dbc.Input(
                    name = 'ccts', placeholder = 'Ingresa múltiples ccts', className = 'form-group'
                ),
                md = 5,
                xs = 7,
                className = "d-flex justify-content-center"
            ),
            justify="center",
        ),
        # Ccts individuales
        html.H3(
            u"O ingresa las claves del centro de trabajo",
            style = {"text-align" : "center", "margin-top" : "2rem", "margin-bottom" : "2rem"}
        )] + 
        input_ccts +
        # Renglón para el botón para agregar una nueva cct
        [dbc.Row([
            dbc.Col(
                dbc.Button(
                    html.I(className = "fas fa-plus-circle"),
                    type = "button",
                    id = "nueva-escuela-button",
                    color = "success"
                ),
                style = {"margin-top" : "1rem", "margin-bottom" : "3rem"},
                className = "d-flex justify-content-center",
            )],
            justify="center",
        ),
        # Renglón para los botones de continuar o regresar
        dbc.Row([
            # Botón para regresarse
            dbc.Col(
                html.A(
                    dbc.Button(
                        u"Regresar",
                        type = "button",
                        style = {"background" : "#FF0055", "border-color" : "#FF0055"}
                    ),
                    href = "/"
                ),
                xs = 2,
                style = {"margin-bottom" : "3rem", "margin-right" : "1rem", "margin-top" : "1rem"},
                className = "d-flex justify-content-center"
            ),
            # Botón para continuar
            dbc.Col(
                dbc.Button(
                    u"Continuar",
                    type = "submit",
                    style = {"background" : "#1199EE", "border-color" : "#1199EE"}
                ),
                xs = 2,
                style = {"margin-bottom" : "3rem", "margin-left" : "1rem", "margin-top" : "1rem"},
                className = "d-flex justify-content-center",
            )],
            justify="center",
        )],
        action = "/apps/reporte",
        id = "formulario-escuelas"
    )
    
    layout = dbc.Container([
        # Texto de encabezado
        dbc.Row(
            dbc.Col([
                html.H1(
                    u"Proyección de matrícula por escuelas de educación básica del estado de Zacatecas",
                    style = {"text-align" : "center", "margin-top" : "3rem", "margin-bottom" : "3rem"}
                )] + [
                html.H4(
                    mensaje_error,
                    style = {"text-align" : "center", "margin-top" : "2rem", "margin-bottom" : "2rem", "color": "red"}
                ) if mensaje_error else ''
                ],
                md = 6,
            ),
            className = "justify-content-center"
        ),
        form],
        fluid = True,
    )
    
    return layout

@app.callback(
    Output('formulario-escuelas', 'children'),
    Input('nueva-escuela-button', 'n_clicks'),
    State('formulario-escuelas', 'children'),
)
def agregar_nueva_escuela(click, formulario) :
    """
    Callback para agregar un nuevo input en el formulario para así agregar más
    ccts.
    
    Args:
        click (int): número de veces que se ha hecho click al botón de agregar
            nueva escuela o None si no se le ha dado click.
        formulario (:obj:): referencia a los hijos del layout del formulario.
    
    Returns:
        Formulario actualizado con un nuevo input.
    """
    if click :
        boton_submit = formulario.pop()
        boton_nueva_escuela = formulario.pop()
        
        num_ccts = len(formulario)
        formulario.append(generar_input_cct(num_ccts + 1))
        
        formulario.append(boton_nueva_escuela)
        formulario.append(boton_submit) 
    return formulario

@app.callback(
    [Output({'type' : 'input-cct', 'index' : MATCH}, 'invalid'),
     Output({'type' : 'input-cct', 'index' : MATCH}, 'valid')],
    Input({'type' : 'input-cct', 'index' : MATCH}, 'value'),
    State({'type' : 'input-cct', 'index' : MATCH}, 'value')
)
def validar_cct(blur, cct) : 
    """
    Callback que se activa cuando los input de los cct pierden foco. Evalúa si
    lo que escribió en el input es una cct que se encuentra registrada en las escuelas.
    
    Args:
        blur (:obj:): evento cuado un input-cct pierde foco.
        cct (str): valor del input que acaba de perder foco.
    
    Returns:
        Devuelve las propiedades invalid y valid del correspondiente input, dependiendo
        de si el cct es válido o no.
    
    """
    if blur :
        ans = cct.upper() in cache['escuelas']
        return not ans, ans
    else :
        raise PreventUpdate

@app.callback(
    Output({'type' : 'div-input', 'index' : MATCH}, 'children'),
    Input({'type' : 'boton-borrar-cct', 'index' : MATCH}, 'n_clicks')
)
def eliminar_cct(click) :
    """
    Callback para ocultar el renglón del formulario correspondiente a un input.
    Se activa cuando se da click sobre el botón que remueve ccts del formulario.
    
    Args:
        click (int): número de veces que se le ha dado click al botón, o None si
        no se le ha dado click.
    
    """
    if click :
        return []
    else :
        raise PreventUpdate
