import numpy as np
import pandas as pd

from TimeSeriesPrediction import fixed_partitioning_predict
from MyUtilities import LoadHTMLTable

class TestResult :
    
    def __init__(self, prediction, Y) :
        """
        Constructor de la clase TestResult. Prepara los parámetros del resultado
        de la predicción para mostrar en Dash.
        
        prediction: numpy array con los datos de la predicción.
            Cada columna representa una escuela.
        Y: numpy array con los datos reales.
            Cada columna representa una escuela
        """

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
    """
    Clase Modelo que sirve como interfaz para la predicción de distintos
    métodos que tiene la capacidad de guardar en memoria los conjuntos
    que ya calculó previamente.
    """
    
    def __init__(self, function, args = dict()) :
        """
        Constructor de la clase modelo.
        
        function: función de python que predice una serie de tiempo
            utilizando un método específico.
        
        args: parámetro opcional para los modelos que utilicen parámetros
            extra aparte de los datos y el tamaño de predicción.
        """
        
        self.model_function = function
        self.args = args
        
        self.cached_sets = dict()
        
        # Número máximo de años de predicción
        self.TEST_SIZE = 5
    
    def predict(self, data, prediction_size) :
        """
        Método que realiza una predicción sobre una observación de datos.
        
        data: numpy array con los valores de la serie de tiempo.
        prediction_size: número de valores o años que se quiere predecir
        
        return: numpy array con los valores de la predicción
        """
        
        self.args['prediction_size'] = prediction_size
        self.args['data'] = data
        
        return self.model_function(**self.args)
    
    def test_set(self, set_name, prediction_size) :
        """
        Método que evalúa un conjunto de datos con el modelo que guarda
        esta clase.
        
        set_name: nombre del conjunto a evaluar.
        
        return: clase TestResult con los resultados de la evaluación
        """
        
        assert(prediction_size <= self.TEST_SIZE)
        
        key = '%s_%d' % (set_name, prediction_size)
        
        if key not in self.cached_sets :
            dataset = pd.read_csv(set_name + '.csv')
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
    # Para efectos de pruebas
    model = Model(fixed_partitioning_predict)
    result = model.test_set('DummySet', 5)
    print(LoadHTMLTable(result.metricas, 'Fix. Part. Time series'))
