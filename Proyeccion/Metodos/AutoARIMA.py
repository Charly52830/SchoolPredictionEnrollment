# Manejo de módulos
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import numpy as np
from pmdarima.arima import auto_arima
from Metodos.Normalizators import MinMaxNormalizator

def train_auto_arima(data) :
	"""Función para entrenar un nuevo modelo ARIMA. Encuentra los mejores parámetros
	p, d, q, P, D, Q que minimizan el error en la predicción.
	
	Args:
	    data (:obj: `numpy.array`): arreglo con los datos de la serie de tiempo
	        con dimensión (n,).
	
	Returns:
	    model (:obj: `pmdarima.arima.arima.ARIMA`): modelo ARIMA entrenado
	
	"""
	# Asignar el valor máximo de los parámetros p,d,q,P,D,Q
	model = auto_arima(
		y = data,
		start_p = 0,
		start_q = 0,
		max_p = 7,
		max_d = 3,
		max_q = 7,
		start_P = 0,
		start_Q = 0,
		max_P = 4,
		max_Q = 4,
		m = 1,
		seasonal = False,
		suppress_warnings = True,
		stepwise = True,
		random_state = 20,
		n_fits = 50,
		trace = False,
		max_order = 10,
	)
	return model

def auto_arima_predict(data, prediction_size, normalizators = []) :
	"""Realiza una predicción utilizando el modelo ARIMA luego de encontrar los
	parámetros de p, d y q que mejor modelen a la serie de tiempo.
	
	Args:
		data (:obj: `numpy.array`): numpy array con los valores reales de la
			serie de tiempo con dimensiones (n,).
		prediction_size (int): número de años a predecir.
		normalizators (:list: `Normalizator`): lista de objetos Normalizator. Las 
			normalizaciones se aplican en el orden en el que se encuentran en la 
			lista y se encuentran en el directorio Metodos/Normalizators.
	
	Returns:
		(:obj: `numpy.array`): numpy array con los valores de la predicción.
	"""
	# Aplicar las normalizaciones
	norms = []
	for i in range(len(normalizators)) :
		normalizator = normalizators[i](data)
		data = normalizator.normalize(data)
		norms.append(normalizator)
	
	# Entrenar el modelo
	model = train_auto_arima(data)
	
	# Obtener predicción
	prediction = model.predict(n_periods = prediction_size)
	
	# Aplicar las desnormalizaciones en el orden inverso
	for i in range(len(norms) - 1, -1, -1) :
		prediction = norms[i].denormalize(prediction)
	return prediction

def evaluate_and_predict_arima(data, prediction_size = 5, normalizators = [MinMaxNormalizator], OFFSET_ANIOS = 5) :
	"""Función que devuelve la predicción de los datos históricos y los datos
	futuros aplicando el modelo ARIMA.
	
	Args:
	    data (:obj: `numpy.array`): numpy array con los valores reales de la
			serie de tiempo con dimensiones (n,).
		prediction_size (int, opcional): número de años a predecir.
		normalizators (:list: `Normalizator`, opcional): lista de objetos Normalizator. 
			Las normalizaciones se aplican en el orden en el que se encuentran 
			en la lista, las clases Normalizator se encuentran en el directorio 
			Metodos/Normalizators.
		OFFSET_ANIOS (int, opcional): número de años a remover de la predicción
			histórica. Tienen que removerse los primeros 5 años para que esta
			función pueda ser utilizada junto con IndividualANN en la opinión de
			expertos, pero si esta función se va a utilizar por sí sola no hace
			falta remover ningún año.
	
	Returns:
		prediction (:obj: `numpy.array`): arreglo con la predicción futura con
			dimensiones (prediction_size,).
		train_prediction (:obj: `numpy.array`): arreglo con la predicción histórica
			con dimensiones (n - OFFSET_ANIOS,).
	"""
	# Aplicar las normalizaciones
	norms = []
	for i in range(len(normalizators)) :
		normalizator = normalizators[i](data)
		data = normalizator.normalize(data)
		norms.append(normalizator)
	
	# Entrenar el modelo
	model = train_auto_arima(data)
	
	# Obtener predicción futura
	prediction = model.predict(n_periods = prediction_size)
	
	# Obtener la predicción del conjunto de los datos de entrenamiento
	if OFFSET_ANIOS :
		train_prediction = model.predict_in_sample()[OFFSET_ANIOS:]
	else :
		train_prediction = model.predict_in_sample()
	
	# Aplicar las desnormalizaciones en el orden inverso
	for i in range(len(norms) - 1, -1, -1) :
		train_prediction = norms[i].denormalize(train_prediction)
		prediction = norms[i].denormalize(prediction)
	
	return prediction, train_prediction

if __name__ == '__main__' :
	escuela = np.array([89,127,134,152,170,172,182,192,197,210,219,222,233,226,222,205,222])
	prediccion = auto_arima_predict(
		data = escuela,
		prediction_size = 5,
		normalizators = [MinMaxNormalizator]
	)
	print(prediccion)
