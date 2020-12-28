/**
*	Función que obtiene el número de grupos en cada año de una escuela específica.
*
*	param cct_escuela: clave del centro de trabajo de la escuela (se aceptan
*		escuelas de preescolar, primaria y secundaria).
*
*	return: arreglo que contiene otros 2 arreglos de la misma longitud:
*		- x: años en los que se encontró registros de alumnos
*		- y: alumnos en la escuela en el respectivo año
*/

var formato_anio = function(anio) {
  if(anio < 10) 
    return "0" + anio.toString();
  return anio.toString()
}

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

var periodos = periodosGruposEscuela(escuela.getProperty("servicio2"))

var x = []	// Años
var y = []	// Alumnos

for(var periodo = 0; periodo < periodos.length; periodo ++) {
  var anio_inicio = periodos[periodo][0]
  var anio_fin = periodos[periodo][1]
  var campo = periodos[periodo][2]

  for(var anio = anio_inicio; anio <= anio_fin; anio ++) {
    var nombre_arista = "out_resultado_i" + formato_anio(anio % 100) + formato_anio((anio + 1) % 100);
    var edges = escuela.field(nombre_arista);
    
    var suma_grupos = 0;
    if(edges != null) {
      var edge_iterator = edges.iterator();
      
      while(edge_iterator.hasNext()) {
        edge = edge_iterator.next();
        var estadistica_911 = edge.getProperty("in");
        var grupos = estadistica_911.getProperty(campo);
        
        if(grupos != null) 
          suma_grupos += grupos;
      }
    }	
    
    if(suma_grupos > 0 || x.length > 0) {
      x.push(anio);
      y.push(suma_grupos);
    }
  }
}

return [x,y]
