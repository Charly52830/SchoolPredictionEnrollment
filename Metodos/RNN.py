import numpy as np
import tensorflow as tf

def load_data(data, window_size) :
	
	ts_len = len(data)
	assert(window_size + 1 <= ts_len)
	
	m = ts_len - window_size
	
	print("m:", m)
	
	x_train = np.zeros((window_size, m))
	y_train = np.zeros((1, m))
	
	m_count = 0
	
	for j in range(window_size, ts_len) :
		x_train[:, m_count] = data[j - window_size : j]
		y_train[:, m_count] = data[j]
		m_count += 1
	
	assert(m_count == m)
	
	return (x_train, y_train)

def create_model(data, window_size) :

	class myCallback(tf.keras.callbacks.Callback):
		def on_epoch_end(self, epoch, logs={}):
			if logs.get('mae') < 10.0 + 1e-5  :
				print("\nReached mae 9, canceling training.!")
				self.model.stop_training = True
			elif logs.get('mape') < 10.0 + 1e-5 :
				print("\nReached mape 9.0, canceling training.!")
				self.model.stop_training = True

	x_train, y_train = load_data(data, window_size)
	
	print(x_train)
	
	#print(x_train.shape)
	#print(y_train.shape)
	
	assert(x_train.shape[0] == window_size)
	
	tf.random.set_seed(0)
	
	model = tf.keras.models.Sequential([
		tf.keras.layers.Lambda(lambda x: tf.expand_dims(x, axis = -1), input_shape = [None]),
		tf.keras.layers.SimpleRNN(3, return_sequences = True),
		tf.keras.layers.SimpleRNN(2, return_sequences = True),
		tf.keras.layers.SimpleRNN(1),
		tf.keras.layers.Dense(1)
	])
	
	lr_schedule = tf.keras.callbacks.LearningRateScheduler(
		lambda epoch: 1e-6 * 10 ** (epoch / 20)
	)
	
	my_callback = myCallback()
	
	optimizer = tf.keras.optimizers.SGD(lr = 1e-10, momentum = 0.9)
	#optimizer = tf.keras.optimizers.Adam(learning_rate = 1e-6)
	model.compile(loss = "mae", optimizer = optimizer, metrics = ["mae", "mape"])
	
	print('Entrenando...')
	model.fit(
		x_train.T,
		y_train.T,
		epochs = 30,
		batch_size = window_size,
		#callbacks = [lr_schedule, my_callback],
		callbacks = [lr_schedule],
		verbose = 2
	)
	
	return model
	

def rnn_predict(data, prediction_size, window_size = 5) :
	model = create_model(data, window_size)
	
	prediction = np.zeros(prediction_size)
	X = np.zeros((1, window_size))
	X[0] = data[-window_size:]
	
	assert(X.shape == (1, window_size))
	
	for i in range(prediction_size) :
		print(X)
		prediction[i] = model.predict(X)[0][0]
		for j in range(window_size - 1) :
			X[0][j] = X[0][j + 1]
		X[0][window_size - 1] = prediction[i]
	
	return prediction

if __name__ == '__main__' :
	matricula_estado = np.array([224288,218311,212178,209284,202853,198284,197430,196997,196940,199294,201120,202799,203100,203010,202541,196441,194857,194833,196187])
	#X = np.array([89,127,134,152,170,172,182,192,197,210,219,222,232,226,222,205])
	X = matricula_estado[:-3]
	
	#Y = np.array([222,229,241])
	Y = matricula_estado[-3:]
	prediction = rnn_predict(X, 3, 5)
	assert(prediction.shape == Y.shape)
	
	MAE = np.abs(Y - prediction).mean()
	MAPE = np.abs((Y - prediction) / Y).mean()
	
	print("MAE:", MAE)
	print("MAPE:", MAPE)
	
