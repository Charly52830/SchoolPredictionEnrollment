/**
*	Función que devuelve la cantidad de grupos de cada escuela del estado que pertenecen
*	a un sostenimiento y nivel educativo específico.
*
*	Notas importantes 
*	(02/08/20) :
*	- La consulta realiza una primer limpieza de los datos. Solo devuelve el registro de las
*	  primarias que tienen más de 18 años registradas excluyendo el año 2010.
*	- Por seguridad, la función no debe de permanecer como idempotente.
*
*	param sostenimiento: sostenimiento de las escuelas.
*		Tiene que ser alguno de los siguientes campos (EN MAYÚSCULA):
*		PRIVADO, PÚBLICO
*		Si no se especifica el parámetro entonces la información
*		devuelta contendrá tanto escuelas privadas como públicas.
*	
*	return: json (300 Kb aprox) con los registros de los grupos en cada año de cada primaria del estado.
*/

var nivel_educativo = "PRIMARIA"
var grupos = {}
var escuelas

if(sostenimiento == null) 
	escuelas =  orient.getDatabase().command("SELECT FROM escuela WHERE servicio2 = ?", nivel_educativo)
else
	escuelas =  orient.getDatabase().command("SELECT FROM escuela WHERE servicio2 = ? and sost_control = ? ", nivel_educativo, sostenimiento)

for(var i = 0; i < escuelas.length; i ++) {
	var escuela = escuelas[i].getRecord()
    var cct = escuela.getProperty("cct")
    var datos_escuela = gruposEscuela(cct)
    var anios = datos_escuela[0]
    var grupos_escuela = datos_escuela[1]
    if(anios.length >= 18) {
		var registro = {}
        for(var j = 0; j < anios.length; j ++) {
          if(anios[j] != 2010)
			registro[anios[j]] = grupos_escuela[j]
    	}
    	grupos[cct] = registro
    }
}

return grupos
