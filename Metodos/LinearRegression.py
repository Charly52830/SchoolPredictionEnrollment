import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def linear_regression(data, prediction_size, window_len) :
	"""Función que realiza una predicción utilizando los últimos window_len datos
	en una regresión lineal.
	
	Args:
		data (:obj: `numpy.array`): datos para la regresión lineal.
		window_len (int): número de los últimos años que se consideran para la
			regresión lineal.
		prediction_size (int): número de años que se busca predecir.
	
	Returns:
		(:obj: `numpy.array`): numpy array de forma (prediction_size,) que contiene
			los datos de la predicción.
	"""
	assert(len(data) >= window_len)
	prediction = np.concatenate((data, np.zeros(prediction_size)), axis = 0)
	X_train = np.array([i for i in range(1, window_len + 1)]).reshape((-1, 1))
	X_pred = np.array([i for i in range(1, window_len + 2)]).reshape((-1, 1))
	
	for j in range(prediction_size) :
		model = LinearRegression().fit(X_train, prediction[-(window_len + prediction_size - j) : -(prediction_size - j)])
		y_pred = model.predict(X_pred)
		prediction[len(data) + j] = y_pred[-1]
	
	return prediction[-prediction_size :]
	
def best_prediction(X, Y, verbose = False) :
	"""Función que encuentra el valor de window_len para el que la regresión
	lineal predice mejor los datos de Y. Se utiliza la métrica MAE para la
	comparación.
	
	Args:
		X (:obj: `numpy.array`): numpy array con los datos con los que la
			regresión lineal predecirá los valores de Y.
		Y (:obj: `numpy.array`): numpy array con los datos que busca predecir
			la regresión lineal.
		verbose (bool): si es True se mostrará el proceso de comparación de
			las predicciones con los distintos valores de window_len.
	
	Returns:
		int: valor de window_len que minimiza el error en la predicción de Y
			basándose en la métrica MAE.
	"""
	
	validation_size = len(Y)
	train_size = len(X)
	best_window = 2
	best_error = 1000000
	
	for window_len in range(2, train_size) :
		prediction = linear_regression(
			data = X,
			prediction_size = validation_size,
			window_len = window_len
		)
		assert(prediction.shape == Y.shape)
		MAE = np.abs(prediction - Y).mean()	# Mean Absolute Error
		
		if verbose :
			print("WINDOW_LEN:", window_len, "MAE:", MAE)
		
		if MAE < best_error :
			best_error = MAE
			best_window = window_len
	
	return best_window

def linear_regression_predict(data, prediction_size, validation_size = 1, verbose = False) :
	"""Función que realiza una predicción utilizando regresión lineal. Primero
	encuentra la cantidad de los últimos años que mejor predicen los datos de
	los validation_size últimos años del arreglo data y después realiza la
	predicción de los siguientes prediction_size datos considerando solo los últimos
	años. A esta técnica de separación de datos se le llama Fixed partitioning.
	
	Args:
		data (:obj: `numpy.array`): datos de la observación.
		prediction_size (int): número de años a predecir.
		validation_size (int): cantidad de los últimos datos considerados para 
			para encontrar el valor de window_len que mejor prediga los datos.
		
		verbose (bool): si es True se mostrará el proceso de comparación de
			las predicciones con los distintos valores de window_len.
		
	Returns:
		(:obj: `numpy.array`): numpy array de forma (prediction_size,) que contiene
			los datos de la predicción.
	"""
	x_train = data[: -validation_size]
	x_validation = data[-validation_size :]
	
	window_len = best_prediction(
		X = x_train,
		Y = x_validation,
		verbose = verbose
	)
	
	return linear_regression(data, prediction_size, window_len)

def base_linear_regression(data, prediction_size, window_len = -1) :
	"""Función que realiza una predicción de los próximos prediction_size datos
	utilizando regresión lineal.
	
	Args:
		data (:obj: `numpy.array`): numpy array con los valores reales de la
			observación.
		prediction_size (int): número de años a predecir.
		window_len (int, optional): número de los últimos años a tomar en cuenta
			para la predicción.
	
	Returns:
		(:obj: `numpy.array`): numpy array con los valores de la predicción.
	"""
	if window_len == -1 :
		window_len = len(data)
	
	assert(window_len >= 2)
	
	x = np.array([ i for i in range(window_len)]).reshape(-1, 1)
	y = data[-window_len:]
	
	model = LinearRegression()
	model.fit(x, y)
	
	x_pred = np.array([i + window_len for i in range(prediction_size)]).reshape(-1, 1)
	y_pred = model.predict(x_pred)
	
	return y_pred

if __name__ == '__main__' :
	base_linear_regression(np.array([61,61,63,77,69,84,88,74,96,93,75,82,77,88,93,91,95,88,89,98,90,87]), 5, 8)
