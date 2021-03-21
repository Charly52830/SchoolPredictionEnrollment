/**
 * Diccionario con los campos de la región en la estadística 911.
 *
 * param nivel: nivel de la escuela de la que se quiere obtener la región.
 *
 * returns arreglo con los periodos en los que la estadistica 911 cambió el formato
*		del nivel educativo especificado. Cada periodo contiene 3 datos:
*		- Primer año del formato
*		- Último año del formato
*		- Campo con el que se identificó a la región de la escuela.
 */

var periodos = {
	"PREESCOLAR" : [
		[1990, 2016, "No hay campo"],
		[2017, 2020, "SERVREG"]
	],
	"PRIMARIA" : [
		[1990, 2016, "No hay campo"],
		[2017, 2020, "SERVREG"]
	],
	"SECUNDARIA" : [
		[1990, 2016, "No hay campo"],
		[2017, 2020, "SERVREG"]
	]
}

return periodos[nivel]
