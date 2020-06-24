import tensorflow as tf
import numpy as np
import pandas as pd
from tensorflow.keras.models import model_from_json
from LoadData import loadData

def create_model(window_size, csv_file, test_size, Y_size = 1, model_name = 'default') :
	
	x_train, y_train, x_test, y_test = loadData(csv_file, window_size, test_size, Y_size, drop_columns = 0)
	print(x_train.shape, y_train.shape)
	print(x_test.shape, y_test.shape)
	
	assert(x_train.shape[0] == window_size)
	
	tf.random.set_seed(0)
	
	model = tf.keras.models.Sequential([
		tf.keras.layers.Dense(60, input_shape = [window_size], activation = "relu"),
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
		batch_size = 5,
		verbose = 1,
		callbacks = [lr_schedule],
		#validation_data = (x_test.T, y_test.T)
	)
	
	prediction = model.predict(x_test.T)
	assert(prediction.shape == y_test.T.shape)
	MAE = np.abs(prediction - y_test.T).mean()
	print("MAE: ", MAE)
	MAPE = np.abs((prediction - y_test.T) / y_test.T ).mean()
	print("MAPE: ", MAPE)
	
	# Save model
	# serialize model to JSON
	model_json = model.to_json()
	with open(model_name + '.json', "w") as json_file:
		json_file.write(model_json)
	model.save_weights(model_name + ".h5")
	print("Saved model to disk as %s" % (model_name))
	
def load_model(model_name = 'default') :
	# load json and create model
	json_file = open(model_name + '.json', 'r')
	loaded_model_json = json_file.read()
	json_file.close()
	loaded_model = model_from_json(loaded_model_json)
	# load weights into new model
	loaded_model.load_weights(model_name + ".h5")
	
	print('Loaded model ', model_name)
	return loaded_model

def dnn_predict(data, prediction_size, cached_model = None) :
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
	model = None
	if cached_model == None :
		model = load_model('default' + str(prediction_size))
	else :
		model = cached_model
	
	window_len = model.layers[0].input_shape[1]
	X = np.zeros((1, window_len))
	X[0] = data[-window_len:]
	assert(X.shape == (1, window_len))
	
	prediction = model.predict(X)
	return prediction[0]

if __name__ == "__main__" :
	create_model(
		window_size = 7,
		csv_file = 'PrimariasCompletas.csv', 
		test_size = 5,
		Y_size = 5,
		model_name = 'default5'
	)
	#create_model(5, 'PrimariasPublicas.csv', 3, 1, 'publicas2')
	#escuela = np.array([106,90,91,89,74,68,66,60,57,42,38,39,30,40,41,34,33,23,23,20,14])
	#print(dnn_predict(escuela, 1, load_model('privadas')))
	
