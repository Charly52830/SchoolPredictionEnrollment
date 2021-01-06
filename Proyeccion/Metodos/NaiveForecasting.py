# Manejo de módulos
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from Metodos.Normalizators import MinMaxNormalizator

import numpy as np

def naive_forecasting_predict(data, prediction_size) :
	"""Realiza una predicción de los próximos prediction_size años. La predicción
	consiste en un arreglo que contiene el último dato observado de la serie de 
	tiempo repetido prediction_size veces.
	
	Args:
		data (:obj: `numpy.array`): numpy array con los valores reales de la
			observación.
		prediction_size (int): número de años a predecir.
	
	Returns:
		(:obj: `numpy.array`): numpy array con los valores de la predicción.
	"""
	prediction = np.zeros(prediction_size)
	# Broadcasting del último dato
	prediction += data[-1]
	return prediction

if __name__ == '__main__' :
	escuela = np.array([89,127,134,152,170,172,182,192,197,210,219,222,233,226,222,205,222])
	prediccion = naive_forecasting_predict(
	    data = escuela,
	    prediction_size = 5
	)
	print(prediccion)
