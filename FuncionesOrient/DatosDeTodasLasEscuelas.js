/**
 * Función que devuelve los datos generales de todas las escuelas activas.
 * 
 * param forzar_escuelas_inactivas: si es false (por defecto) devuelve solo las
 *   escuelas activas si es true devuelve los datos de las escuelas incluso si se 
 *   consideran inactivas.
 */

if(forzar_escuelas_inactivas != null) {
  if(forzar_escuelas_inactivas === "true" || forzar_escuelas_inactivas === "false")
    forzar_escuelas_inactivas = (forzar_escuelas_inactivas === "true");
  else if(!(forzar_escuelas_inactivas === true || forzar_escuelas_inactivas === false))
    return "No se especificaron correctamente los parámetros de la función";
}
else
  forzar_escuelas_inactivas = false;

// Obtener todas las escuelas
var escuelas = orient.getDatabase().command("SELECT FROM escuela WHERE servicio2 IN ['PREESCOLAR', 'PRIMARIA', 'SECUNDARIA']");
var resultado = {};

for(var i = 0; i < escuelas.length; i ++) {
  var escuela = escuelas[i].getRecord();
  var cct = escuela.getProperty("cct");
  var datos_escuela = DatosGeneralesEscuela(escuela, forzar_escuelas_inactivas);
  if(datos_escuela != "Escuela inactiva")
  	resultado[cct] = datos_escuela;
}

return resultado;
