import pandas as pd
import numpy as np
import bqplot.pyplot as plt
import tensorflow as tf
from IPython.display import display, HTML, IFrame
import ipywidgets as widgets
import altair as alt
import datapane as dp

from bqplot import (ColorScale, DateColorScale, OrdinalColorScale, 
                    LinearScale, Tooltip)
from ipywidgets import interact, interactive, fixed, interact_manual

def LoadReport(title, X, Y, prediccion, anios) :
    anios_ = [1998 + i for i in range(len(X))]
    n1 = len(anios_)
    anios_ += [1997 + len(X) + i  for i in range(len(Y) + 1)]
    n2 = len(anios_) - n1
    anios_ += [1997 + len(X) + i  for i in range(len(Y) + 1)]
    n3 = len(anios_) - n2 - n1
    
    series = ['Datos de entrenamiento'] * n1
    series += ['Datos de prueba'] * n2
    series += ['Datos predecidos'] * n3
    
    alumnos = list(X)
    alumnos += (list(X) + list(Y))[-(anios + 1):]
    alumnos += (list(X) + list(prediccion))[-(anios + 1):]
    
    df = pd.DataFrame(data = {
        'Serie' : series,
        'Año' : anios_,
        'Alumnos' : alumnos
    })
    
    columns = ['Año %d' % (i) for i in range(1, anios + 1)]
    columns += ['MAPE', 'MAE', 'RMSE']
    
    metricas = np.zeros(3)
    
     # MAPE
    metricas[0] = np.abs((prediccion - Y) / Y).mean()
    
    # MAE
    metricas[1] = np.abs(prediccion - Y).mean()
    
    # RMSE
    metricas[2] = np.sqrt(np.square(prediccion - Y).mean())
    
    metricas = pd.DataFrame(
        np.array([list(prediccion) + list(metricas)]),
        columns = columns
    )
    
    # Crear grafica
    chart = alt.Chart(df).mark_line().encode(
        x = 'Año',
        y = 'Alumnos',
        color = 'Serie'
    ).mark_line(point = True).interactive().properties(
        title = title
    )
    
    # Crear reporte
    reporte = dp.Report(dp.Table(metricas), dp.Plot(chart))
    
    return reporte
    
def LoadScatterPlotEvaluation(Y, Y_hat, prediction_size) :
    n = int(Y.shape[0] / prediction_size)
    colors = []
    if prediction_size >= 1:
        colors.append(1)
    if prediction_size >= 2:
        colors.append(2)
    if prediction_size >= 3:
        colors.append(3)
    if prediction_size >= 4:
        colors.append(4)
    if prediction_size >= 5:
        colors.append(5)

    colors = np.array(colors * n)
    
    axes_options = {
        'x': dict(label='Valor real (alumnos)'),
        'y': dict(label='Valor predecido (alumnos)'),
        'color': dict(label='Año', side='right')
    }

    scatter2 = plt.scatter(
        Y,
        Y_hat,
        color=colors,
        stroke='black',
        axes_options=axes_options
    )

def LoadEvaluationPlot(result, prediction_size, conjunto, modelo) :
    n = int(result.Y.shape[0] / prediction_size)
    m = max(np.amax(result.Y_hat), np.amax(result.Y))

    colors = []
    if prediction_size >= 1:
        colors.append(1)
    if prediction_size >= 2:
        colors.append(2)
    if prediction_size >= 3:
        colors.append(3)
    if prediction_size >= 4:
        colors.append(4)
    if prediction_size >= 5:
        colors.append(5)

    colors = np.array(colors * n)

    fig = plt.figure(
        title = 'Predicción de matrícula escolar en %s utilizando %s' % (conjunto, modelo), 
        legend_location = 'top-left', 
        fig_margin = dict(top = 50, bottom = 70, left = 100, right = 100)
    )

    plt.scales(scales={'color': OrdinalColorScale(colors=['Green', 'DodgerBlue', 'Yellow', 'Orange', 'Red'])})

    axes_options = {
        'x': dict(label='Valor real (alumnos)'),
        'y': dict(label='Valor predecido (alumnos)'),
        'color': dict(label='Año', side='right')
    }

    scatter2 = plt.scatter(
        result.Y,
        result.Y_hat,
        color=colors,
        stroke='black',
        axes_options=axes_options
    )

    #LoadScatterPlotEvaluation(result.Y, result.Y_hat, prediction_size)

    plt.plot(
        x = np.array([0, m]), 
        y = np.array([0, m]), 
        labels = ['Línea base de predicción'], 
        display_legend = True
    )

def LoadHTMLTable(metricas, modelo) :
	
	def load_header(anios) :
		header = ''
		for i in range(anios) :
			header += '<th colspan="3" style="text-align:center"> Año %s </th>\n' % (i + 1)
		return header
	
	def load_metrics_row(anios) :
		return '<td colspan="3" style="text-align:center">Métricas</td>\n' * anios
	
	def load_individual_metrics(anios) :
		return """
			<td>MAE</td>
			<td>RMSE</td>
			<td>MAPE</td>
		""" * anios
	def load_table_data(metricas, modelo) :
		row = '<td> %s </td>' % (modelo)
		for metrica in metricas :
			row += """
				<td> %.3f </td>
				<td> %.3f </td>
				<td> %.3f </td>
			""" % (metrica[0], metrica[1], metrica[2])
		return row
	
	anios = len(metricas)
	table = """
		<table>
			<tr>
				<th rowspan='3' style="text-align:center">
					Modelo
				</th>
				%s
			</tr>
			<tr>
				%s
			</tr>
			<tr>
				%s
			</tr>
			<tr>
				%s
			</tr>
		</table>
	""" % (load_header(anios), load_metrics_row(anios), load_individual_metrics(anios), load_table_data(metricas, modelo))
	
	return table
		
		
		
