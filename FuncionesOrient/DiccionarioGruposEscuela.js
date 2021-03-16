/**
*	Diccionario con los campos del número de grupos de la estadística 911 
*	a inicio del ciclo escolar de cada nivel escolar.
*
*   Notas importantes:
*   (31/12/2020):
*   - Los registros de 1996 y 1997 son inválidos para primaria y preescolar, pero
*	  son válidos para secundaria, por lo que se comentaron sus campos.
*
*	param nivel: nivel escolar del que se quiere saber los periodos
*
*	return: arreglo con los periodos en los que la estadistica 911 cambió el formato
*		del nivel educativo especificado. Cada periodo contiene 3 datos:
*		- Primer año del formato
*		- Último año del formato
*		- Campo con el que se identificó a la cantidad de grupos
*/

var periodos = {
	"PREESCOLAR" : [
		[1990, 1995, "No hay diccionario"],
        //[1996, 1997, "TOT31"],
		[1998, 2016, "V64"],
		[2017, 2017, "V182"],
		[2018, 2018, "v182"],
		[2019, 2019, "V182"]
	],
	"PRIMARIA" : [
      	[1990, 1995, "No hay diccionario"],
        //[1996, 1997, "TOT87"],
		[1998, 2016, "V348"],
		[2017, 2017, "V616"],
		[2018, 2018, "v616"],
		[2019, 2019, "V616"]
	],
	"SECUNDARIA" : [
		[1990, 1995, "No hay diccionario"],
		[1996, 1997, "TOT37"],
		[1998, 2016, "V165"],
		[2017, 2017, "V341"],
		[2018, 2018, "v341"],
		[2019, 2019, "V341"]
	]
}

return periodos[nivel]
