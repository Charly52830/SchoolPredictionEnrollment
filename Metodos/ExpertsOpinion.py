# Manejo de módulos
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import numpy as np
from Metodos.IndividualANN import individual_ann, evaluate_and_predict_ann
from Metodos.FuzzyTimeSeries import hyperopt_fts_predict, evaluate_and_predict_fts
from Metodos.AutoARIMA import auto_arima_predict, evaluate_and_predict_arima
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

def evaluate_and_predict_ep(data, prediction_size = 5, 
	experts = [evaluate_and_predict_ann, evaluate_and_predict_arima, evaluate_and_predict_fts]) :
	"""
	"""
	assert(len(data) > 5)
	global_prediction = np.zeros((prediction_size))
	global_train_prediction = np.zeros((len(data) - 5))
	
	for expert in experts :
		args = dict()
		args['data'] = data
		args['prediction_size'] = prediction_size
		prediction, train_prediction = expert(**args)
		print(prediction)
		global_prediction += prediction
		global_train_prediction += train_prediction
	
	return global_prediction / len(experts), global_train_prediction / len(experts)
	

if __name__ == '__main__' :
	escuela = np.array([388,370,388,383,376,359,354,337,325,373,367,380,401,398,392,343,324,318,320,332,351,378])
	prediction, train_prediction = evaluate_and_predict_ep(
		data = escuela,
	)
	print(prediction, train_prediction)
