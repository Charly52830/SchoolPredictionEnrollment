import numpy as np
import pandas as pd
from pmdarima.arima import auto_arima

def auto_arima_predict(data, prediction_size) :
	"""Realiza una predicción utilizando el modelo ARIMA luego de encontrar los
	parámetros de p, d y q que mejor modelen a la serie de tiempo.
	
	Args:
		data (:obj: `numpy.array`): numpy array con los valores reales de la
			observación.
		prediction_size (int): número de años a predecir.
	
	Returns:
		(:obj: `numpy.array`): numpy array con los valores de la predicción.
	"""
	
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
	prediction = model.predict(n_periods = prediction_size)
	
	return prediction

if __name__ == '__main__' :
	pass
