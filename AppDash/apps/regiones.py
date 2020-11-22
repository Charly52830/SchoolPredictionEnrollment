import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from app import app

layout = html.Div([
    html.H3('Regiones'),
    dcc.Link('Regresar', href='/'),
    html.Br(),
    dcc.Link('Reporte', href='/apps/reporte'),
])
