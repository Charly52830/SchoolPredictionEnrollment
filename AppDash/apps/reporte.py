import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from app import app

botones_sidebar = dbc.Col(
    [
        dbc.Button([html.I(className="fas fa-arrow-left")], id = 'next_button', style = {"margin-top" : "1rem"}),
        html.Br(),
        dbc.Button([html.I(className="fas fa-arrow-right")], id = 'previous_button', style = {"margin-top" : "1rem"}),
        html.Br(),
        dbc.Button([html.I(className="fas fa-share-alt")], id = 'share_button', style = {"margin-top" : "1rem"}),
        html.Br(),
        dbc.Button([html.I(className="fas fa-file-pdf")], id = 'pdf_button', style = {"margin-top" : "1rem"}),
        html.Br(),
        dbc.Button([html.I(className="fas fa-file-excel")], id = 'excel_button', style = {"margin-top" : "1rem"}),
        html.Br(),
        dbc.Button([html.I(className="fas fa-question-circle")], id = 'help_button', style = {"margin-top" : "1rem"}),
    ],
)

sidebar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(dbc.Button([html.I(className="fas fa-home")], id = 'home_button')),
                ],
                align="center",
                no_gutters=True,
            ),
            href="/",
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(botones_sidebar, id="navbar-collapse", navbar=True),
    ],
    color="#e6e6e6",
    style = {
        "position" : "fixed",
        "top" : 0,
        "left" : 0,
        "bottom" : 0,
        "width" : "5rem",
        "padding-top" : "1rem",
    },
    className = "nav flex-column",
)

# add callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

layout = html.Div([
    # Content
    html.Div(
        [
            # Navbar
            dbc.Navbar(
                [
                    dbc.Row(
                        dbc.Col(dbc.Input(type="text", placeholder="Reporte sin titulo", style = {"text-align":"center"} )),
                        no_gutters=True,
                        className="d-flex justify-content-center",
                        align="center",
                    ),
                    dbc.Row(
                        dbc.Col("01/01/2021", style = {"font-size" : "small", "color" : "#5a6268", "margin-top" : "3px"}),
                        no_gutters=True,
                        className="d-flex justify-content-center",
                        align="center",
                    ),
                ],
                className = "d-flex justify-content-center flex-column",
                style = {
                    "border-style" : "solid none solid none", 
                    "border-width" : "thin", 
                    "border-color" : "#e6e6e6", 
                    "padding-top" : "5px",
                    "padding-bottom" : "3px",
                }
            ),
        ],
        style = {"margin-left" : "5rem"},
    ),
    # Sidebar
    sidebar,
])
