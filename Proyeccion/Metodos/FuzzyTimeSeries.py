# Manejo de módulos
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import numpy as np
from pyFTS.partitioners import Grid, Entropy
from pyFTS.models import pwfts, chen, hofts
from pyFTS.common import Membership as mf
from Metodos.Normalizators import MinMaxNormalizator

def fts_train(data, fuzy_sets, membership_func, order, model, partitioner) :
	"""Función para entrenar un modelo FTS dados los hiperparámetros del modelo.
	
	Para más información acerca de los términos ver:
	https://towardsdatascience.com/a-short-tutorial-on-fuzzy-time-series-dcc6d4eb1b15
	
	Args:
		data (:obj: `numpy.array`): numpy array de una dimensión que contiene
			los datos de entrenamiento de la serie de tiempo.
		fuzy_sets(int): número de conjuntos (o términos lingüisticos) de los que 
			se compondrá la variable lingüistica.
		membership_func(:obj: `Membership.function`): función de pertenencia del 
			modelo.
		order(int): número de lags para considerar en la autoregresión.
		model(:obj: `pyFTS.Models`): modelo FTS a utilizar.
		partitioner(:obj: `pyFTS.partitioners`): tipo de particionador a utilizar.
	
	Returns:
		error(float): MAPE del modelo FTS construido al predecir los datos de
			entrenamiento.
		prediction(:obj: `numpy.array`): arreglo numpy con los datos de la predicción
			de los años futuros (no de los datos de entrenamiento) con forma 
			(prediction__size,).
	"""
	assert(len(data) > 5)
	# Crear partitioner
	partitioner = partitioner(data = data, npart = fuzy_sets, mf = membership_func)
	
	# Crear modelo
	model = model(order = order, partitioner = partitioner)
	
	# Entrenar modelo
	model.fit(data)
	
	# Encontrar error histórico
	y_hat = []
	for i in range(5, len(data)) :
		prediction = model.predict(data[:i], steps_ahead = 1)
		y_hat.append(prediction[0])
	
	y_hat = np.array(y_hat)
	y = data[5:]
	
	# Calcular MAPE
	error = np.abs((y_hat - y) / y).mean()
	
	return error, model

def train_hyperopt_fts(data) :
	"""
	"""
	# Hiperparámetros
	# TODO: conforme se agreguen más datos a la base de datos el número de fuzy 
	# sets se tendrá que calibrar. (Para 16/11/2020) el óptimo es 10.
	fuzy_sets = [10]
	membership_functions = [mf.gaussmf, mf.trimf]
	orders = [2, 3]
	models = [hofts.WeightedHighOrderFTS, pwfts.ProbabilisticWeightedFTS]
	# TODO: Intentar Entropy.EntropyPartitioner como particionador
	partitioners = [Grid.GridPartitioner] 
	
	best_error = None
	best_model = None
	
	# Grid search
	for fuzy_set in fuzy_sets :
		for membership_function in membership_functions :
			for order in orders :
				for model in models :
					for partitioner in partitioners :
						error, model = fts_train(
							data, 
							fuzy_set, 
							membership_function, 
							order, 
							model, 
							partitioner
						)
						if best_error is None or error < best_error :
							best_error = error
							best_model = model
	
	return best_model

def hyperopt_fts_predict(data, prediction_size, normalizators = []) :
	"""Función que implementa Grid Search para optimizar los parámetros de un
	modelo Fuzzy. Encuentra los mejores parámetros para los datos dados y 
	devuelve la predicción. El error se calcula encontrando el MAPE de los datos 
	de entrenamiento utilizando el modelo FTS con la configuración dada.
	
	Args:
		data (:obj: `numpy.array`): numpy array de una dimensión que contiene
			los datos de entrenamiento de la serie de tiempo.
		prediction_size (int): número de años a predecir.
		normalizators (:list: `Normalizator`): lista de objetos Normalizator. Las 
			normalizaciones se aplican en el orden en el que se encuentran en la 
			lista y se encuentran en el directorio Metodos/Normalizators.
	
	Returns:
		(:obj: `numpy.array`): arreglo numpy con los datos de la predicción 
			con forma (prediction__size,)
	"""
	# Aplicar las normalizaciones
	norms = []
	for i in range(len(normalizators)) :
		normalizator = normalizators[i](data)
		data = normalizator.normalize(data)
		norms.append(normalizator)
	
	# Entrenar el modelo
	model = train_hyperopt_fts(data)
	
	# Obtener predicción
	prediction = model.predict(data, steps_ahead = prediction_size)
	prediction = np.array(prediction)
	
	# Aplicar las desnormalizaciones en el orden inverso
	for i in range(len(norms) - 1, -1, -1) :
		prediction = norms[i].denormalize(prediction)
	
	return prediction

def evaluate_and_predict_fts(data, prediction_size = 5, normalizators = [MinMaxNormalizator]) :
	"""
	"""
	assert(len(data) > 5)
	# Aplicar las normalizaciones
	norms = []
	for i in range(len(normalizators)) :
		normalizator = normalizators[i](data)
		data = normalizator.normalize(data)
		norms.append(normalizator)
	
	# Entrenar el modelo
	model = train_hyperopt_fts(data)
	
	# Obtener predicción futura
	prediction = np.array(model.predict(data, steps_ahead = prediction_size))
	
	# Obtener la predicción del conjunto de los datos de entrenamiento
	train_prediction = []
	for i in range(5, len(data)) :
		next = model.predict(data[:i], steps_ahead = 1)
		train_prediction.append(next[0])
	
	train_prediction = np.array(train_prediction)
	
	# Aplicar las desnormalizaciones en el orden inverso
	for i in range(len(norms) - 1, -1, -1) :
		train_prediction = norms[i].denormalize(train_prediction)
		prediction = norms[i].denormalize(prediction)
	
	return prediction, train_prediction

if __name__ == '__main__' :
	escuela = np.array([89,127,134,152,170,172,182,192,197,210,219,222,233,226,222,205,222])
	prediccion = hyperopt_fts_predict(
	    data = escuela,
	    prediction_size = 5,
	    normalizators = [MinMaxNormalizator]
	)
	print(prediccion)
