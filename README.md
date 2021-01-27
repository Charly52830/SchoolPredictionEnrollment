# School Enrollment Prediction 

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Charly52830/SchoolPredictionEnrollment/master?filepath=Proyeccion/JupyterNotebooks/)

Repository for the thesis project: multiple time series forecasting applied to school enrollment projection.

This project is a collaboration with the Secretary of Education of Zacatecas (SEZ) that aims to improve the enrollment forecasting process with which the number of students that will be enrolled the next years in each school of Zacatecas is obtained. The proposed solution combines neural networks, fuzzy time series and the ARIMA model in a single algorithm to generate the enrollment forecasting for the next 5 years. The Mexico 911 statistic is used to train the algorithms, and the experts opinion algorithm performs an accuracy of 11% over the forecasting method used previously to the implementation of this project.

Due to the number of observed data varies from school to school in the 911 statistic, the next rules were developed for assigning a prediction method to each school:

1. If the number of observed data is greater than 8 then the experts opinion algorithm is used.
2. If the number of observed data is between 5 and 8 then the the ARIMA model is used.
3. If the number of observed data is between 2 and 4 then Simple Linear Regression is used.
4. If the number of observed data is 1 then Naïve Forecasting is used.

For more information about the methods and its evaluation, I invite you to run the notebooks on Binder which contains the evaluation for the distincts datasets.

# Proyección de Matrícula Escolar

Repositorio para el proyecto de tesis: predicción de múltiples series de tiempo aplicado a la proyección de matrícula escolar.

Este proyecto es una colaboración con la Secretaría de Educación del estado de Zacatecas (SEZ) que busca optimizar el proceso de proyección de matrícula por el que se obtiene el número de alumnos que se inscribirán en cada escuela del estado en los próximos años. La solución propuesta se basa en combinar redes neuronales, series de tiempo difusas y el modelo ARIMA en un solo algoritmo experto que genera la predicción de matrícula en los próximos 5 años. Utiliza datos de la estadística 911 y se desempeña con una precisión del 11% mayor sobre el método utilizado por la SEZ previo a la implementación de este proyecto.

Debido a que no todas las escuelas contienen el mismo número de años registrados en la estadística 911, se utilizaron las siguientes reglas para asignar un método de predicción:

1. Si el número de datos de la escuela es mayor a 8 entonces se utiliza el algoritmo de opinión de expertos.
2. Si el número de datos de la escuela se ecuentra entre 5 y 8 entonces se utiliza el modelo ARIMA.
3. Si el número de datos de la escuela se encuentra entre 2 y 4 entonces se utiliza regresión lineal simple.
4. Si la escuela tiene solo un dato entonces se utiliza predicción ingenua.

Para más información sobre los métodos de predicción y su evaluación te invito a ejecutar en Binder los notebooks que contienen las evaluaciones de los modelos en escuelas de preescolar, primarias y secundarias.
