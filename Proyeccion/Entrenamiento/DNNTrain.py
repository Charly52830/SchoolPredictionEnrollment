import os, sys
import tensorflow as tf
import numpy as np
import pandas as pd
from tensorflow.keras.models import model_from_json
from LoadData import loadData

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
	print(x_train.shape, y_train.shape)
	print(x_test.shape, y_test.shape)
	
	assert(x_train.shape[0] == window_len)
	tf.random.set_seed(0)
	
	model = tf.keras.models.Sequential([
		tf.keras.layers.Dense(60, input_shape = [window_len], activation = "relu"),
		tf.keras.layers.Dense(30, activation = "relu"),
		tf.keras.layers.Dense(15, activation = "relu"),
		tf.keras.layers.Dense(Y_size)
	])
	
	lr_schedule = tf.keras.callbacks.LearningRateScheduler(
		lambda epoch: 1e-6 * 10 ** (epoch / 20)
	)
	optimizer = tf.keras.optimizers.SGD(lr = 1e-6, momentum = 0.9)
	#optimizer = tf.keras.optimizers.Adam(learning_rate = 1e-6)
	model.compile(loss = "mae", optimizer = optimizer)	
	
	model.fit(
		x_train.T, 
		y_train.T, 
		epochs = 20,
		batch_size = window_len,
		verbose = 1,
		#callbacks = [lr_schedule],
		#validation_data = (x_test.T, y_test.T)
	)
	
	# Comentar este bloque de lineas si se entrena un modelo para producción
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
	print("Modelo %s guardado en el dorectorio ModelosDNN" % (model_name))

if __name__ == "__main__" :
	# Aquí van las pruebas
	pass
