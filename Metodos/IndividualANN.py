# Manejo de módulos
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import os, sys
import tensorflow as tf
import numpy as np
import warnings

from Entrenamiento.Normalizators import MinMaxNormalizator, DummyNormalizator, DifferencingNormalizator

def get_batch_size(n) :
	"""Función que encuentra un divisor de n para ser el tamaño del batch. Se
	cumple que el valor devuelto es mayor a dos y que el número de batches es
	también mayor a dos.
	
	El propósito de esta función es que obtener batches del mismo tamaño, que es
	un requisito para la función load_data.
	
	Args:
		n (int): número de observaciones totales.
	
	Returns:
		(int): número de observaciones que contendrá un batch, es decir, el
			tamaño del batch.
	
	"""
	batch_size = n
	for x in range(2, n) :
		if x * x > n:
			break
		if n % x == 0 :
			if x > 2 and n // x > 2:
				return x
			elif n // x > 2 and x > 2:
				return n // x
	return batch_size

def load_data(data, window_len, shuffle = False) :
	"""Función que prepara los datos de entrenamiento a partir de un numpy array
	que contiene los datos de la serie de tiempo.
	
	Args:
		data (:obj: `numpy.array`): numpy array de una dimensión que contiene
			los datos de entrenamiento de la serie de tiempo.
		window_len (int): número de lags que representan a los predictores de la
			ANN.
		shuffle (bool): si es True se aplicará random_shuffle a los elementos de
			la entrada de la red neuronal, recomendado para ANN que no son RNN.
			Si es False entonces no se aplicará un random shuffle.
		
	Returns:
		inputs (:obj: `tensorflow.Tensor`): tensor de tres dimensiones. La 
			primer dimensión corresponde al número de batches, la segunda 
			corresponde al tamaño de cada batch, la tercera corresponde al 
			número de predictores (window_len).
		targets (:obj: `tensorflow.Tensor`): tensor de dos dimensiones. La 
			primer dimensión corresponde al número de batches, la segunda
			corresponde al tamaño de cada batch.
	
	"""
	input_data = data[: -1]
	targets = np.concatenate((data[window_len :], np.zeros(window_len - 1)), axis = 0)
	
	n = len(input_data) - window_len + 1
	batch_size = get_batch_size(n)
	
	dataset = tf.keras.preprocessing.timeseries_dataset_from_array(
		data = input_data,
		targets = targets,
		sequence_length = window_len,
		sampling_rate = 1,
		sequence_stride = 1,
		shuffle = shuffle,
		batch_size = batch_size
	)
	
	inputs = tf.stack([inputs for inputs, _ in dataset], axis = 0)
	targets = tf.stack([target for _, target in dataset], axis = 0)
	
	return tf.cast(inputs, tf.float64), tf.cast(targets, tf.float64)

def individual_ann(data, prediction_size, window_len, normalizators = []) :
	"""Función que entrena una red neuronal para una sola serie de tiempo y que
	se entrena únicamente con los datos de la serie de tiempo.
	
	Args:
		data (:obj: `numpy.array`): numpy array de una dimensión que contiene
			los datos de entrenamiento de la serie de tiempo.
		prediction_size (int): número de años a predecir.
		window_len (int): número de lags que representan a los predictores de la
			ANN.
		normalizators (:list: `Normalizator`): lista de objetos Normalizator. Las 
			normalizaciones se aplican en el orden en el que se encuentran en la 
			lista y se encuentran en el directorio Entrenamiento/Normalizators.
	Returns:
		(:obj: `numpy.array`): arreglo numpy con los datos de la predicción 
			con forma (prediction__size,)
	
	"""
	tf.random.set_seed(1)
	data = data.astype(np.float64)
	
	# Aplicar las normalizaciones
	norms = []
	for i in range(len(normalizators)) :
		normalizator = normalizators[i](data)
		data = normalizator.normalize(data)
		norms.append(normalizator)
	
	inputs, targets = load_data(data, window_len)
	model = tf.keras.models.Sequential([
		tf.keras.layers.Dense(60, input_shape = (None, inputs.shape[2]), activation = "tanh"),
		tf.keras.layers.Dense(30, activation = "tanh"),
		tf.keras.layers.Dense(15, ),
		tf.keras.layers.Dense(1)
	])
	
	model.compile(
		loss = "mse",
		optimizer = tf.keras.optimizers.SGD(lr = 1e-6, momentum = 0.9)
	)
	
	lr_schedule = tf.keras.callbacks.LearningRateScheduler(
		lambda epoch: 1e-6 * 10 ** (epoch / 20)
	)
	
	early_stopping = tf.keras.callbacks.EarlyStopping(
		monitor='loss',
		patience=5,
		mode='min'
	)
	
	model.fit(
		inputs,
		targets,
		epochs = 100,
		callbacks = [early_stopping, lr_schedule],
		verbose = 0
	)
	
	prediction = np.zeros(prediction_size)
	X = np.zeros((1, window_len))
	X[0] = data[-window_len:]
	assert(X.shape == (1, window_len))
	
	for i in range(prediction_size) :
		X_tensor = tf.constant(X)
		X_tensor = tf.reshape(X_tensor, (1, 1, window_len))
		prediction[i] = model.predict(X_tensor)[0][0][0]
		for j in range(window_len - 1) :
			X[0][j] = X[0][j + 1]
		X[0][window_len - 1] = prediction[i]
	
	# Aplicar las desnormalizaciones en el orden inverso
	for i in range(len(norms) - 1, -1, -1) :
		prediction = norms[i].denormalize(prediction)
	return prediction

if __name__ == '__main__' :
	warnings.filterwarnings("ignore")
	escuela = np.array([89,127,134,152,170,172,182,192,197,210,219,222,233,226,222,205,222,223])
	prediction = individual_ann(
		data = escuela,
		prediction_size = 5,
		window_len = 5,
		normalizator = MinMaxNormalizator(escuela, -1, 1)
	)
	print(prediction)
