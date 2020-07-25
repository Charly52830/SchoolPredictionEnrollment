# Manejo de módulos
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import numpy as np
import json
import csv
import pandas as pd
from Metodos.LinearRegression import linear_regression_predict

def find_dataset(dataset_name, extension = '.csv') :
	"""Función de utilidad para encontrar un archivo en el directorio Datasets.
	
	Args:
		dataset_name (str): nombre del archivo.
		extension (str, optional): extensión del archivo, por defecto es .csv.
	
	Returns:
		str: ubicación del archivo en el directorio Datasets.
	"""
	
	return os.path.join(
		os.path.dirname(__file__), 
		os.pardir, 
		'Datasets/', 
		dataset_name + extension
	)

def crearCSV(dataset_name) :
	"""Función que crea un archivo csv con los datos de las escuelas, a partir
	de un archivo json.
	
	Args:
		dataset_name (str): el nombre del archivo json guardado en el directorio Datasets.
	"""
	
	# Nota importante (08/05/2020) :
	# Se excluyen los datos de 1996 a 1997 porque no son legítimos
	
	# Nota importante (18/07/2020) :
	# Debido a que los datos del 2010 de primaria están perdidos, se predice el 
	# dato con regresión linear + fixed partitioning
	
	# Opening JSON file 
	f = open(find_dataset(dataset_name, '.json'))
	  
	# returns JSON object as  a dictionary
	data = json.load(f) 
	results = data['result'][0]

	# Closing file 
	f.close() 

	# Borrar registros que no son escuelas
	results.pop('@type')
	results.pop('@version')

	num_anios = int(input("Ingresa el número de años\n"))	# 22 hasta el 2019
	
	with open(find_dataset(dataset_name), mode = 'w') as archivo :
		writer = csv.writer(archivo, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(["cct"] + [1998 + i for i in range(num_anios)])
		for cct_escuela in results :
			escuela = results[cct_escuela]
			
			alumnos = np.zeros(num_anios, dtype = int)
			for i in range(num_anios) :
				anio = 1998 + i
				if anio == 2010 :
					alumnos[i] = linear_regression_predict(alumnos[:12], 1)[0]
				elif str(anio) in escuela :
					alumnos[i] = int(escuela[str(anio)])
			
			writer.writerow(np.append(np.array([cct_escuela]), alumnos))
	
	print("Archivo guardado como %s en el directorio Datasets" % (dataset_name + '.csv'))

def cleanData(dataset_name) :
	"""Función que elimina los registros con muchos ceros y con números negativos.
	Crea un nuevo archivo csv con los datos limpios con el prefijo Clean en el
	nombre del archivo.
	
	Args:
		dataset_name (str): nombre del dataset.
	"""
	dataset = pd.read_csv(find_dataset(dataset_name))
	num_anios = dataset.shape[1] - 1
	remove_counter = 0
	
	with open(find_dataset('Clean' + dataset_name), mode = 'w') as archivo :
		writer = csv.writer(archivo, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(["cct"] + [1998 + i for i in range(num_anios)])
		
		for i in range(dataset.shape[0]) :
			row = np.array(dataset.loc[i])
			cct = row[0]
			row = row[1:]
			zero_index = np.where(row == 0)[0]
			
			if len(zero_index) == 1 :
				zero_index = zero_index[0]
				if zero_index >= 5 :
					# Al menos cinco años para predecir
					row[zero_index] = int(linear_regression_predict(row[:zero_index], 1)[0])
			
			if not np.any(row <= 0) :
				writer.writerow(np.concatenate((np.array([cct]), row)))
			else :
				remove_counter += 1
	
	print("Dataset limpiado. Archivo %s guardado en el directorio Datasets" % ('Clean' + dataset_name + '.csv'))
	print("Registros eliminados: %d" % (remove_counter))
	print("Registros totales finales: %d" % (dataset.shape[0] - remove_counter))

def sortData(csv_file, save_as, reverse = False) :
	dataset = pd.read_csv(csv_file)
	n = dataset.shape[0]
	num_anios = dataset.shape[1] - 1
	assert(num_anios == 22)
	
	index_list = []
	for i in range(n) :
		index_list.append((np.array(dataset.loc[i][1:], dtype = float).mean(), i))
	
	index_list.sort(reverse = reverse)
	
	with open(save_as + '.csv', mode='w') as archivo :
		writer = csv.writer(archivo, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(["cct"] + [1998 + i for i in range(num_anios)])
		
		for i in range(n) :
			writer.writerow(np.array(dataset.loc[index_list[i][1]]))
	
	print('Archivo guardado como', save_as + '.csv')

def filterData(csv_file, save_as, custom_function) :
	dataset = pd.read_csv(csv_file)
	n = dataset.shape[0]
	num_anios = dataset.shape[1] - 1
	
	with open(save_as + '.csv', mode='w') as archivo :
		writer = csv.writer(archivo, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(["cct"] + [1998 + i for i in range(num_anios)])
		
		for i in range(n) :
			if custom_function(np.array(dataset.loc[i][1:])) :
				writer.writerow(np.array(dataset.loc[i]))
			
	print('Archivo guardado como', save_as + '.csv')
	
if __name__ == '__main__' :
	crearCSV('PrimariasPublicas')
	cleanData('PrimariasPublicas')

