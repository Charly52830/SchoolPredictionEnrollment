import os, sys
import tensorflow as tf
import numpy as np
import pandas as pd
from tensorflow.keras.models import model_from_json
from LoadData import loadData

def get_batch_len(n) :
	batch_len = n
	for x in range(2, n) :
		if x * x > n:
			break
		if n % x == 0 :
			if x > 2 and n // x > 2:
				return x
			elif n // x > 2 and x > 2:
				return n // x
	return batch_len
 
def create_model(dataset_name, window_len, test_size, Y_size = 1, model_name = 'default') :
	"""Función que entrena una red neuronal y guarda el modelo en dos archivos, 
	uno con extensión .h5 y otro con extensión .json. Los modelos pueden ser
	cargados más tarde para realizar predicciones.
	
	Args:
		window_len (int): longitud de los vectores de entrada de la red neuronal
			(que también representa el número de años que se toman para la predicción).
		dataset_name (str): nombre del dataset con el que se entrenará a la red
			neuronal.
		test_size (int): número de años que forman parte del conjunto de prueba. Por 
			regla de negocio este valor debe ser de 5 años. 
		Y_size (int, optional): número de años que va a predecir la red neuronal. 
			Por defecto su valor es de 1.
		model_name (str): nombre con el que se guardarán los archivos del modelo.
	"""
	x_train, y_train, x_test, y_test = loadData(dataset_name, window_len, test_size, Y_size, drop_columns = 0)
	
	assert(x_train.shape[0] == window_len)
	tf.random.set_seed(0)
	
	# Convoluciones
	"""	
	model = tf.keras.models.Sequential([
		tf.keras.layers.Conv1D(
			filters = 60,
			kernel_size = 5,
			strides = 1,
			padding = 'causal',
			activation = 'relu',
			input_shape = (None, 5)
		),
		tf.keras.layers.Dense(60, activation = "relu"),
		tf.keras.layers.Dense(30, activation = "relu"),
		tf.keras.layers.Dense(15, activation = "relu"),
		tf.keras.layers.Dense(Y_size)
	])
	"""
	model = tf.keras.models.Sequential([
		tf.keras.layers.Dense(60, input_shape = [window_len]),
		tf.keras.layers.Dense(30,),
		tf.keras.layers.Dense(15,),
		tf.keras.layers.Dense(Y_size)
	])
	
	lr_schedule = tf.keras.callbacks.LearningRateScheduler(
		lambda epoch: 1e-6 * 10 ** (epoch / 20)
	)
	optimizer = tf.keras.optimizers.SGD(lr = 1e-8, momentum = 0.9)
	#optimizer = tf.keras.optimizers.Adam(learning_rate = 1e-6)
	model.compile(loss = "mse", optimizer = optimizer)	

	# Crear tensores (Convoluciones)
	batch_len = get_batch_len(x_train.shape[1])	# Número de observaciones (m)
	train_inputs = tf.constant(x_train.T)
	train_inputs = tf.constant(np.array(tf.split(train_inputs, train_inputs.shape[0] // batch_len )))
	train_targets = tf.constant(y_train.T)
	train_targets = tf.constant(np.array(tf.split(train_targets, train_targets.shape[0] // batch_len )))
	
	batch_len = get_batch_len(x_test.shape[1])	# Número de observaciones (m)
	test_inputs = tf.constant(x_test.T)
	test_inputs = tf.reshape(test_inputs, (1, test_inputs.shape[0], test_inputs.shape[1]))
	
	model.fit(
		x_train.T, 
		y_train.T, 
		epochs = 20,
		#batch_size = window_len,
		verbose = 1,
		#callbacks = [lr_schedule],
		#validation_data = (x_test.T, y_test.T)
	)
	
	# Comentar este bloque de lineas si se entrena un modelo para producción
	#prediction = model.predict(test_inputs)	# Convoluciones
	#prediction = prediction.reshape((y_test.shape[1], y_test.shape[0]))	# Convoluciones
	prediction = model.predict(x_test.T)
	assert(prediction.shape == y_test.T.shape)
	MAE = np.abs(prediction - y_test.T).mean()
	print("MAE: ", MAE)
	MAPE = np.abs((prediction - y_test.T) / y_test.T ).mean()
	print("MAPE: ", MAPE)
	
	# Save model
	# serialize model to JSON
	model_json = model.to_json()
	with open(os.path.join(
		os.path.dirname(__file__), 
		os.pardir, 
		'ModelosDNN/', 
		model_name + '.json'
	),"w") as json_file :
		json_file.write(model_json)
	
	model.save_weights(os.path.join(
		os.path.dirname(__file__), 
		os.pardir, 
		'ModelosDNN/', 
		model_name + '.h5'
	))
	print("Modelo %s guardado en el directorio ModelosDNN" % (model_name))

if __name__ == "__main__" :
	create_model(
		dataset_name = 'DifferencedPrimariasPublicas',
		window_len = 5,
		test_size = 5,
		Y_size = 1,
		model_name = 'DNNPublicas'
	)
