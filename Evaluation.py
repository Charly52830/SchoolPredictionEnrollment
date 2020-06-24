import numpy as np
import pandas as pd
import plotly.graph_objects as go

from TimeSeriesPrediction import fixed_partitioning_predict

class TestResult :
    
    def __init__(self, prediction, Y) :
        """
        Constructor de la clase TestResult. Prepara los parámetros del resultado
        de la predicción para mostrar en Dash.
        
        prediction: numpy array con los datos de la predicción.
        Y: numpy array con los datos reales.
        """
        
        assert(len(prediction) == len(Y))
        
        # Mean absolute error
        self.mae = np.abs(prediction - Y).mean()
        
        # Mean absolute percentage error
        self.mape = np.abs( (prediction - Y) / Y).mean()
        
        # TO DO: agregar cálculo de probabilidad de riesgo
        
        m = Y.shape[0] * Y.shape[1]
        prediction = np.reshape(prediction, m)
        Y = np.reshape(Y, m)
        
        # Gráfica de evaluación
        self.fig = go.Figure()
        
        m = max(np.amax(prediction), np.amax(Y))
        # Rango de confianza
        self.fig.add_trace(go.Scatter(
            x = [0, 10, m + 5, m - 5, 0, 0], 
            y = [0, 0, m - 5, m + 5, 10, 0], 
            mode = 'none', fill = 'tonexty', name = 'Rango deseable')
        )
        # Rango de confianza
        self.fig.add_trace(go.Scatter(
            x = [10, 20, m + 10, m - 10, 0, 0, m - 5, m + 5, 10], 
            y = [0, 0, m - 10, m + 10, 20, 10, m + 5, m - 5, 0], 
            mode = 'none', fill = 'tozeroy', name = 'Rango aceptable')
        )
        
        self.fig.update_layout(
            xaxis_title = 'Valor real',
            yaxis_title = 'Valor predecido'
        )
        self.fig.add_trace(go.Scatter(x = Y, y = prediction, mode = 'markers', name = 'Prediccion'))
        self.fig.add_trace(go.Scatter(x = [0, m], y = [0, m], mode = 'lines', name = 'Linea base'))    

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
                
                print(i, dataset.shape[0])
                
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
    model = Model(fixed_partitioning_predict)
    result = model.test_set('PrimariasCompletas', 5)
    
