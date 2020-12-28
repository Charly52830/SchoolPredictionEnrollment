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

var edges = escuela.field("out_ubicado_en");
if(edges == null)
	return {"lat" : null, "lng" : null, "mun" : null};
var edge_iterator = edges.iterator();

while(edge_iterator.hasNext()) {
  var edge = edge_iterator.next();
  var inmueble = edge.getProperty("in");
  var latitud = inmueble.getProperty("latitud");
  var longitud = inmueble.getProperty("longitud");
  var mun = inmueble.getProperty("municipio");
  
  if(latitud != null && longitud != null)
    return {"lat" : latitud, "lng" : longitud, "mun": mun};
}

return {"lat" : null, "lng" : null, "mun" : null};
