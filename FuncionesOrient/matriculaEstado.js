/**
*	Función que devuelve la cantidad de alumnos en el estado por cada año.
*
*	param nivel_educativo: nivel del que se quiere realizar la consulta
*		Tiene que ser alguno de los siguientes campos (EN MAYÚSCULA):
*		PREESCOLAR, PRIMARIA, SECUNDARIA, MEDIA SUPERIOR, SUPERIOR
*	
*	param sostenimiento: sostenimiento de las escuelas.
*		Tiene que ser alguno de los siguientes campos (EN MAYÚSCULA):
*		PRIVADO, PÚBLICO
*		Si no se especifica el parámetro entonces la información
*		devuelta contendrá tanto escuelas privadas como públicas.
*	
*	return: objeto de la forma año : alumnos
*/

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
    for(var j = 0; j < anios.length; j ++) {
		if(!matricula.hasOwnProperty(anios[j])) 
			matricula[anios[j]] = alumnos[j]
        else
			matricula[anios[j]] += alumnos[j]
    }
}

return matricula
