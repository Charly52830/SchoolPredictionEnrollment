/**
*	Función que predice la cantidad de alumnos que habrá en los próximos años 
*	en una escuela especifica, aplicando regresión lineal en los datos
*	históricos.
*
*	param cct_escuela: escuela de la que se quiere predecir la matricula
*	param anios_prediccion: número de años que se quieren predecir a partir del
*		último registro en la base de datos.
*	
*	return anios: arreglo con los años predecidos
*	return alumnos: número de alumnos predecidos en el respectivo año
*	return cor:	correlación de los datos históricos
*/

var datos_escuela = matriculaEscuela(cct_escuela)

if(datos_escuela == "Escuela no encontrada")
	return datos_escuela

var x = datos_escuela[0] 	// Años
var y = datos_escuela[1]	// Alumnos

if(x.length < 2) 
	return "Insuficientes datos para predicción"

var b = regresionLinealSimple(x, y)
var ultimo_anio = x[x.length - 1]
var prediccion_x = []	// Años a predecir
var prediccion_y = []	// Predicción de alumnos

for(var i = 1; i <= anios_prediccion; i++) {
	prediccion_x.push(ultimo_anio + i)
	prediccion_y.push(b[0] + (ultimo_anio + i) * b[1])
}

var resultado = {
	anios : prediccion_x,
	alumnos : prediccion_y,
	cor : correlacion(x, y)
}

return resultado
