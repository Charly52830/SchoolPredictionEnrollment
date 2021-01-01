import dash
import dash_bootstrap_components as dbc
import json

# Hojas de estilo
FONT_AWESOME = "https://use.fontawesome.com/releases/v5.12.1/css/all.css"

cache = dict()
cache['escuelas'] = json.load(open("DatosEscuelas.json"))
print("Número total de escuelas", len(cache['escuelas']))

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets = [dbc.themes.BOOTSTRAP, FONT_AWESOME])
server = app.server
