# Manejo de módulos
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import numpy as np
from Metodos.IndividualANN import individual_ann
from Metodos.FuzzyTimeSeries import hyperopt_fts_predict
from Metodos.AutoARIMA import auto_arima_predict
from Entrenamiento.Normalizators import MinMaxNormalizator

def weightless_ep(data, prediction_size, experts = []) :
	"""Función de predicción que toma la opinión de distintos métodos de
	predicción. Considera que todos los métodos tienen el mismo peso, por lo que
	la predicción final es el promedio de todos los métodos en cada año.
	
	Args :
		data (:obj: `numpy.array`): numpy array de una dimensión que contiene
			los datos de entrenamiento de la serie de tiempo.
		prediction_size (int): número de años a predecir.
		experts(list): lista de tuplas. Cada tupla contiene una función de un
		método de predicción y sus respectivos parámetros especiales en un
		diccionario.
	
	Returns:
		(:obj: `numpy.array`): arreglo numpy con los datos de la predicción 
			con forma (prediction__size,)
	"""
	global_prediction = np.zeros((prediction_size))
	
	for expert, args in experts :
		args['data'] = data
		args['prediction_size'] = prediction_size
		global_prediction += expert(**args)
		
	return global_prediction / len(experts)

if __name__ == '__main__' :
	escuela = np.array([377,388,392,394,408,405,426,403,414,412,424,438,452,443,429,430,428])
	prediction = weightless_ep(
		data = escuela,
		prediction_size = 5,
		experts = [
			(individual_ann, dict(window_len = 5, normalizators = [MinMaxNormalizator])), 
			(hyperopt_fts_predict, dict()), 
			(auto_arima_predict, dict(normalizators = [MinMaxNormalizator]))
		]
	)
	print(prediction)
