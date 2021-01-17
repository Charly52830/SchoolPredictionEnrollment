# -*- coding: utf-8 -*-
import dash
import dash_bootstrap_components as dbc
import json

# Hojas de estilo
FONT_AWESOME = "https://use.fontawesome.com/releases/v5.12.1/css/all.css"
GOOGLE_FONTS = "https://fonts.googleapis.com/css2?family=Poppins&display=swap"

# Cargar los datos de las escuelas en cache
cache = json.load(open("DatosEscuelas.json"))

app = dash.Dash(
    __name__, 
    suppress_callback_exceptions = True,
    external_stylesheets = [
        dbc.themes.BOOTSTRAP, 
        FONT_AWESOME,
        GOOGLE_FONTS,
    ]
)

server = app.server
