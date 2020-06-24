import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def linear_regression(Y, window_len, prediction_size) :
	assert(len(Y) >= window_len)
	prediction = np.concatenate((Y, np.zeros(prediction_size)), axis = 0)
	X_train = np.array([i for i in range(1, window_len + 1)]).reshape((-1, 1))
	X_pred = np.array([i for i in range(1, window_len + 2)]).reshape((-1, 1))
	
	for j in range(prediction_size) :
		model = LinearRegression().fit(X_train, prediction[-(window_len + prediction_size - j) : -(prediction_size - j)])
		y_pred = model.predict(X_pred)
		prediction[len(Y) + j] = y_pred[-1]
	
	return prediction[-prediction_size :]

def best_prediction(X, Y, verbose = False) :
	validation_size = len(Y)
	train_size = len(X)
	best_window = 2
	best_error = 1000000
	
	for window_len in range(2, train_size) :
		prediction = linear_regression(
			Y = X,
			window_len = window_len,
			prediction_size = validation_size
		)
		assert(prediction.shape == Y.shape)
		MAE = np.abs(prediction - Y).mean()	# Mean Absolute Error
		
		if verbose :
			print("WINDOW_LEN:", window_len, "MAE:", MAE)
		
		if MAE < best_error :
			best_error = MAE
			best_window = window_len
	
	return best_window

def linear_regression_predict(data, prediction_size, validation_size = 1, verbose = False) :
	x_train = data[: -validation_size]
	x_validation = data[-validation_size :]
	
	window_len = best_prediction(
		X = x_train,
		Y = x_validation,
		verbose = verbose
	)
	
	return linear_regression(data, window_len, prediction_size)

if __name__ == '__main__' :
	#print(linear_regression_prediction(np.array([89,127,134,152,170,172,182,192,197,210,219,222,232,226,222,205]), 3, 1, True))
	main('PrimariasCompletas.csv', 1, 3)
	
