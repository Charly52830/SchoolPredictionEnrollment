# Manejo de módulos
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import numpy as np
import pandas as pd
from Metodos.LinearRegression import linear_regression_predict, base_linear_regression
from Metodos.AutoRegression import ar_predict
from Metodos.AutoARIMA import auto_arima_predict
from Metodos.IndividualANN import individual_ann 
from Entrenamiento.Normalizators import MinMaxNormalizator, DummyNormalizator, DifferencingNormalizator

class TestResult :
    """Clase que contiene los resultados de las métricas de evaluación. La clase
    Model genera instancias de esta clase cada vez que se ejecuta una evaluación.
    """
    
    def __init__(self, prediction, Y, groups) :
        """Constructor de la clase TestResult. Prepara los parámetros del resultado
        de la predicción para mostrar en Jupyter.
        
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
            groups (:obj: `numpy.array`): numpy array con los datos de los grupos. 
                Cada columna representa una escuela, cada fila representa un año.
                Este parámetro es utilizado para el cálculo de la Probabilidad de
                riesgo.
        """
        
        self.metricas = []
        for i in range(prediction.shape[0]) :
            tmp_pred = prediction[i]
            tmp_Y = Y[i]
            tmp_group = groups[i]

            # Mean absolute error
            mae = np.abs(tmp_pred - tmp_Y).mean()

            # Root mean squared error
            rmse = np.sqrt(np.square(tmp_pred - tmp_Y).mean())

            # Mean absolute percentage error
            mape = np.abs((tmp_pred - tmp_Y) / tmp_Y).mean()
            
            # Probabilidad de riesgo
            # Alternativa A de la Probabilidad de riesgo
            #pr = (np.abs(np.abs(tmp_pred - tmp_Y)) >= tmp_Y / tmp_group).mean()
            
            # Alternativa B de la probabilidad de riesgo
            pr = (np.abs(tmp_pred - tmp_Y) >= tmp_group).mean()
            
            self.metricas.append((mae, rmse, mape, pr))
        
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
       
    def test_set(self, dataset_name, prediction_size, group_dataset) :
        """Método que evalúa un conjunto de datos con el modelo que guarda
        esta clase.
        
        Args:
            dataset_name (str): nombre del conjunto a evaluar. Los conjuntos de
                datos se encuentran en el directorio Datasets con extensión .csv.
            prediction_size (int): número de años a predecir.
            group_dataset (str): nombre del dataset que contiene el número de grupos
                para cada cct del dataset a evaluar.
        
        Returns:
            (:obj: `TestResult`): instancia de la clase TestResult con los 
                resultados de la evaluación.
        """
        assert(prediction_size <= self.TEST_SIZE)
        
        key = '%s_%d' % (dataset_name, prediction_size)
        if key not in self.cached_sets :
            # Cargar dataset en memoria
            dataset = pd.read_csv(os.path.join(
                os.path.dirname(__file__), 
                os.pardir, 
                'Datasets/', 
                dataset_name + '.csv'
            ))
            
            # Cargar dataset de grupos en memoria
            grupos = pd.read_csv(os.path.join(
                os.path.dirname(__file__),
                os.pardir,
                'Datasets/',
                group_dataset + '.csv'
            ))
            # Objeto para buscar ccts en el dataset de grupos
            unique_index = pd.Index(list(grupos['cct']))
            
            num_escuelas = dataset.shape[0]
            # Número de observaciones a evaluar por cada escuela
            observaciones_escuela = (1 + self.TEST_SIZE - prediction_size)
            # Número total de observaciones a evaluar
            m = num_escuelas * observaciones_escuela
            
            # Predicciones
            Y_hat = np.zeros((prediction_size, m))
            # Datos reales
            Y = np.zeros((prediction_size, m))
            # Grupos (para métrica de probabilidad de riesgo)
            group_data = np.zeros((prediction_size, m))
            
            # Indica la columna en la que se colocará la observación
            ob_index = 0
            for i in range(num_escuelas) :
                # Escuela
                row = np.array(dataset.loc[i])
                cct = row[0]
                row = row[1:]
                
                # Encontrar el promedio de (la taza de alumnos por grupo en cada año)
                if cct in unique_index :
                    index = unique_index.get_loc(cct)
                    # Número de grupos en cada año
                    grupos_escuela = np.array(grupos.loc[index][1:])
                    # Número real de alumnos en cada año
                    alumnos = np.array(dataset.loc[i])[1:]
                    
                    # Broadcasting del promedio del promedio de alumnos por grupo
                    group_val = (alumnos[:-self.TEST_SIZE] / grupos_escuela[:-self.TEST_SIZE]).mean()
                    
                else :
                    # Broadcasting de infinito
                    group_val = 1e9
                
                for j in range(observaciones_escuela) :
                    # Datos históricos de la observación
                    ob_X = row[: -(self.TEST_SIZE - j)]
                    # Datos a predecir de la observación
                    if prediction_size + j == self.TEST_SIZE :
                        ob_Y = row[-self.TEST_SIZE + j:]
                    else :
                        ob_Y = row[-self.TEST_SIZE + j: -(self.TEST_SIZE - prediction_size) + j]
                    # Predicción de los datos
                    ob_Y_hat = self.predict(ob_X, prediction_size)
                    
                    Y_hat[:, ob_index] = ob_Y_hat
                    Y[:, ob_index] = ob_Y
                    group_data[:, ob_index] = group_val
                    
                    ob_index += 1
                print("Escuela %d de %d terminada" % (i + 1, num_escuelas))
            self.cached_sets[key] = TestResult(Y_hat, Y, group_data)
        
        return self.cached_sets[key]

if __name__ == '__main__' :
	#m = Model(base_linear_regression)
	#m = Model(AR_predict, {'normalizators' : []})
	#m = Model(auto_arima_predict, {'normalizators' : [MinMaxNormalizator]})
	m = Model(individual_ann, {'window_len' : 5, 'normalizators' : [MinMaxNormalizator]})
	test_result = m.test_set(
		dataset_name = 'DummySet',
		prediction_size = 1,
		group_dataset = 'GruposPrimaria'
	)
	mae, rmse, mape, rp = test_result.metricas[-1]
	print("MAE: %.3lf" % (mae))
	print("RMSE: %.3lf" % (rmse))
	print("MAPE: %.3lf" % (mape))
	print("RP: %.3lf" % (rp))
	
