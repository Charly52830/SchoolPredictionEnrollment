# -*- coding: utf-8 -*-
import dash
import dash_bootstrap_components as dbc
import json

# Hojas de estilo
FONT_AWESOME = "https://use.fontawesome.com/releases/v5.12.1/css/all.css"

# Cargar los datos de las escuelas en cache
cache = dict()
cache['escuelas'] = json.load(open("DatosEscuelas.json"))

# Cargar los datos de las regiones en cache
cache['regiones'] = {
    "32ADG0012M" : {"nombre" : "Fresnillo Estatal"},
    "32ADG0025Q" : {"nombre" : "Fresnillo Federal"},
    "32ADG0013L" : {"nombre" : "Jalpa Estatal"},
    "32ADG0003E" : {"nombre" : "Jalpa Federal"},
    "32ADG0014K" : {"nombre" : "Tlaltenango Estatal"},
    "32ADG0004D" : {"nombre" : "Tlaltenango Federal"},
    "32ADG0015J" : {"nombre" : "Río Grande Estatal"},
    "32ADG0005C" : {"nombre" : "Río Grande Federal"},
    "32ADG0016I" : {"nombre" : "Concepción del Oro Estatal"},
    "32ADG0006B" : {"nombre" : "Concepción del Oro Federal"},
    "32ADG0017H" : {"nombre" : "Pinos Estatal"},
    "32ADG0007A" : {"nombre" : "Pinos Federal"},
    "32ADG0018G" : {"nombre" : "Jerez Estatal"},
    "32ADG0008Z" : {"nombre" : "Jerez Federal"},
    "32ADG0127N" : {"nombre" : "Loreto Estatal"},
    "32ADG0009Z" : {"nombre" : "Loreto Federal"},
    "32ADG0021U" : {"nombre" : "Guadalupe Estatal"},
    "32ADG0019F" : {"nombre" : "Guadalupe Federal"},
    "32ADG0022T" : {"nombre" : "Sombrerete Estatal"},
    "32ADG0020V" : {"nombre" : "Sombrerete Federal"},
    "32ADG0011N" : {"nombre" : "Zacatecas Estatal"},
    "32ADG0023S" : {"nombre" : "Nochistlán Federal"},
    "32ADG0026P" : {"nombre" : "Valparaíso Federal"}
}

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
