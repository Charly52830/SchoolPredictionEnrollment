# Manejo de módulos
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import numpy as np
import pandas as pd
from Metodos.LinearRegression import linear_regression_predict

class TestResult :
    """Clase que contiene los resultados de las métricas de evaluación. La clase
    Model genera instancias de esta clase cada vez que se ejecuta una evaluación.
    """
    
    def __init__(self, prediction, Y) :
        """Constructor de la clase TestResult. Prepara los parámetros del resultado
        de la predicción para mostrar en Dash.
        
        Las métricas que calcula son las siguientes:
        - Mean absolute error
        - Mean absolute percentage error
        - Root mean squared error
        - Probabilidad de riesgo (ver notebook Evaluacion para más información)
        
        Args:
            prediction (:obj: `numpy.array`): numpy array con los datos de la
                predicción. Cada columna representa una escuela, cada fila
                representa un año.
            Y (:obj: `numpy.array`): numpy array con los datos reales. Cada 
                columna representa una escuela, cada fila representa un año.
        """
        
        # Nota importante (25/07/2020)
        # La métrica de probabilidad de riesgo aún no está implementada

        self.metricas = []
        for i in range(prediction.shape[0]) :
            tmp_pred = prediction[i]
            tmp_Y = Y[i]

            # Mean absolute error
            mae = np.abs(tmp_pred - tmp_Y).mean()

            # Root mean squared error
            rmse = np.sqrt(np.square(tmp_pred - tmp_Y).mean())

            # Mean absolute percentage error
            mape = np.abs((tmp_pred - tmp_Y) / tmp_Y).mean()
            
            # TO DO: agregar cálculo de probabilidad de riesgo
            
            self.metricas.append((mae, rmse, mape))
        
        m = Y.shape[0] * Y.shape[1]
        self.Y_hat = np.reshape(prediction.T, m)
        self.Y = np.reshape(Y.T, m)

class Model :
    """Clase Modelo que sirve como interfaz para la predicción de distintos
    métodos que tiene la capacidad de guardar en memoria los conjuntos
    que ya calculó previamente.
    """
    
    def __init__(self, function, args = dict()) :
        """Constructor de la clase Model.
        
        Args:
            function (python function): función de python que predice una serie 
                de tiempo utilizando un método específico. Las funciones se 
                encuentran en el directorio Metodos.
            args (:obj: `dict`): parámetro opcional para los modelos que 
                utilicen parámetros extra aparte de los datos y el tamaño de 
                predicción.
        """
        
        self.model_function = function
        self.args = args
        
        self.cached_sets = dict()
        
        # Número máximo de años de predicción
        self.TEST_SIZE = 5
    
    def predict(self, data, prediction_size) :
        """Método que realiza una predicción sobre una observación de datos.
        
        Args:
            data (:obj: `numpy.array`): numpy array con los valores de la serie 
                de tiempo. Debe contener únicamente una observación.
            prediction_size (int): número de valores o años que se quiere predecir.
        
        Returns:
             (:obj: `numpy.array`): numpy array con los valores de la predicción.
        """
        
        self.args['prediction_size'] = prediction_size
        self.args['data'] = data
        
        return self.model_function(**self.args)
    
    def test_set(self, dataset_name, prediction_size) :
        """Método que evalúa un conjunto de datos con el modelo que guarda
        esta clase.
        
        Args:
            dataset_name (str): nombre del conjunto a evaluar. Los conjuntos de
                datos se encuentran en el directorio Datasets con extensión .csv.
            prediction_size (int): número de años a predecir.
        
        Returns:
            (:obj: `TestResult`): instancia de la clase TestResult con los 
                resultados de la evaluación.
        """
        
        assert(prediction_size <= self.TEST_SIZE)
        
        key = '%s_%d' % (dataset_name, prediction_size)
        
        if key not in self.cached_sets :

            dataset = pd.read_csv(os.path.join(
				os.path.dirname(__file__), 
				os.pardir, 
				'Datasets/', 
				dataset_name + '.csv'
			))
            dataset = dataset.drop('cct', 1)

            #m = prediction_size * dataset.shape[0]  # Número total de predicciones
            prediction_data = np.zeros((prediction_size, dataset.shape[0])) # Ŷ
            real_data = np.zeros((prediction_size, dataset.shape[0])) # Y

            for i in range(dataset.shape[0]) :
                row = np.array(dataset.loc[i])
                
                # Separamos los últimos 5 años
                X = row[: -self.TEST_SIZE]
                
                if prediction_size == self.TEST_SIZE :
                    Y = row[-self.TEST_SIZE :]
                else :
                    Y = row[-self.TEST_SIZE : -(self.TEST_SIZE - prediction_size)]

                prediction_data[:, i] = self.predict(X, prediction_size)
                real_data[:, i] = Y
                
            self.cached_sets[key] = TestResult(prediction_data, real_data)
        return self.cached_sets[key]

if __name__ == '__main__' :
    # Aquí van las pruebas
	pass
