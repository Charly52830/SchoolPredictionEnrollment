# Manejo de módulos
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import numpy as np
from statsmodels.tsa.ar_model import AR
from Entrenamiento.Normalizators import MinMaxNormalizator, DummyNormalizator, DifferencingNormalizator

def ar_predict(data, prediction_size, normalizators = []) :
	"""Método de predicción que aplica un modelo auto regresivo.
	
	Args:
		data (:obj: `numpy.array`): numpy array con los valores reales de la
			observación.
		prediction_size (int): número de años a predecir.
		normalizators (:list: `Normalizator`): lista de objetos Normalizator. Las 
			normalizaciones se aplican en el orden en el que se encuentran en la 
			lista y se encuentran en el directorio Entrenamiento/Normalizators.
	
	Returns:
		(:obj: `numpy.array`): numpy array con los valores de la predicción.
	"""
	# Aplicar las normalizaciones
	norms = []
	for i in range(len(normalizators)) :
		normalizator = normalizators[i](data)
		data = normalizator.normalize(data)
		norms.append(normalizator)

	model = AR(data).fit()
		
	prediction = model.predict(
		start = len(data), 
		end = len(data) + prediction_size - 1 , 
		dynamic = True
	)
	
	# Aplicar las desnormalizaciones en el orden inverso
	for i in range(len(norms) - 1, -1, -1) :
		prediction = norms[i].denormalize(prediction)
	return prediction

if __name__ == '__main__' :
	escuela = np.array([89,127,134,152,170,172,182,192,197,210,219,222,232,226,222,205,222])
	prediction = AR_predict(escuela, 5, [MinMaxNormalizator, DifferencingNormalizator])
	print(prediction)
