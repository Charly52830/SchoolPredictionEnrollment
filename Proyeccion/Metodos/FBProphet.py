# Manejo de módulos
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import pandas as pd
import numpy as np
from prophet import Prophet

from Metodos.Normalizators import MinMaxNormalizator

def train_fb_prophet(data):
	"""Entrena un modelo de FB Prophet.
	
	Args:
		data (:obj: `numpy.array`): numpy array con los valores reales de la
			serie de tiempo con dimensiones (n,).
	
	Returns:
		model (:obj: `fbprophet.forecaster.Prophet`): modelo FB Prophet entrenado.
	"""
	# Crear dataframe para pasar al modelo
	data = {
		'ds' : ["%d-12-31" % (1998 + i) for i in range(len(data))],
		'y' : data
	}
	
	df = pd.DataFrame(data)
	
	# Entrenar modelo
	model = Prophet()
	model.fit(df)
	
	return model

def fb_prophet_predict(data, prediction_size, normalizators = []) :
	"""Realiza una predicción de una serie de tiempo anual utilizando FB Prophet.
	
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
	model = train_fb_prophet(data)
	
	# Obtener predicción
	prediction = model.predict(model.make_future_dataframe(periods = prediction_size, freq = 'Y'))['yhat']
	prediction = np.array(prediction)[-prediction_size:]
	
	# Aplicar las desnormalizaciones en el orden inverso
	for i in range(len(norms) - 1, -1, -1) :
		prediction = norms[i].denormalize(prediction)
	return prediction

def evaluate_and_predict_fb_prophet(data, prediction_size = 5, normalizators = [MinMaxNormalizator], OFFSET_ANIOS = 5) :
	"""Función que devuelve la predicción de los datos históricos y los datos
	futuros aplicando FB Prophet.
	
	Args:
	    data (:obj: `numpy.array`): numpy array con los valores reales de la
			serie de tiempo con dimensiones (n,).
		prediction_size (int, optional): número de años a predecir.
		normalizators (:list: `Normalizator`, optional): lista de objetos Normalizator. 
			Las normalizaciones se aplican en el orden en el que se encuentran 
			en la lista, las clases Normalizator se encuentran en el directorio 
			Metodos/Normalizators.
		OFFSET_ANIOS (int, optional): número de años a remover de la predicción
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
	model = train_fb_prophet(data)
	
	# Obtener predicción futura
	prediction = model.predict(model.make_future_dataframe(periods = prediction_size, freq = 'Y'))['yhat']
	train_prediction = np.array(prediction[: - prediction_size])
	prediction = np.array(prediction)[- prediction_size:]
	
	# Obtener la predicción del conjunto de los datos de entrenamiento
	if OFFSET_ANIOS :
		train_prediction = train_prediction[OFFSET_ANIOS:]
	
	# Aplicar las desnormalizaciones en el orden inverso
	for i in range(len(norms) - 1, -1, -1) :
		train_prediction = norms[i].denormalize(train_prediction)
		prediction = norms[i].denormalize(prediction)
	
	return prediction, train_prediction

if __name__ == '__main__' :
	escuela = np.array([89,127,134,152,170,172,182,192,197,210,219,222,233,226,222,205,222])
	prediccion = fb_prophet_predict(
		data = escuela,
		prediction_size = 5,
		normalizators = [MinMaxNormalizator]
	)
	print(prediccion)
