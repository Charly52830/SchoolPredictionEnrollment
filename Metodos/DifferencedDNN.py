import os, sys
import tensorflow as tf
import numpy as np

def differencing_transform(data) :
	n = len(data) - 1
	new_data = np.zeros(n)
	for i in range(n - 1, -1, -1) :
		new_data[i] = data[i + 1] - data[i]
	
	return new_data.astype(np.int32)

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

def load_data(data, window_len, test_size = 5, shuffle = False) :
	data = np.concatenate((data, np.array([0] * test_size)), axis = 0)
	targets = data[test_size :]
	input_data = data[: -test_size]
	
	n = len(input_data) - window_len + 1
	batch_size = get_batch_len(n)
	
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

def differenced_dnn(data, prediction_size, window_len) :
	tf.random.set_seed(1)
	
	new_data = differencing_transform(data)
	new_data = new_data.astype(np.float64)
	inputs, targets = load_data(new_data, window_len)
	
	model = tf.keras.models.Sequential([
		tf.keras.layers.Dense(60, input_shape = (None, inputs.shape[2])),
		tf.keras.layers.Dense(30,),
		tf.keras.layers.Dense(15,),
		tf.keras.layers.Dense(1)
	])
	
	model.compile(
		loss = "mae",
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
		epochs = 103,
		callbacks = [early_stopping, lr_schedule],
		verbose = 0
	)
	
	prediction = np.zeros(prediction_size)
	X = np.zeros((1, window_len))
	X[0] = new_data[-window_len:]
	assert(X.shape == (1, window_len))
	
	for i in range(prediction_size) :
		X_tensor = tf.constant(X)
		X_tensor = tf.reshape(X_tensor, (1, 1, window_len))
		prediction[i] = model.predict(X_tensor)[0][0][0]
		for j in range(window_len - 1) :
			X[0][j] = X[0][j + 1]
		X[0][window_len - 1] = prediction[i]
	
	
	#X = tf.constant(new_data[-window_len:])
	#X = tf.reshape(X, (1, 1, window_len))
	#prediction = model.predict(X)
	
	# Esto solo va a funcionar si prediction_size == 1
	return (prediction + data[-1]).astype(np.int32).reshape((prediction_size,))

if __name__ == '__main__' :
	escuela = np.array([129,116,121,130,111,92,101,110,114,119,118,130,132,116,113,91,109])
	print(differenced_dnn(
		data = escuela,
		prediction_size = 5,
		window_len = 5
	))
