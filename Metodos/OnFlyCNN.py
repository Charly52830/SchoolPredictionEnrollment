import numpy as np
import tensorflow as tf

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

def cnn_lstm_predict(data, prediction_size, window_len) :
	tf.random.set_seed(1)
	data = data.astype(np.float64)
	inputs, targets = load_data(data, window_len)
	
	model = tf.keras.Sequential([
		tf.keras.layers.Conv1D(
			filters = 32,
			kernel_size = 5,
			strides = 1,
			padding = 'causal',
			activation = 'relu',
			input_shape = (None, window_len)
		),
		tf.keras.layers.LSTM(32, return_sequences=True),
		tf.keras.layers.Dense(units=32, activation='relu'),
		tf.keras.layers.Dense(units=1),
	])
	
	model.compile(
		loss = tf.losses.MeanSquaredError(),
		#loss = "mae",
		optimizer = tf.optimizers.Adam(lr = 1),
		#optimizer = tf.keras.optimizers.SGD(lr = 1e-6, momentum = 0.9),
		metrics=[tf.metrics.MeanAbsoluteError()]
	)
	
	early_stopping = tf.keras.callbacks.EarlyStopping(
		monitor='loss',
		patience=10,
		mode='min'
	)
	
	class myCallback(tf.keras.callbacks.Callback):
		def on_epoch_end(self, epoch, logs={}):
			if logs.get('loss') < 500 + 1e-5  :
				#print("\nReached loss 500, canceling training.!")
				self.model.stop_training = True
	
	my_callback = myCallback()
	
	model.fit(
		inputs,
		targets,
		epochs = 100,
		callbacks = [early_stopping, my_callback],
		verbose = 0
	)
	
	x_predict = tf.constant(np.array(data[-window_len:]).reshape((1,window_len)))
	x_predict = tf.reshape(x_predict, (1, 1, window_len))
	
	prediction = model.predict(x_predict)
	prediction = prediction.reshape((1,))
	
	if model.metrics[0].result().numpy() < 400.0 or model.metrics[0].result().numpy() > 800.0:	# Loss below 400
		return np.array([data[-1]]), 1000.0
	return prediction, model.metrics[1].result().numpy()	# Prediccion, MAE

def custom_cnn_predict(data, prediction_size) :
	assert(prediction_size == 1)
	min_error = 1001.0
	ans = np.zeros(prediction_size)
	ans = data[-1]	# Broadcasting del último elemento
	
	for i in range(3,7) :
		prediction, error = cnn_lstm_predict(
			data = data,
			prediction_size = prediction_size,
			window_len = i
		)
		if error < min_error :
			min_error = error
			ans = prediction
	return ans

if __name__ == '__main__' :
	escuela = np.array([128,133,124,117,120,113,113,114,111,113,117,121,125,127,131,111,103])
	print(custom_cnn_predict(escuela, 1))
	
