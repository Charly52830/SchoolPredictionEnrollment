/**
*	Función que devuelve la cantidad de alumnos de cada escuela primaria del estado que pertenecen
*	a un sostenimiento específico.
*
*	param sostenimiento: sostenimiento de las escuelas.
*		Tiene que ser alguno de los siguientes campos (EN MAYÚSCULA):
*		PRIVADO, PÚBLICO
*		Si no se especifica el parámetro entonces la información
*		devuelta contendrá tanto escuelas privadas como públicas.
*	
*	return: json (300 Kb aprox) con los registros de los alumnos en cada año de cada primaria del estado.
*/

var nivel_educativo = "PREESCOLAR"
var matricula = {}
var escuelas

if(sostenimiento == null) 
	escuelas =  orient.getDatabase().command("SELECT FROM escuela WHERE servicio2 = ?", nivel_educativo)
else
	escuelas =  orient.getDatabase().command("SELECT FROM escuela WHERE servicio2 = ? and sost_control = ? ", nivel_educativo, sostenimiento)

for(var i = 0; i < escuelas.length; i ++) {
	var escuela = escuelas[i].getRecord()
    var cct = escuela.getProperty("cct")
    var datos_escuela = matriculaEscuela(cct)
    var anios = datos_escuela[0]
    var alumnos = datos_escuela[1]
    if(anios.length >= 18) {
		var registro = {}
        for(var j = 0; j < anios.length; j ++) {
          if(anios[j] != 2010)
              registro[anios[j]] = alumnos[j]
    	}
    	matricula[cct] = registro
    }
}

return matricula
