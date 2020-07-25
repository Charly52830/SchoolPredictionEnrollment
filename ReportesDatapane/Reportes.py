# Manejo de módulos
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import altair as alt
import datapane as dp
import pandas as pd
import numpy as np
from Metodos.DNN import load_model, dnn_predict, dnn_predict_by_year
from Metodos.TimeSeriesPrediction import fixed_partitioning_predict
from Metodos.LinearRegression import linear_regression_predict, base_linear_regression, linear_regression

# Nota importante (25/07/2020)
# Este archivo contiene funciones cuyo propósito es facilitar la generación de
# reportes de Datapane en un ambiente de producción no profesional (utilizando
# modelos de producción y no de evaluación, pero sin estar integrados a ningún
# sistema).

def PublicarReporte(lista_proyecciones, nombre_reporte, num_datos) :
    """Publica un reporte en datapane. El reporte contendrá una tabla con los
    resultados de múltiples proyecciones, así como una gráfica por cada proyección.
    
    Se debe contar con una llave de Datapane para poder publicar un reporte, la
    cual se puede obtener en: https://datapane.com/home/
    
    Antes de ejecutar esta función se debe iniciar una sesión ejecutando el
    siguiente comando:
    
    $ datapane login --server=https://datapane.com/ --token=TOKEN
    
    sustituyendo el valor del token con la llave de Datapane.
    
    Args:
    	lista_proyecciones (list): lista de tuplas, las tuplas contienen los objetos
    		(numpy.array, datapane.Plot) que son los resultados de una proyección
    		así como los datos históricos, y una gráfica de Altair en un objeto
    		de Datapane respectivamente. Una tupla de estas es generada por la
    		función PrepararProyección.
    	nombre_reporte (str): nombre del reporte de Datapane.
    	num_datos (int): número de datos históricos + número de datos predecidos.
    """
	# Crear tabla
	columnas = ["cct"] + ["%02d-%02d" % ((98 + i) % 100, (99 + i) % 100) for i in range(27)]
	
	n = len(lista_proyecciones)
	m = len(columnas)
	lista_graficas = []
	lista_renglones = []
	
	for i in range(n) :
		row = lista_proyecciones[i][0]
		grafica = lista_proyecciones[i][1]
		lista_renglones.append(row)
		lista_graficas.append(grafica)
	
	datos = np.array(lista_renglones)	
	tabla = pd.DataFrame(
		datos,
		columns = columnas
	)
	lista = [dp.Table(tabla)] + lista_graficas
	
	# Crear reporte y publicarlo
	reporte = dp.Report(*lista)
	
	print("Reporte terminado")
	reporte.publish(name = nombre_reporte, open = True, visibility = 'PUBLIC')

def PrepararProyeccion(data, prediction_size, title, cct, metodo, args = dict()) :
	"""Genera una proyección, y la prepara para ser publicada en un reporte de Datapane.
	
	Args:
		data (:obj: `numpy.array`): numpy array con los datos históricos de la
			observación.
		prediction_size (int): número de años a predecir.
		title (str): titulo de la gráfica.
		cct (str): clave del centro de trabajo de la escuela.
		metodo (function): método de predicción a utilizar. Las funciones se
			encuentran en el directorio Metodos.
		args (:obj: `dict`): diccionario con los parámetros especiales que pueda
			requerir el método de predicción.
	
	Returns:
		(:obj: `numpy.array`): numpy array con los datos históricos y predecidos
			de la observación.
		(:obj: `datapane.Plot`): objeto con la gráfica de la predicción.
	"""
	# Realizar predicción
	args['prediction_size'] = prediction_size
	args['data'] = data
	prediccion = metodo(**args)
	
	# Preparar lineas de la gráfica
	alumnos = list(data)
	anios = [1998 + i for i in range(len(data))]
	
	alumnos.append(data[-1])
	anios.append(anios[-1])
	
	alumnos += list(prediccion)
	last_year = anios[-1] + 1
	anios += [last_year + i for i in range(prediction_size)]
	
	series = ['Datos reales'] * len(data) + ['Datos predecidos'] * (prediction_size + 1)
	
	df = pd.DataFrame(data = {
		'Serie' : series,
		'Año' : anios,
		'Alumnos' : alumnos
	})
	
	# Crear grafica
	chart = alt.Chart(df).mark_line().encode(
		x = 'Año',
		y = 'Alumnos',
		color = 'Serie'
	).mark_line(point = True).interactive().properties(
		title = title
	)
	
	row = np.array([cct] + list(data) + list(prediccion))
	
	return (row, dp.Plot(chart))

if __name__ == '__main__':
	proyecciones = []
	
	proyecciones.append(PrepararProyeccion(
		data = np.array([61,61,63,77,69,84,88,74,96,93,75,82,77,88,93,91,95,88,89,98,90,87]),
		prediction_size = 5,
		title = "Proyección de matrícula de 32DJN0243V utilizando Fix. part. linear regression",
		cct = "32DJN0243V",
		metodo = base_linear_regression,
		args = dict(window_len = 8)
	))
	proyecciones.append(PrepararProyeccion(
		data = np.array([40,51,56,35,44,48,63,84,64,73,79,80,78,86,78,88,84,88,73,76,79,86]),
		prediction_size = 5,
		title = "Proyección de matrícula de 32DJN0254A utilizando Fix. part. linear regression",
		cct = "32DJN0254A",
		metodo = base_linear_regression,
		args = dict(window_len = 8)
	))
	proyecciones.append(PrepararProyeccion(
		data = np.array([199,181,171,176,166,157,154,162,193,179,204,223,241,257,244,260,242,245,237,223,229,220]),
		prediction_size = 5,
		title = "Proyección de matrícula de 32DPR0475B utilizando Redes neuronales",
		cct = "32DPR0475B",
		metodo = base_linear_regression,
		args = dict(window_len = 8)
	))
	proyecciones.append(PrepararProyeccion(
		data = np.array([175,179,181,183,188,192,180,200,209,207,215,239,239,239,241,241,218,215,208,213,213,231]),
		prediction_size = 5,
		title = "Proyección de matrícula de 32DPR0477Z utilizando Redes neuronales",
		cct = "32DPR0477Z",
		metodo = base_linear_regression,
		args = dict(window_len = 8)
	))
	proyecciones.append(PrepararProyeccion(
		data = np.array([40,46,34,40,49,52,43,45,48,55,73,66,69,62,79,85,87,94,98,85,71,80]),
		prediction_size = 5,
		title = "Proyección de matrícula de 32ETV0109D utilizando Fix. part. linear regression",
		cct = "32ETV0109D",
		metodo = base_linear_regression,
		args = dict(window_len = 8)
	))
	proyecciones.append(PrepararProyeccion(
		data = np.array([56,53,52,56,64,69,58,60,50,55,52,56,58,67,86,87,113,123,111,98,110,100]),
		prediction_size = 5,
		title = "Proyección de matrícula de 32ETV0248E utilizando Fix. part. linear regression",
		cct = "32ETV0248E",
		metodo = base_linear_regression,
		args = dict(window_len = 8)
	))
	PublicarReporte(proyecciones, 'ReporteEjidalRegresionLineal', 27)
