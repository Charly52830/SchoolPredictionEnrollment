import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import numpy as np
import pandas as pd

# Importar métodos de predicción
from Metodos.AutoARIMA import auto_arima_predict
from Metodos.IndividualANN import individual_ann_predict
from Metodos.FuzzyTimeSeries import hyperopt_fts_predict

# Importar Normalizadores
from Metodos.Normalizators import MinMaxNormalizator, DummyNormalizator, DifferencingNormalizator

# Importar interface de Modelos
from Evaluation import Model, TestResult

DATASET_NAME = 'TodasLasEscuelas'
GROUP_DATASET_NAME = 'TodosLosGrupos'
SCHOOLS = 3011

def combine(results) :
    assert(len(results))
    Y = None
    Y_hat = None
    groups = None
    
    for test_result in results :
        if Y is None :
            Y = test_result.Y
            Y_hat = test_result.Y_hat
            groups = test_result.groups
        else :
            Y_hat = Y_hat + test_result.Y_hat
    
    experts = len(results)
    Y_hat /= experts
    
    test_result = TestResult(Y_hat, Y, groups)
    test_result.Y = np.reshape(test_result.Y, (SCHOOLS, 5)).T
    test_result.Y_hat = np.reshape(test_result.Y_hat, (SCHOOLS, 5)).T
    return test_result

if __name__ == '__main__' :
    nar = Model(individual_ann_predict, args = dict(window_len = 5, normalizators = [MinMaxNormalizator]))
    arima = Model(auto_arima_predict, args = dict(normalizators = [MinMaxNormalizator]))
    fts = Model(hyperopt_fts_predict, args = dict(normalizators = [MinMaxNormalizator]))
    
    # Calcular predicciones con NAR
    result_nar = nar.test_set(
        dataset_name = DATASET_NAME,
        prediction_size = 5,
        group_dataset = GROUP_DATASET_NAME
    )
    result_nar.Y = np.reshape(result_nar.Y, (SCHOOLS, 5)).T
    result_nar.Y_hat = np.reshape(result_nar.Y_hat, (SCHOOLS, 5)).T
    
    # Calcular predicciones con ARIMA
    result_arima = arima.test_set(
        dataset_name = DATASET_NAME,
        prediction_size = 5,
        group_dataset = GROUP_DATASET_NAME
    )
    result_arima.Y = np.reshape(result_arima.Y, (SCHOOLS, 5)).T
    result_arima.Y_hat = np.reshape(result_arima.Y_hat, (SCHOOLS, 5)).T
    
    # Calcular predicciones con FTS
    result_fts = fts.test_set(
        dataset_name = DATASET_NAME,
        prediction_size = 5,
        group_dataset = GROUP_DATASET_NAME
    )
    result_fts.Y = np.reshape(result_fts.Y, (SCHOOLS, 5)).T
    result_fts.Y_hat = np.reshape(result_fts.Y_hat, (SCHOOLS, 5)).T
    
    # Calcular predicciones ARIMA + NAR
    result_arima_nar = combine([result_arima, result_nar])
    
    # Calcular predicciones FTS + NAR
    result_fts_nar = combine([result_fts, result_nar])
    
    # Calcular predicciones FTS + ARIMA
    result_fts_arima = combine([result_fts, result_arima])
    
    # Calcular predicciones FTS + ARIMA + NAR
    result_fts_arima_nar = combine([result_fts, result_arima, result_nar])
    
    print("Metricas NAR", result_nar.metricas, end = '\n\n')
    print("Metricas ARIMA", result_arima.metricas, end = '\n\n')
    print("Metricas ARIMA + NAR", result_arima_nar.metricas, end = '\n\n')
    print("Metricas FTS", result_fts.metricas, end = '\n\n')
    print("Metricas FTS + NAR", result_fts_nar.metricas, end = '\n\n')
    print("Metricas FTS + ARIMA", result_fts_arima.metricas, end = '\n\n')
    print("Metricas FTS + ARIMA + NAR", result_fts_arima_nar.metricas, end = '\n\n')
