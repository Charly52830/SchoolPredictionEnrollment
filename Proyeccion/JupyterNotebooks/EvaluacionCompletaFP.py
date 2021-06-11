import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import numpy as np
import pandas as pd

# Importar métodos de predicción
from Metodos.NaiveForecasting import naive_forecasting_predict
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
PREDICTION_SIZE = 4

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
    test_result.Y = np.reshape(test_result.Y, (SCHOOLS, PREDICTION_SIZE)).T
    test_result.Y_hat = np.reshape(test_result.Y_hat, (SCHOOLS, PREDICTION_SIZE)).T
    return test_result

def run(validation_size) :
    nar = Model(individual_ann_predict, args = dict(window_len = 5, normalizators = [MinMaxNormalizator]))
    arima = Model(auto_arima_predict, args = dict(normalizators = [MinMaxNormalizator]))
    fts = Model(hyperopt_fts_predict, args = dict(normalizators = [MinMaxNormalizator]))

    nar.TEST_SIZE = 4
    arima.TEST_SIZE = 4
    fts.TEST_SIZE = 4
    nar.VALIDATION_SIZE = validation_size
    arima.VALIDATION_SIZE = validation_size
    fts.VALIDATION_SIZE = validation_size
    
    # Calcular predicciones con NAR
    result_nar = nar.test_set(
        dataset_name = DATASET_NAME,
        prediction_size = PREDICTION_SIZE,
        group_dataset = GROUP_DATASET_NAME
    )
    result_nar.Y = np.reshape(result_nar.Y, (SCHOOLS, PREDICTION_SIZE)).T
    result_nar.Y_hat = np.reshape(result_nar.Y_hat, (SCHOOLS, PREDICTION_SIZE)).T
    
    # Calcular predicciones con ARIMA
    result_arima = arima.test_set(
        dataset_name = DATASET_NAME,
        prediction_size = PREDICTION_SIZE,
        group_dataset = GROUP_DATASET_NAME
    )
    result_arima.Y = np.reshape(result_arima.Y, (SCHOOLS, PREDICTION_SIZE)).T
    result_arima.Y_hat = np.reshape(result_arima.Y_hat, (SCHOOLS, PREDICTION_SIZE)).T
    
    # Calcular predicciones con FTS
    result_fts = fts.test_set(
        dataset_name = DATASET_NAME,
        prediction_size = PREDICTION_SIZE,
        group_dataset = GROUP_DATASET_NAME
    )
    result_fts.Y = np.reshape(result_fts.Y, (SCHOOLS, PREDICTION_SIZE)).T
    result_fts.Y_hat = np.reshape(result_fts.Y_hat, (SCHOOLS, PREDICTION_SIZE)).T
    
    # Calcular predicciones ARIMA + NAR
    result_arima_nar = combine([result_arima, result_nar])
    
    # Calcular predicciones FTS + NAR
    result_fts_nar = combine([result_fts, result_nar])
    
    # Calcular predicciones FTS + ARIMA
    result_fts_arima = combine([result_fts, result_arima])
    
    # Calcular predicciones FTS + ARIMA + NAR
    result_fts_arima_nar = combine([result_fts, result_arima, result_nar])
    
    results = [
        ("NAR", result_nar.metricas),
        ("ARIMA", result_arima.metricas),
        ("ARIMA + NAR", result_arima_nar.metricas),
        ("FTS", result_fts.metricas),
        ("FTS + NAR", result_fts_nar.metricas),
        ("FTS + ARIMA", result_fts_arima.metricas),
        ("FTS + ARIMA + NAR", result_fts_arima_nar.metricas)
    ]
    
    return results

if __name__ == '__main__' :
    print("Corriendo algoritmos de prueba")
    resultados_prueba = run(4)
    
    print("Corriendo algoritmos de validacion")
    resultados_validacion = run(0)
    
    print("PRUEBA:")
    for nombre, resultado in resultados_prueba :
        print("Metricas %s" % (nombre), resultado, end = '\n\n')
        
    print("VALIDACION:")
    for nombre, resultado in resultados_validacion :
        print("Metricas %s" % (nombre), resultado, end = '\n\n')
