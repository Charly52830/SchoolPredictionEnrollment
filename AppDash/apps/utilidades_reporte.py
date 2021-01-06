# -*- coding: utf-8 -*-
from datetime import date
import numpy as np

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from collections import OrderedDict
from statsmodels.tsa.stattools import acf, pacf

from app import app

MAPBOX_TOKEN = open(".mapbox_token").read()

TEXTO_TOOLTIP = {
    "PAG" : u"Promedio del número de alumnos por grupo que la escuela ha tenido en todos los años",
    "MAE" : u"Otorga el error absoluto promedio en la misma escala en la que se encuentran los datos",
    "RMSE" : u"Evalúa la precisión de la proyección en la misma escala en la que se encuentran los datos, pero es más sensible que MAE ante errores grandes",
    "MAPE" : u"Promedio del porcentaje de error para conocer la precisión de la proyección en una escala general",
    "PR" : u"Probabilidad de tomar una mala decisión basada en los resultados que arroja la proyección"
}

def ordenar_escuelas(escuelas) :
    """
    Ordena las escuelas por su promedio de alumnos y devuelve un diccionario
    ordenado de las escuelas.
    
    Args:
        escuelas (dict): diccionario que contiene las escuelas.
        
    Returns:
        escuelas_ordenadas (:obj: `OrderedDict`): devuelve el mismo diccionario 
            que se recibe pero con las escuelas ordenadas en orden por su promedio
            de alumnos.
    """
    escuelas_ordenadas = OrderedDict()
    CCTS_ordenados = [(np.array(escuelas[cct]["matricula"]).mean(), cct) for cct in escuelas]
    CCTS_ordenados.sort()
    
    for _, cct in CCTS_ordenados :
        escuelas_ordenadas[cct] = escuelas[cct]
    
    return escuelas_ordenadas

class GeneradorDeGraficas :
    
    def generar_scatterplot(escuelas, show_legend = True, title = u"Proyección de matrícula") :
        """
        Función para generar una gráfica que contiene los Scatterplot de las 
        distintas escuelas.
        
        Args:
            escuelas (:obj: `OrderedDict`): diccionario ordenado con los datos de
                todas las escuelas que se quieren agregar al scatterplot.
            show_legend (bool, opcional): controla si se mostrará o no la leyenda en la gráfica.
            title (str, opcional): título a mostrar en la gráfica.
        
        Returns:
            scatterplot (:obj: `plotly.graph_objs.Figure`): figura con los Scatterplot
                lista para ser utilizada por un objeto dcc.Graph.
        """
        def add_trace(fig, cct, data, seed_year = 1998) :
            """
            Agrega un nuevo scatterplot a la gráfica.
            
            Args:
                fig (:obj: `plotly.graph_objs.Figure`): figura a la cual agregar
                    el nuevo scatterplot.
                cct (str): cct de la escuela a agregar.
                data (list): datos de la escuela a agregar.
                seed_year (int, opcional): primer año en el que se tiene registro de los
                    datos de la escuela.
            """
            scatter = go.Scatter(
                x = ["%d-08-01" % (seed_year + i) for i in range(len(data))],
                y = [str(i) for i in data],
                name = cct,
                text = [str(i) for i in data],
                yaxis="y",
                mode = 'lines+markers',
            )
            fig.add_trace(scatter)

        # Create figure
        scatterplot = go.Figure()

        # Add traces
        for cct in escuelas :
            matricula = escuelas[cct]['matricula'] + escuelas[cct]['pred']
            
            # Agregar matricula
            add_trace(
                fig = scatterplot,
                cct = cct,
                data = matricula,
                seed_year = escuelas[cct]['primer_anio']
            )

        # Add shapes
        scatterplot.update_layout(
            shapes = [
                dict(
                    fillcolor="rgba(77, 213, 0, 0.2)",
                    line={"width": 0},
                    type="rect",
                    x0="2020-01-01",
                    x1="2021-01-01",
                    xref="x",
                    y0=0,
                    y1=1.0,
                    yref="paper"
                ),
                dict(
                    fillcolor="rgba(144, 217, 0, 0.3)",
                    line={"width": 0},
                    type="rect",
                    x0="2021-01-01",
                    x1="2022-01-01",
                    xref="x",
                    y0=0,
                    y1=1.0,
                    yref="paper"
                ),
                dict(
                    fillcolor="rgba(213, 221, 0, 0.3)",
                    line={"width": 0},
                    type="rect",
                    x0="2022-01-01",
                    x1="2023-01-01",
                    xref="x",
                    y0=0,
                    y1=1.0,
                    yref="paper"
                ),
                dict(
                    fillcolor="rgba(225, 165, 0, 0.3)",
                    line={"width": 0},
                    type="rect",
                    x0="2023-01-01",
                    x1="2024-01-01",
                    xref="x",
                    y0=0,
                    y1=1.0,
                    yref="paper"
                ),
                dict(
                    fillcolor="rgba(229, 99, 0, 0.3)",
                    line={"width": 0},
                    type="rect",
                    x0="2024-01-01",
                    x1="2025-01-01",
                    xref="x",
                    y0=0,
                    y1=1.0,
                    yref="paper"
                ),
            ]
        )

        # Style all the traces
        scatterplot.update_traces(
            hoverinfo = "name+x+text",
            showlegend = show_legend
        )

        # Update axes
        scatterplot.update_layout(
            xaxis = dict(
	            autorange = True,
	            range = ["1998-08-01", "2025-08-01"],
	            rangeslider = dict(
		            autorange = True,
		            range = ["1998-08-01", "2025-08-01"]
	            ),
	            type = "date",
            ),
            title = title,
            title_font = dict(size = 20),	# Tamaño del titulo
            title_x = 0.5,	# Centrar el titulo
        )

        scatterplot.update_xaxes(
            title_text = u"Ciclo escolar",
            title_font = {"size": 20}
        )

        scatterplot.update_yaxes(
            title_text = u"Alumnos",
            title_font = {"size": 20}
        )

        # Update layout
        scatterplot.update_layout(
            dragmode="zoom",
            hovermode="x",
            template="plotly_white",
            margin=dict(b = 50),
        )

        return scatterplot

    def generar_boxplot(escuelas, show_legend = True, title = u'Box plot de la matrícula escolar') :
        """
        Función para generar una gráfica que contiene los Boxplot generados con
        la matrícula histórica de todas las escuelas.
        
        Args:
            escuelas (:obj: `OrderedDict`): diccionario ordenado con los datos de
                todas las escuelas que se quieren agregar a la gráfica.
            show_legend (bool, opcional): controla si se mostrará o no la leyenda en la gráfica.
            title (str, opcional): título a mostrar en la gráfica.
        
        Returns:
            boxplot (:obj: `plotly.graph_objs.Figure`): figura con los Boxplot
                lista para ser utilizada por un objeto dcc.Graph.
        """
        # Create figure
        boxplot = go.Figure()
        
        # Add traces
        for cct in escuelas :
            matricula = escuelas[cct]['matricula']
            
            boxplot.add_trace(go.Box(
                y = matricula,
                name = cct,
            ))
        
        # Style all the traces
        boxplot.update_traces(showlegend = show_legend)
        
        # Update axes
        boxplot.update_xaxes(
	        title_text = "Escuelas",
	        title_font = {"size": 20}
        )

        boxplot.update_yaxes(
	        title_text = "Alumnos",
	        title_font = {"size": 20}
        )
        
        # Update layout
        boxplot.update_layout(
            dragmode = "zoom",
            hovermode = "x",
            template = "plotly_white",
        )
        
        boxplot.update_layout(
	        title = title,
	        title_font = dict(size = 20),	# Tamaño del titulo
	        title_x = 0.5,	# Centrar el titulo
        )
        
        return boxplot

    def generar_tabla_metricas(escuelas, links_requeridos = True) :
        """
        Función para generar la tabla de métricas.
        
        Args:
            escuelas (:obj: `OrderedDict`): diccionario ordenado con los datos de
                todas las escuelas que se quieren agregar a la tabla.
            links_requeridos (bool, opcional): si es True las ccts tendrán un link que
                lleve al reporte individual de las escuelas, si es False entonces
                la cct solo será texto plano.
                
        Returns:
            objeto con el layout de la tabla.
        """
        
        # Colores a utilizar en las métricas por cada escuela de
        colores_metricas = [
            "#4DD500",
            "#90D900",
            "#D5DD00",
            "#E1A500",
            "#E56300",
        ]
        
        def color_por_alumnos_promedio(error, PAG) :
            """
            Devuelve uno de los colores de la paleta dependiendo de qué tal bajo
            sea el error con respecto al PAG.
            
            El PAG se divide entre 4 y se busca el color que le corresponde.
            
            Args:
                error (float): error de la escuela a comparar con el PAG, específicamente,
                    debe de ser MAE o RMSE.
                PAG (float): promedio de alumnos por grupo para compararse con el
                    error.
            
            Returns:
                color (str): color que le corresponde al error.
            
            """
            x = PAG / 4
            for i in range(1, 4) :
                if error < i * x :
                    return colores_metricas[i - 1]

            return colores_metricas[-1]

        def color_por_porcentage(error) :
            """
            Devuelve uno de los colores de la paleta dependiendo de que tan bajo
            sea el error con respecto a la escala de 1 a 0.
            
            Todos los errores superiores a 0.5 son rojos, el resto de los colores
            se decide encontrando el color correspondiente entre 0.125, 0.25, 0.375
            y 0.5.
            
            Args:
                error (float): error de la escuela, específicamente debe ser MAPE
                    o PR.
            
            Returns:
                color (str): color que le corresponde al error.
            """
            for i in range(1, 4) :
                if error < i * 0.125 :
                    return colores_metricas[i - 1]
            return colores_metricas[-1]
        
        def generar_layout_cabecera(titulo, campo, margin_left) :
            """
            Genera el layout que contiene el tooltip del encabezado, así como
            la cabecera de la columnad de la tabla que le corresponde al campo.
            
            Args:
                titulo (str): título que lleva el tooltip al mostrarse en pantalla.
                campo (str): campo de la columna
                margin_left (str): margen izquierdo del tooltip.
            
            Returns:
                layout del encabezado de una columna
            
            """
            layout = html.Th(
                html.Div([
                    html.Span([
                        titulo,
                        html.Img(
                            src = app.get_asset_url('%s.svg' % (campo.lower())),
                            style = {"margin-bottom" : "5px"}
                        ),
                        html.Div(
                            TEXTO_TOOLTIP[campo],
                            className = "texto-tooltip",
                        )],
                        className = "contenido-tooltip",
                        style = {"margin-left" : margin_left}
                    ),
                    campo],
                    className = "mi-tooltip",
                )
            )
            
            return layout
        
        encabezados = [
            (u"Promedio de Alumnos por Grupo", "PAG", "-8rem"),
            (u"Mean Absolute Error", "MAE", "-10rem"),
            (u"Root Mean Squared Error", "RMSE", "-11rem"),
            (u"Mean Absolute Percentage Error", "MAPE", "-16rem"),
            (u"Probabilidad de Riesgo", "PR", "-19rem")
        ]
        
        # Cabecera de la tabla
        cabecera = html.Thead(html.Tr([
            html.Th("cct")] +
            [generar_layout_cabecera(*encabezado) for encabezado in encabezados]
        ))
        
        # Cuerpo de la tabla
        cuerpo = html.Tbody([
            html.Tr([
                # Layout del CCT
                html.Td(html.A(cct, href = "reporte/%s" % (cct), id = "link-escuela") if links_requeridos else cct),
                # Layout del PAG
                html.Td("%.2lf" % (escuelas[cct]["PAG"])),
                # Layout de MAE
                html.Td(
                    escuelas[cct]["mae"],
                    style = {
                        "color" : color_por_alumnos_promedio(
                            error = escuelas[cct]["mae"],
                            PAG = escuelas[cct]["PAG"],
                        ),
                    }
                ),
                # Layout de rmse
                html.Td(
                    escuelas[cct]["rmse"],
                    style = {
                        "color" : color_por_alumnos_promedio(
                            error = escuelas[cct]["rmse"],
                            PAG = escuelas[cct]["PAG"]
                        ),
                    }
                ),
                # Layout de MAPE
                html.Td(
                    escuelas[cct]["mape"],
                    style = {
                        "color" : color_por_porcentage(
                            error = escuelas[cct]["mape"]
                        ),
                    }
                ),
                # Layout de PR
                html.Td(
                    escuelas[cct]["rp"],
                    style = {
                        "color" : color_por_porcentage(
                            error = escuelas[cct]["rp"]
                        ),
                    }
                )]
            )
            for cct in escuelas]
        )
        
        # Tabla completa
        tabla = dbc.Table([
            cabecera,
            cuerpo],
            # Estilos del layout general de la tabla.
            style = {
                "font-size" : "0.86875rem",
                "text-align" : "center",
            },
            className = "tabla-metricas"
        )
        
        return tabla

    def generar_tabla_matricula(escuelas, links_requeridos = True) :
        """
        Función para generar la tabla de matrícula. Alínea adecuadamente los
        datos de la matrícula en caso de que una escuela no cuente con suficientes
        datos.
        
        Args:
            escuelas (:obj: `OrderedDict`): diccionario ordenado con los datos de
                todas las escuelas que se quieren agregar a la tabla.
            links_requeridos (bool, opcional): si es True las ccts tendrán un link que
                lleve al reporte individual de las escuelas, si es False entonces
                la cct solo será texto plano.
                
        Returns:
            objeto con el layout de la tabla.
        """
        # Cabecera de la tabla
        anio_actual = date.today().year
        nombre_columnas = ["cct"] + ["%d\n%d" % (anio, anio + 1) for anio in range(anio_actual - 5, anio_actual + 5)]
        cabecera = html.Thead(
            html.Tr([
                html.Th(
                    nombre_col,
                    style = {"padding-left" : "0"}
                ) for nombre_col in nombre_columnas]
            )
        )
        
        # Cuerpo de la tabla
        cuerpo = html.Tbody([
            html.Tr(
                # cct
                [html.Td(
                    html.A(cct, href = "reporte/%s" % (cct), id = "link-escuela") if links_requeridos else cct,
                    style = {"padding-left" : "0"}
                )] + 
                # Últimos 4 años
                [html.Td(
                    escuelas[cct]["matricula"][-(5 - i)] if len(escuelas[cct]["matricula"]) >= 5 - i else '',
                    style = {"padding-left" : "0"}
                ) for i in range(4)] + 
                # Último año de color rojo
                [html.Td(
                    escuelas[cct]["matricula"][-1],
                    style = {
                        "padding-left" : "0",
                        "color" : "#FF0055"
                    }
                )] + 
                # Predicción
                [html.Td(
                    pred,
                    style = {"padding-left" : "0"}
                ) for pred in escuelas[cct]["pred"]]
            )
        for cct in escuelas])
        
        # Tabla
        tabla = dbc.Table([
            cabecera,
            cuerpo],
            className = "table-responsive",
            style = {
                "font-size" : "small",
                "text-align" : "center"
            }
        )
        return tabla

    def generar_correlograma(escuela, cct, es_acf = True) :
        """
        Función para generar una gráfica que contiene el correlograma de los datos
        de matrícula de una escuela.
        
        Args:
            escuelas (:obj: `OrderedDict`): diccionario ordenado con los datos de
                todas las escuelas que se quieren agregar al scatterplot.
            cct (str): clave de la escuela de la que se quiere obtener el
                correlograma.
            es_acf (bool, opcional): si es True, el correlograma graficará la
                función de autocorrelación (ACF), si no, la función de 
                autocorrelación parcial (PACF).
        
        Returns:
            correlograma (:obj: `plotly.graph_objs.Figure`): figura con el correlograma
                listo para ser utilizado por un objeto dcc.Graph.
        """
        # Calcular la autocorrelación al vuelo
        if es_acf :
            title = "ACF de %s" % (cct)
            if len(escuela) == 1 :
                correlacion = np.array([1])
            else :
                correlacion = np.array(acf(escuela, nlags = len(escuela) - 1))
        else :
            title = "PACF de %s" % (cct)
            if len(escuela) == 1 :
                correlacion = np.array([1])
            else :
                correlacion = np.array(pacf(escuela, nlags = len(escuela) - 1))
        
        # Create figure
        correlograma = go.Figure(data=[go.Bar(y=correlacion)])
        
        # Update axes
        correlograma.update_layout(
	        xaxis = dict(
		        autorange = True,
		        rangeslider = dict(
			        autorange = True,
			        range = [0, len(escuela)]
		        ),
	        ),
	        title = title,
	        title_font = dict(size = 20),	# Tamaño del titulo
	        title_x = 0.5,	# Centrar el titulo
        )
        
        correlograma.update_xaxes(
	        title_text = "Lag",
	        title_font = {"size": 20}
        )

        correlograma.update_yaxes(
	        title_text = "ACF" if es_acf else "PACF",
	        title_font = {"size": 20}
        )
        
        # Update layout
        correlograma.update_layout(
            hovermode = "x",
            template = "plotly_white",
        )
        
        return correlograma

    def generar_mapa(escuelas, titulo = u"Ubicación de las escuelas") :
        """
        Función para generar una gráfica que contiene el mapa con las ubicaciones
        de las escuelas.
        
        Args:
            escuelas (:obj: `OrderedDict`): diccionario ordenado con los datos de
                todas las escuelas que se quieren agregar al scatterplot.
            titulo (str, opcional): título a mostrar en la gráfica.
        
        Returns:
            correlograma (:obj: `plotly.graph_objs.Figure`): figura con el mapa
                listo para ser utilizado por un objeto dcc.Graph.
        """
        
        # Separar las ccts por nivel
        escuelas_por_nivel = {
            "Preescolar" : [],
            "Primaria" : [],
            "Secundaria" : []
        }
        for cct in escuelas :
            escuelas_por_nivel[escuelas[cct]["nivel"]].append(cct)
        
        # Create figure
        mapa = go.Figure()
        tamanio_circulos = 8 + 0.07 * (101 - min(100, len(escuelas)))
        
        # Add traces
        if escuelas_por_nivel['Preescolar'] :
            mapa.add_trace(go.Scattermapbox(
                lat = [escuelas[cct]["lat"] for cct in escuelas_por_nivel["Preescolar"]],
                lon = [escuelas[cct]["lng"] for cct in escuelas_por_nivel["Preescolar"]],
                name = "Preescolares",
                mode = 'markers',
                marker = go.scattermapbox.Marker(size = tamanio_circulos),
                text = ["%s (%d alumnos)" % (cct, escuelas[cct]["matricula"][-1]) for cct in escuelas_por_nivel["Preescolar"]]
            ))
        
        if escuelas_por_nivel['Primaria'] :
            mapa.add_trace(go.Scattermapbox(
                lat = [escuelas[cct]["lat"] for cct in escuelas_por_nivel["Primaria"]],
                lon = [escuelas[cct]["lng"] for cct in escuelas_por_nivel["Primaria"]],
                name = "Primarias",
                mode = 'markers',
                marker = go.scattermapbox.Marker(size = tamanio_circulos),
                text = ["%s (%d alumnos)" % (cct, escuelas[cct]["matricula"][-1]) for cct in escuelas_por_nivel["Primaria"]]
            ))
        
        if escuelas_por_nivel['Secundaria'] :
            mapa.add_trace(go.Scattermapbox(
                lat = [escuelas[cct]["lat"] for cct in escuelas_por_nivel["Secundaria"]],
                lon = [escuelas[cct]["lng"] for cct in escuelas_por_nivel["Secundaria"]],
                name = "Secundarias",
                mode = 'markers',
                marker = go.scattermapbox.Marker(size = tamanio_circulos),
                text = ["%s (%d alumnos)" % (cct, escuelas[cct]["matricula"][-1]) for cct in escuelas_por_nivel["Secundaria"]]
            ))
        
        # Update layout
        mapa.update_layout(
            mapbox_accesstoken = MAPBOX_TOKEN,
            mapbox_style = "light",
            mapbox = {
                # Centro de Zacatecas
                'center': go.layout.mapbox.Center(lat = 23.1719, lon = -102.861),
                'zoom': 5.65
            },
            title = titulo,
	        title_font = dict(size = 20),	# Tamaño del titulo
	        title_x = 0.5,	# Centrar el titulo,
	        margin=dict(b = 15),
        )
        
        return mapa
