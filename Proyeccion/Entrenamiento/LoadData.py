# Manejo de módulos
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import numpy as np
import pandas as pd
import random

def loadData(dataset_name, window_len, test_size, Y_size, drop_columns = 0, shuffle_data = True) :
	"""Función que carga los datos de un dataset y los prepara para ser 
	procesados por una red neuronal.
	
	Args:
		dataset_name (str): nombre del dataset.
		window_len (int): longitud de los vectores de entrada de la red neuronal
			(que también representa el número de años que se toman para la predicción).
		test_size (int): número de años que forman parte del conjunto de prueba. Por 
			regla de negocio este valor debe ser de 5 años.
		Y_size (int): número de años que va a predecir la red neuronal.
		drop_columns (int, optional): número de años a partir de 1998 que se 
			descartarán. El valor por defecto es cero.
		suffle_data (boolean, optional): si es True las observaciones se ordenarán
			aleatoriamente, si es False no lo harán. El valor por defecto es True.
			Se utiliza 0 como semilla.
		
	Returns:
		x_train (:obj: `numpy.array`): matriz de dimensiones (window_len, m) que 
			contiene los los vectores de entrada para entrenar la red neuronal.
		y_train (:obj: `numpy.array`): matriz de dimensiones (Y_size, m) que
			contiene los datos a predecir para cada observación en en el conjunto
			de entrenamiento.
		x_test (:obj: `numpy.array`): matriz de dimensiones (window_len, m_test) que 
			contiene los los vectores de entrada para probar la red neuronal.
		y_test (:obj: `numpy.array`): matriz de dimensiones (Y_size, m_test) que
			contiene los datos a predecir para cada observación en en el conjunto
			de prueba.
	"""

	dataset = pd.read_csv(os.path.join(
		os.path.dirname(__file__), 
		os.pardir, 
		'Datasets/', 
		dataset_name + '.csv'
	))
	dataset = dataset.drop('cct', 1)
	
	first_year = 1998
	for i in range(drop_columns) :
		dataset = dataset.drop(str(first_year + i), 1)
	
	assert(window_len + Y_size + test_size <= dataset.shape[1])
	#assert(Y_size <= test_size)
	
	m = dataset.shape[0] * (dataset.shape[1] - test_size - Y_size - window_len + 1)
	m_test = dataset.shape[0] * test_size
	
	index = [i for i in range(m)]
	if shuffle_data :
		# Apply random shuffle to index
		random.seed(0)
		random.shuffle(index)
	
	x_train = np.zeros((window_len, m))
	y_train = np.zeros((Y_size, m))
	x_test = np.zeros((window_len, m_test))
	y_test = np.zeros((Y_size, m_test))
	
	m_count = 0
	m_test_count = 0
	
	print("Total de observaciones de entrenamiento: %d" % (m))
	print("Total de observaciones de prueba: %d" % (m_test))
	
	for i in range(dataset.shape[0]) :
		row = np.array(dataset.loc[i])
		for j in range(window_len, dataset.shape[1] - Y_size + 1) :
			if j < dataset.shape[1] - test_size - Y_size + 1:
				# Train dataset
				x_train[:, index[m_count]] = row[j - window_len : j]
				y_train[:, index[m_count]] = row[j : j + Y_size]
				m_count += 1
				
			else :
				# Test dataset
				x_test[:, m_test_count] = row[j - window_len : j]
				y_test[:, m_test_count] = row[j : j + Y_size]
				m_test_count += 1
		
	assert(m_count == m)
	assert(m_test_count == m_test)
	
	print('Dataset %s cargado para la red neuronal' % (dataset_name + '.csv'))
	return (x_train, y_train, x_test, y_test)
	
if __name__ == '__main__' :
	# Aquí van las pruebas
	pass
