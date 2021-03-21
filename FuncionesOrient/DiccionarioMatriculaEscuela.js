/**
*	Diccionario con los campos del número de alumnos de la estadística 911 
*	a inicio del ciclo escolar de cada nivel escolar.
*
*	Notas importantes 
*	(31/03/2020):
*	- No hay diccionario del periodo de 1990 a 1995, pero si hay registros.
*	- No hay registros de estadística 911 de media superior a partir del 2013.
*	- No hay registros de estadística 911 de superior.
*
*	(07/04/2020):
*	- Los registros de primaria del 2010 se encuentran perdidos
*	- Los registros de secundaria del 2015 se encuentran perdidos
*
*	(29/12/2020):
*	- Los registros de 1996 y 1997 son inválidos para primaria y preescolar, pero
*	  son válidos para secundaria, por lo que se comentaron sus campos.
*
*	param nivel: nivel escolar del que se quiere saber los periodos
*
*	return: arreglo con los periodos en los que la estadistica 911 cambió el formato
*		del nivel educativo especificado. Cada periodo contiene 3 datos:
*		- Primer año del formato
*		- Último año del formato
*		- Campo con el que se identificó a la cantidad de alumnos
*/

var periodos = {
	"PREESCOLAR" : [
		[1990, 1995, "No hay diccionario"],
		//[1996, 1997, "TOT30"],
		[1998, 2016, "V63"],
		[2017, 2017, "V177"],
		[2018, 2018, "v177"],
		[2019, 2020, "V177"]
	],
	"PRIMARIA" : [
		[1990, 1995, "No hay diccionario"],
		//[1996, 1997, "TOT158"],
		[1998, 2016, "V347"],
		[2017, 2017, "V608"],
		[2018, 2018, "v608"],
		[2019, 2020, "V608"]
	],
	"SECUNDARIA" : [
		[1990, 1995, "No hay diccionario"],
		[1996, 1997, "TOT85"],
		[1998, 2016, "V164"],
		[2017, 2017, "V340"],
		[2018, 2018, "v340"],
		[2019, 2020, "V340"]
	],
	"MEDIA SUPERIOR" : [
		[1990, 1995, "No hay diccionario"],
		[1996, 1997, "TOT7"],
		[1998, 2013, "V15"],
		[2014, 2014, "MS184"],
		[2015, 2017, "MS815"],
		[2018, 2020, "V51"]
	],
	"SUPERIOR" : [
		[1990, 1995, "No hay diccionario"],
		[1996, 1996, "SIV016"],
		[1997, 1997, "SIV074Z"],
		[1998, 2003, "SIV016Z"],
		[2004, 2017, "S12"],
		[2018, 2020, "V226"]
	]
}

return periodos[nivel]
