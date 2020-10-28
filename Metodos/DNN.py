import os, sys
import tensorflow as tf
import numpy as np
from tensorflow.keras.models import model_from_json

def load_model(model_name = 'default') :
	"""Función que carga a memoria un modelo de redes neuronales. Los modelos
	se encuentran guardados en el directorio ModelosDNN.
	
	Args:
		model_name (str, optional): nombre del modelo. Si no se especifica se
			cargará por defecto el modelo llamado default.
	
	Returns:
		loaded_model(:obj: `tensorflow.keras.model`): objeto con el modelo.
	"""
	# load json and create model
	#json_file = open(model_name + '.json', 'r')
	json_file = open(os.path.join(
		os.path.dirname(__file__), 
		os.pardir, 
		'ModelosDNN/', 
		model_name + '.json'
	), 'r')
	loaded_model_json = json_file.read()
	json_file.close()
	loaded_model = model_from_json(loaded_model_json)
	# load weights into new model
	#loaded_model.load_weights(model_name + ".h5")
	loaded_model.load_weights(os.path.join(
		os.path.dirname(__file__), 
		os.pardir, 
		'ModelosDNN/', # Directorio
		model_name + '.h5' # Archivo
	))
	
	print('Modelo %s cargado en memoria' % (model_name))
	return loaded_model

def dnn_predict(data, prediction_size, cached_model = None) :
	"""Función que realiza una predicción utilizando un modelo DNN.
	
	Args:
		data (:obj: `numpy.array`): datos de la observación a predecir.
		prediction_size (int): número de años a predecir.
		cached_model (:obj: `tensorflow.keras.model`, optional): 
			modelo a utilizar para la predicción. Si no se especifíca el modelo
			se cargará por defecto el modelo default.
			
			Nota importante (19/07/20):
			El modelo default fue cambiado por el modelo ValidacionPrimaria. Se
			recomienda siempre especificar el parámetro cached_model.
		
	Returns:
		(:obj: `numpy.array`): arreglo numpy con los datos de la predicción 
			con forma (prediction__size,).
	"""
	model = None
	if cached_model == None :
		model = load_model()
	else :
		model = cached_model
	
	window_len = model.layers[0].input_shape[1]
	
	prediction = np.zeros(prediction_size)
	X = np.zeros((1, window_len))
	X[0] = data[-window_len:]
	assert(X.shape == (1, window_len))
	
	for i in range(prediction_size) :
		prediction[i] = model.predict(X)[0][0]
		for j in range(window_len - 1) :
			X[0][j] = X[0][j + 1]
		X[0][window_len - 1] = prediction[i]
	
	return prediction

def dnn_predict_by_year(data, prediction_size, cached_model = None) :
	"""Función que realiza una predicción utilizando modelos cuyo Y_size es mayor
	a uno (Y_size representa el número de años que predice el modelo).
	
	Args:
		data (:obj: `numpy.array`): datos de la observación.
		prediction_size (int): número de años a predecir.
		cached_model (:obj: `tensorflow.keras.model`, optional):
			modelo a utilizar para la predicción. Si no se especifíca el modelo
			se cargará por defecto el modelo default con el sufijo prediction_size.
			
			Nota importante (19/07/20):
			Los modelos default{1,2,3,4,5} fueron removidos del directorio de modelos.
	
	Returns:
		(:obj: `numpy.array`): arreglo numpy con los datos de la predicción 
			con forma (prediction__size,).
	"""
	model = None
	if cached_model == None :
		model = load_model('default' + str(prediction_size))
	else :
		model = cached_model
	
	window_len = model.layers[0].input_shape[1]
	
	# Esta línea no está testeada pero es importante
	assert(model.layers[-1].input_shape[1] == prediction_size)
	
	X = np.zeros((1, window_len))
	X[0] = data[-window_len:]
	assert(X.shape == (1, window_len))
	
	prediction = model.predict(X)
	return prediction[0]

def differenced_dnn(data, prediction_size, cached_model) :
	assert(prediction_size == 1)
	def differencing_transform(data) :
		n = len(data) - 1
		new_data = np.zeros(n)
		for i in range(n - 1, -1, -1) :
			new_data[i] = data[i + 1] - data[i]
		
		return new_data.astype(np.int32)
	
	new_data = differencing_transform(data) 
	
	model = None
	if cached_model == None :
		model = load_model()
	else :
		model = cached_model
	
	window_len = model.layers[0].input_shape[1]
	
	prediction = np.zeros(prediction_size)
	X = np.zeros((1, window_len))
	X[0] = new_data[-window_len:]
	assert(X.shape == (1, window_len))
	
	for i in range(prediction_size) :
		prediction[i] = model.predict(X)[0][0]
		for j in range(window_len - 1) :
			X[0][j] = X[0][j + 1]
		X[0][window_len - 1] = prediction[i]
	
	# Esto solo va a funcionar si prediction_size == 1
	return (prediction + data[-1]).astype(np.int32)

def dnn_predict_by_mean(data, prediction_size) :
	mean = data.mean() 
	if mean > 73.045 :
		model = load_model('DNNMediana2')
	else :
		model = load_model('DNNMediana1')
	
	window_len = model.layers[0].input_shape[1]
	
	prediction = np.zeros(prediction_size)
	X = np.zeros((1, window_len))
	X[0] = data[-window_len:]
	assert(X.shape == (1, window_len))
	
	for i in range(prediction_size) :
		prediction[i] = model.predict(X)[0][0]
		for j in range(window_len - 1) :
			X[0][j] = X[0][j + 1]
		X[0][window_len - 1] = prediction[i]
	
	return prediction

if __name__ == "__main__" :
	escuela = np.array([188,180,172,204,187,180,177,182,178,171,165,162,160,159,167,163,151])
	print(differenced_dnn(
		data = escuela,
		prediction_size = 1,
		cached_model = load_model('DNNPublicas')
	))
