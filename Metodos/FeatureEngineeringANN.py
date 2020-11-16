# Manejo de módulos
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import tensorflow as tf
import numpy as np
import pandas as pd
from tsfresh import extract_features, select_features
from tsfresh.utilities.dataframe_functions import impute, roll_time_series, make_forecasting_frame
from Entrenamiento.Normalizators import MinMaxNormalizator, DummyNormalizator, DifferencingNormalizator

def prepare_fe_data(x, y) :
	_id = []
	time = []
	serie = []
	
	for i in range(x.shape[0]) :
		for j in range(x.shape[1]) :
			_id.append(i)
			time.append(j)
			serie.append(x[i][j])
	
	x_df = pd.DataFrame({
		'id' : _id,
		'time' : time,
		'x' : serie
	})
	
	y_df = pd.core.series.Series(y)
	
	extracted_features = extract_features(x_df, column_id="id", column_sort="time")
	impute(extracted_features)
	features_filtered = select_features(extracted_features, y_df)
	return features_filtered

def load_data(data, window_len) :
	x = np.zeros((len(data) - window_len, window_len))
	y = np.zeros((len(data) - window_len))
	for i in range(len(data) - window_len) :
		x[i] = data[i: i + window_len]
		y[i] = data[i + window_len]
		
	return x, y

def fe_ann_predict(data, prediction_size, window_len, normalizators = []) :	
	# Aplicar las normalizaciones
	norms = []
	for i in range(len(normalizators)) :
		normalizator = normalizators[i](data)
		data = normalizator.normalize(data)
		norms.append(normalizator)
	
	# Create windows
	x, y = load_data(data, window_len)
	print(x)
	print(prepare_fe_data(x, y))
	
	# Transform into a dataframe for applying feature engineering

if __name__ == '__main__' :
	escuela = np.array([73,76,74,66,62,58,54,62,105,107,116,125,134,151,137,144,141,146,140,160,162,138])
	"""
	#series = pd.core.series.Series(escuela)
	fe_ann_predict(escuela, 5, 10)
	"""
	
	df, targets = make_forecasting_frame(
		x = escuela,
		kind = "matricula",
		rolling_direction = 1,
		max_timeshift = None
	)
	
	df_features = extract_features(
		df, 
		column_id="id", 
		column_sort="time", 
		column_value = "value", 
		column_kind = "kind"
	)
	
	_targets = np.array([76,74,66,62,58,54,62,105,107,116,125,134,151,137,144,141,146,140,160,162,138])
	
	#df_features.index = targets.index
	targets.index = df_features.index
	
	impute(df_features)
	features_filtered = select_features(
		df_features, 
		targets
	)
	
	print(features_filtered)
	
