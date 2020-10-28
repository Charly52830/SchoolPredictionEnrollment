import os, sys
import tensorflow as tf
import numpy as np
from tensorflow.keras.models import model_from_json
#from DNN import load_model

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

def cnn_predict(data, prediction_size, cached_model = None) :
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
	assert(prediction_size == 1)
	
	model = None
	if cached_model == None :
		model = load_model()
	else :
		model = cached_model
	
	window_len = model.layers[0].input_shape[2]
	
	prediction = np.zeros(prediction_size)
	X = np.zeros((1, window_len))
	X[0] = data[-window_len:]
	assert(X.shape == (1, window_len))
	
	for i in range(prediction_size) :
		inputs = tf.constant(X)
		inputs = tf.reshape(inputs, (1, inputs.shape[0], inputs.shape[1]))
		prediction[i] = model.predict(inputs)[0][0][0]
		for j in range(window_len - 1) :
			X[0][j] = X[0][j + 1]
		X[0][window_len - 1] = prediction[i]
	
	return prediction

if __name__ == '__main__' :
	escuela = np.array([650,659,698,681,685,674,729,755,774,764,776,790,832,769,799,811,769])
	print(cnn_predict(
		data = escuela,
		prediction_size = 1,
		cached_model = load_model('ValidacionPrimariasCNN')
	))
