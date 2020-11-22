import dash
import dash_bootstrap_components as dbc

# Hojas de estilo
FONT_AWESOME = "https://use.fontawesome.com/releases/v5.12.1/css/all.css"


app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets = [dbc.themes.BOOTSTRAP, FONT_AWESOME])
server = app.server
