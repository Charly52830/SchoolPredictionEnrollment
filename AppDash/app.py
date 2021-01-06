# -*- coding: utf-8 -*-
import dash
import dash_bootstrap_components as dbc
import json

# Hojas de estilo
FONT_AWESOME = "https://use.fontawesome.com/releases/v5.12.1/css/all.css"

# Cargar los datos de las escuelas en cache
cache = dict()
cache['escuelas'] = json.load(open("DatosEscuelas.json"))

app = dash.Dash(
    __name__, 
    suppress_callback_exceptions = True,
    external_stylesheets = [
        dbc.themes.BOOTSTRAP, 
        FONT_AWESOME,
        "assets/body-color-gray.css"
    ]
)

server = app.server
