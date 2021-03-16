/**
 * Función que devuelve los generales de una escuela si se considera activa.
 * Una escuela es activa si su estatus es ACTIVO y si tiene al menos el 70% de 
 * datos de la matrícula y el grupo a partir del primer año en el que aparece
 * en la base de datos.
 * 
 * Realiza una limpieza de los datos, de forma que los datos de la matrícula o el
 * grupo que se encuentren en cero los sustituye por el promedio de los datos que 
 * no se encuentran en cero.
 *
 * Devuelve además de la matrícula, el promedio de la tasa de alumnos por grupo, nivel,
 * latitud, longitud, municipio, región y nombre de la escuela.
 * 
 * param escuela_o_cct: cct de la escuela (string) u objeto escuela.
 * param forzar_inactiva: si es true devuelve los datos de la escuela incluso si se considera
 *   inactiva.
 *
 * returns objeto json con los datos generales de la escuela.
 */

var limpiar_anios_en_cero = function(anios, valores) {
  var anios_sin_cero = 0;
  var suma = 0;

  for(var i = 0; i < anios.length; i ++) {
    suma += valores[i];
    if(valores[i] > 0)
      anios_sin_cero ++;
  }
  
  // Si el 70% de los datos se encuentran en 0 entonces se considera una escuela inactiva
  if(anios_sin_cero <  0.7 * anios.length && !forzar_inactiva)
    return "Escuela inactiva";
  
  var promedio = parseInt(suma / anios_sin_cero);

  // Sustituir los valores en cero con el promedio
  for(var i = 0; i < anios.length; i ++) {
    if(valores[i] == 0) 
      valores[i] = promedio;
    valores[i] = parseInt(valores[i]);
  }
  
  return valores;
}

var capitalizar = function(string) {
  var palabras = string.split(' ');
  var respuesta = '';
  palabras.forEach(function(palabra) {
    palabra = palabra.toLowerCase();
    
    // Eliminar caracteres especiales
    var patron = new RegExp(/[\wáéíóúñ]+/);
    palabra = patron.exec(palabra);
    if(palabra == null)
      return;
    palabra = palabra[0];
    
    
    // Capitalizar
    if(palabra.length > 3 || respuesta.length == 0) {
      var primer_letra = palabra.slice(0, 1).toUpperCase();
      var resto_de_la_palabra = palabra.slice(1);
      palabra = primer_letra + resto_de_la_palabra;
    }
    
    if(respuesta.length > 0)
      respuesta += ' ';
    respuesta += palabra;
  });
  return respuesta;
}

if(forzar_inactiva != null) {
  if(forzar_inactiva === "true" || forzar_inactiva === "false")
    forzar_inactiva = (forzar_inactiva === "true");
  else if(!(forzar_inactiva === true || forzar_inactiva === false))
    return "No se especificaron correctamente los parámetros de la función";
}
else
  forzar_inactiva = false;

var escuela = null;
if(typeof escuela_o_cct === 'string' || escuela_o_cct instanceof String) {
  var cct = escuela_o_cct;
  var escuela =  orient.getDatabase().command("SELECT FROM escuela WHERE cct = ?", cct)
  
  if(escuela.length == 0)
      return "Escuela no encontrada";

  escuela = escuela[0].getRecord();
}
else 
  escuela = escuela_o_cct;

var estatus = escuela.getProperty("estatus");
if(estatus != "ACTIVO" && !forzar_inactiva)
  return "Escuela inactiva";

var nivel_escuela = escuela.getProperty("servicio2");
var nombre_escuela = escuela.getProperty("nombre");

/* Obtener matrícula de la escuela y obtener el promedio para sustituir los valores
que tienen cero */

var anios_y_matricula = MatriculaEscuela(escuela);
var anios_matricula = anios_y_matricula[0];
var matricula = anios_y_matricula[1];
matricula = limpiar_anios_en_cero(anios_matricula, matricula);
if(!forzar_inactiva && matricula === "Escuela inactiva" || matricula.length == 0)
  return "Escuela inactiva";

/* Obtener matrícula de la escuela y obtener el promedio para sustituir los valores
que tienen cero */
var anios_y_grupos = GruposEscuela(escuela);
var anios_grupos = anios_y_grupos[0];
var grupos = anios_y_grupos[1];
grupos = limpiar_anios_en_cero(anios_grupos, grupos);
if(!forzar_inactiva && grupos === "Escuela inactiva" || grupos.length == 0)
  return "Escuela inactiva";

// Alinear los mismos años de los grupos y alumnos para calcular el promedio de la tasa de alumnos por grupo
var primer_anio_grupos = anios_grupos[0];
var ultimo_anio_grupos = anios_grupos[anios_grupos.length - 1];
var anio_grupos = primer_anio_grupos;

var primer_anio_matricula = anios_matricula[0];
var ultimo_anio_matricula = anios_matricula[anios_matricula.length - 1];
var anio_matricula = primer_anio_matricula;

var sum_grupos_alineados = 0;
var contador_anios_alineados = 0;

while(anio_grupos <= ultimo_anio_grupos || anio_matricula <= ultimo_anio_matricula) {
  if(anio_grupos == anio_matricula) {
    sum_grupos_alineados += 
      matricula[anio_matricula - primer_anio_matricula] / grupos[anio_grupos - primer_anio_grupos];
    contador_anios_alineados ++;
    
    anio_grupos ++;
    anio_matricula ++;
  }
  else if(anio_grupos < anio_matricula) 
    anio_grupos ++;
  else
    anio_matricula ++;
}
var promedio_alumnos_grupo = sum_grupos_alineados / contador_anios_alineados;

var ubicacion = UbicacionEscuela(escuela);
var lat = ubicacion["lat"];
var lng = ubicacion["lng"];
var mun = ubicacion["mun"];

respuesta = {
  "primer_anio" : primer_anio_matricula,
  "matricula" : matricula,
  "prom_alumnos_grupo" : parseFloat(promedio_alumnos_grupo.toFixed(3)),
  "nombre" : capitalizar(nombre_escuela),
  "nivel" : capitalizar(nivel_escuela),
  "lat" : lat,
  "lng" : lng,
  "mun" : capitalizar(mun),
  "region" : RegionEscuela(escuela)
}

return respuesta; 
