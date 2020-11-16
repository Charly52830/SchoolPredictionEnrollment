# Manejo de módulos
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import numpy as np
from pyFTS.partitioners import Grid, Entropy
from pyFTS.models import pwfts, chen, hofts
from pyFTS.common import Membership as mf

from Entrenamiento.Normalizators import MinMaxNormalizator, DummyNormalizator, DifferencingNormalizator

def fts_predict(data, prediction_size, normalizators = []) :
	# Aplicar las normalizaciones
	norms = []
	for i in range(len(normalizators)) :
		normalizator = normalizators[i](data)
		data = normalizator.normalize(data)
		norms.append(normalizator)
	
	# Crear partitioner
	# Definir el número de conjuntos fuzzy y la función de pertenencia
	partitioner = Grid.GridPartitioner(data = data, npart = 9, mf = mf.gaussmf)
	
	# Crear modelo
	model = hofts.WeightedHighOrderFTS(order = 3, partitioner = partitioner)
	
	# Entrenar modelo
	model.fit(data)
	
	# Realizar predicción
	prediction = model.predict(data, steps_ahead = prediction_size)
	
	# Aplicar las desnormalizaciones en el orden inverso
	for i in range(len(norms) - 1, -1, -1) :
		prediction = norms[i].denormalize(prediction)
	
	return prediction

def fts_predict(data, prediction_size, fuzy_sets, membership_func, order, model, partitioner) :
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
	
	# Realizar predicción
	prediction = model.predict(data, steps_ahead = prediction_size)
	
	return error, prediction

def hyperopt_fts_predict(data, prediction_size, normalizators = []) :
	# Aplicar las normalizaciones
	norms = []
	for i in range(len(normalizators)) :
		normalizator = normalizators[i](data)
		data = normalizator.normalize(data)
		norms.append(normalizator)
	
	# Hiperparámetros
	fuzy_sets = [10]
	membership_functions = [mf.gaussmf, mf.trimf]
	orders = [2, 3]
	models = [hofts.WeightedHighOrderFTS, pwfts.ProbabilisticWeightedFTS]
	partitioners = [Grid.GridPartitioner] # Intentar Entropy.EntropyPartitioner
	
	best_error = None
	best_prediction = None
	
	for fuzy_set in fuzy_sets :
		for membership_function in membership_functions :
			for order in orders :
				for model in models :
					for partitioner in partitioners :
						error, prediction = fts_predict(
							data, 
							prediction_size, 
							fuzy_set, 
							membership_function, 
							order, 
							model, 
							partitioner
						)
						if best_error is None or error < best_error :
							best_prediction = prediction
							best_error = error
	
	# Aplicar las desnormalizaciones en el orden inverso}
	prediction = np.array(best_prediction)
	for i in range(len(norms) - 1, -1, -1) :
		prediction = norms[i].denormalize(prediction)
	
	return prediction

if __name__ == '__main__' :
	escuela = np.array([377,388,392,394,408,405,426,403,414,412,424,438,429,443,429,430,428])
	prediction = hyperopt_fts_predict(
		data = escuela, 
		prediction_size = 5, 
		#normalizators = [MinMaxNormalizator]
	)
	print(prediction)
