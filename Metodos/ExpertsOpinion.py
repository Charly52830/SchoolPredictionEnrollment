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

def weightless_ep(data, prediction_size, experts = [], args = []) :
	assert(len(experts) == len(args))
	#predictions = np.zeros((len(experts), prediction_size))
	global_prediction = np.zeros(prediction_size)
	for i in range(len(experts)) :
		args[i]['data'] = data
		args[i]['prediction_size'] = prediction_size
		prediction = experts[i](**args[i])
		global_prediction += prediction
	
	global_prediction /= len(experts)
	return global_prediction

if __name__ == '__main__' :
	escuela = np.array([377,388,392,394,408,405,426,403,414,412,424,438,429,443,429,430,428])
	prediction = weightless_ep(
		escuela,
		5,
		experts = [
			individual_ann,
			hyperopt_fts_predict,
			auto_arima_predict
		],
		args = [
			dict(window_len = 5, normalizators = [MinMaxNormalizator]), # Normalizador para individual ann
			dict(),
			dict(normalizators = [MinMaxNormalizator]), # Normalizador para auto arima
		]
	)
	print(prediction)
