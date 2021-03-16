/**
 * Función que obtiene la región de una escuela.
 *
 * Notas importantes:
 * (31/12/2020): 
 * - Por motivos del diccionario, solo se puede obtener la región de las escuelas que tengan
 * datos después del 2016.
 *
 * param escuela_o_cct: cct de la escuela (string) u objeto escuela.
 * 
 * returns clave de la región a la que pertenece la escuela.
 */

var formato_anio = function(anio) {
  if(anio < 10) 
    return "0" + anio.toString();
  return anio.toString();
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

var periodos = DiccionarioRegionEscuela(escuela.getProperty("servicio2"));

for(var periodo = periodos.length - 1; periodo >= 0; periodo --) {
  var anio_inicio = periodos[periodo][0];
  var anio_fin = periodos[periodo][1];
  var campo = periodos[periodo][2];
	
  for(var anio = anio_inicio; anio <= anio_fin; anio ++) {
    var nombre_arista = "out_resultado_i" + formato_anio(anio % 100) + formato_anio((anio + 1) % 100);
    var edges = escuela.field(nombre_arista);
    if(edges == null)
      continue;
      
    var edge_iterator = edges.iterator();
    while(edge_iterator.hasNext()) {
      edge = edge_iterator.next();
      var estadistica_911 = edge.getProperty("in");
      var region = estadistica_911.getProperty(campo);
      
      if(region != null)
        return region;
    }
  }
}

return "Region no encontrada";
