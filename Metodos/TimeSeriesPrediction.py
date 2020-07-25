import numpy as np
import pandas as pd

def time_series_prediction(train_Y, steps, SEASONAL_LAG, WINDOW_LEN) :
	"""Algoritmo de predicción de una serie de tiempo. Utiiliza el promedio de
	la diferencia de valores pasados más un valor anterior en la serie de tiempo.
	
	Se ejecuta en O(n) utilizando recursividad con 3 funciones.
	
	Puede mejorarse la precisión si se suma el promedio de una ventana de 
	longitud WINDOW_LEN centrada en la posición i - SEASONAL_LAG. Esto puede 
	contribuir a reducir el ruido en la predicción.
	
	Args:
		train_Y (:obj: `numpy.array`): valores de entrenamiento de la serie de tiempo.
		steps (int): número de valores a predecir.
		SEASONAL_LAG: controla el número anterior del valor de la serie de tiempo
			a sumar.
		WINDOW_LEN: longitud del promedio de la diferencia de los últimos valores.
	
	Returns: 
		list: lista de python (NO NUMPY ARRAY) de longitud steps con los valores 
		predecidos.
	"""
	
	N = len(train_Y)
	
	if WINDOW_LEN > N or SEASONAL_LAG > N :
		print("\nERROR\nLa longitud de WINDOW_LEN o SEASONAL_LAG no pueden exceder el número de registros")
		print("WINDOW_LEN:", WINDOW_LEN, "SEASONAL_LAG:", SEASONAL_LAG, "Número de registros:", N)
		print("")
		return None
	
	prediction = [False] * steps
	lazy_mean_sum = dict()
	
	def diff(i) :
		return series(i) - series(i - SEASONAL_LAG)
	
	def mean_sum(i) :
		if not i in lazy_mean_sum :
			if i == N - 1 :
				sum = 0
				for j in range(N - WINDOW_LEN, N) :
					sum += diff(j)
				lazy_mean_sum[i] = sum
			else :
				lazy_mean_sum[i] = mean_sum(i - 1) + diff(i) - diff(i - WINDOW_LEN)
		return lazy_mean_sum[i]
	
	def series(i) :
		if i < N :
			return train_Y[i]
		if not prediction[i - N] :
			prediction[i - N] = mean_sum(i - 1) / WINDOW_LEN + series(i - SEASONAL_LAG)
		return prediction[i - N]
	
	for x in range(N, N + steps):
		series(x)
	
	return prediction

def best_prediction(X, Y, verbose = False) :
	"""Algoritmo de optimización de series de tiempo que consiste en probar todas
	las posibles combinaciones de pares de WINDOW_LEN y SEASONAL_LAG. Los
	modelos son comparados utilizando Mean Absolute Error.
	
	Trabaja en O(n^3) donde n es la longitud del segmento de entrenamiento,
	(puede optimizarse a O(n^2)).
	
	Args:
		X (:obj: `numpy.array`): segmento de entrenamiento de la serie de tiempo.
		Y (:obj: `numpy.array`): segmento de validación de la serie de tiempo.
		verbose (bool): especifica si quieres imprimir en pantalla el resultado 
		de las pruebas.
	
	Return:
		best_seasonal_lag (int): valor del seasonal lag con el que se obtuvo menor error.
		best_window_len (int): valor de window_len con el que se obtuvo menor error.
		best_prediction (float): mejor predicción del segmento de validación.
	"""
	
	validation_size = len(Y)
	train_size = len(X)
	
	best_seasonal_lag = 1
	best_window_len = 1
	best_prediction = np.array([])
	best_error = 101	#best mean absolute error
	
	for WINDOW_LEN in range(1, train_size + 1) :
		for SEASONAL_LAG in range(1, train_size + 1) :
			prediction = np.array(time_series_prediction(X, validation_size, SEASONAL_LAG, WINDOW_LEN))
			MAE = np.abs(prediction - Y).mean()	# Mean Absolute Error
			if verbose :
				print("WINDOW_LEN: ", WINDOW_LEN, "SEASONAL_LAG: ", SEASONAL_LAG, "MAE: ", MAE)
			if MAE < best_error :
				best_seasonal_lag = SEASONAL_LAG
				best_window_len = WINDOW_LEN
				best_prediction = prediction
				best_error = MAE
	
	if verbose:
		print("Best seasonal lag:", best_seasonal_lag, "Best window len:", best_window_len, "Best error:", best_error)
	
	return (best_seasonal_lag, best_window_len, best_prediction)

def fixed_partitioning_predict(data, prediction_size, validation_size = 1, verbose = False) :
	"""Predicción de una serie de tiempo utilizando estadística y fuerza bruta como
	algoritmo de optimización.
	
	Args:
		data (:obj: `numpy.array`): numpy array con los valores de la serie de tiempo.
		validation_size (int): longitud del segmento de validación.
		prediction_size (int): número de valores que quiere predecir.
		verbose (bool): especifica si quiere imprimir en pantalla los resultados del
			algoritmo optimizador.
	
	Returns: 
		(:obj: `numpy.array`): numpy array de tamaño prediction_size con la mejor 
		predicción que encontró.
	"""
	
	x_train = data[: -validation_size]
	x_validation = data[-validation_size :]
	
	seasonal_lag, window_len, _ = best_prediction(
		X = x_train, 
		Y = x_validation,
		verbose = verbose
	)
	
	return np.array(time_series_prediction(data, prediction_size, seasonal_lag, window_len))	

if __name__ == '__main__' :
	main('PrimariasCompletas.csv', 1, 1)
