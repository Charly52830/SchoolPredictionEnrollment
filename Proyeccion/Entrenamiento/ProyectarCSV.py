# Manejo de módulos
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import numpy as np
import pandas as pd

from Metodos.ExpertsOpinion import evaluate_and_predict_ep

if __name__ == '__main__' :
	dataset_name = "PrimariasCompletas"
	archivo_grupos = "GruposPrimaria"
	
	archivo_proyeccion = open("Proyeccion%s.csv" % (dataset_name), "a+")
	
	# Contar el número de lineas en el archivo para remotar trabajo previo
	num_lines = 0
	with open("Proyeccion%s.csv" % (dataset_name), 'r') as f:
		for line in f:
			num_lines += 1
	
	print("num_lines:", num_lines)
	
	if num_lines == 0 :
		# Insertar cabecera al nuevo archivo
		archivo_proyeccion.write("cct,proyeccion_1,proyeccion_2,proyeccion_3,proyeccion_4,proyeccion_5,mae,rmse,mape,rp\n")
		num_lines = 1
	
	# Cargar dataset de las escuelas
	escuelas = pd.read_csv(os.path.join(
		os.path.dirname(__file__), 
		os.pardir, 
		'Datasets/',
		dataset_name + '.csv'
	))
	
	# Cargar dataset de las escuelas
	grupos = pd.read_csv(os.path.join(
		os.path.dirname(__file__), 
		os.pardir, 
		'Datasets/',
		archivo_grupos + '.csv'
	))
	# Objeto para buscar ccts en el dataset de grupos
	unique_index = pd.Index(list(grupos['cct']))
	
	print("Empezando en la escuela %d" % (num_lines))
	
	for i in range(num_lines - 1, escuelas.shape[0]) :
		row = np.array(escuelas.loc[i])
		cct = row[0]
		matricula = row[1:]
		
		# Obtener el número promedio de alumnos por grupo en la escuela
		if cct in unique_index :
			index = unique_index.get_loc(cct)
			grupos_escuela = np.array(grupos.loc[index][1:])
			matricula_por_grupo = (matricula / grupos_escuela).mean()
		else :
			matricula_por_grupo = 1e9
		
		# Obtener predicción futura e histórica
		proy_matricula_futura, proy_matricula_historica = evaluate_and_predict_ep(matricula)
		matricula_historica_real = matricula[5:]
		
		# Calcular los errores
		mae = np.abs(proy_matricula_historica - matricula_historica_real).mean()
		rmse = np.sqrt(np.square(proy_matricula_historica - matricula_historica_real).mean())
		mape = np.abs((proy_matricula_historica - matricula_historica_real) / matricula_historica_real).mean()
		pr = (np.abs(proy_matricula_historica - matricula_historica_real) >= matricula_por_grupo).mean()
		
		
		proy_matricula_historica = proy_matricula_historica.astype(np.int)
		# Escribir nuevo renglón
		archivo_proyeccion.write("%s,%d,%d,%d,%d,%d,%.2lf,%.2lf,%.2lf,%.2lf\n" % (
			cct,
			proy_matricula_historica[0],
			proy_matricula_historica[1],
			proy_matricula_historica[2],
			proy_matricula_historica[3],
			proy_matricula_historica[4],
			mae,
			rmse,
			mape,
			pr
		))
		
		print("Escuela %d terminada" % (i + 1))
	
	print("Todas las escuelas han sido proyectadas en el archivo Proyeccion%s.csv" % (dataset_name))
	archivo_proyeccion.close()
