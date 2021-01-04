import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH
from dash.exceptions import PreventUpdate

from app import app, cache

def generar_input_cct(index, cct = None) :
    layout = html.Div(
        dbc.Row([
            dbc.Col(
                dbc.Input(
                    size = "10",
                    type = "text",
                    placeholder = "32DJN0494Z",
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
    ccts: Lista de ccts válidos e inválidos
    """
    ccts_invalidos = False
    if ccts :
        input_ccts = []
        for i in range(len(ccts)) :
            cct = ccts[i]
            ccts_invalidos |= cct not in cache['escuelas']
            input_ccts.append(generar_input_cct(i + 1, cct))
    else :
        input_ccts = [generar_input_cct(1)]
    
    form = html.Form(
        input_ccts
        +
        [dbc.Row([
            dbc.Col(
                dbc.Button(
                    html.I(className = "fas fa-plus-circle"),
                    type = "button",
                    id = "nueva-escuela-button"
                ),
                style = {"margin-top" : "1rem", "margin-bottom" : "3rem"},
                className = "d-flex justify-content-center",
            )],
            justify="center",
        ),
        dbc.Row([
            dbc.Col(
                html.A(
                    dbc.Button(
                        "Regresar",
                        type = "button",
                        style = {"background" : "#FF0055", "border-color" : "#FF0055"}
                    ),
                    href = "/"
                ),
                xs = 2,
                style = {"margin-bottom" : "3rem", "margin-right" : "1rem", "margin-top" : "1rem"},
                className = "d-flex justify-content-center"
                
            ),
            dbc.Col(
                dbc.Button(
                    "Continuar",
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
        dbc.Row(
            dbc.Col([
                html.H1(
                    "Proyección de matrícula por escuelas de educación básica del estado de Zacatecas",
                    style = {"text-align" : "center", "margin-top" : "3rem", "margin-bottom" : "3rem"}
                ),
                html.H3(
                    "Ingresa las claves del centro de trabajo",
                    style = {"text-align" : "center", "margin-top" : "2rem", "margin-bottom" : "2rem"}
                )] + [
                html.H4(
                    mensaje_error,
                    style = {"text-align" : "center", "margin-top" : "2rem", "margin-bottom" : "2rem"}
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
    Input({'type' : 'input-cct', 'index' : MATCH}, 'n_blur'),
    State({'type' : 'input-cct', 'index' : MATCH}, 'value')
)
def validar_cct(blur, cct) : 
    if blur :
        ans = cct in cache['escuelas']
        return not ans, ans
    else :
        raise PreventUpdate

@app.callback(
    Output({'type' : 'div-input', 'index' : MATCH}, 'children'),
    Input({'type' : 'boton-borrar-cct', 'index' : MATCH}, 'n_clicks')
)
def eliminar_cct(click) :
    if click :
        return []
    else :
        raise PreventUpdate
