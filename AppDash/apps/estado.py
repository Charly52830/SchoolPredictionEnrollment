# -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from app import app

layout = html.Div([
    html.H3('Estado'),
    dcc.Link('Regresar', href='/'),
])
