/**
*	Función que calcula los valores de la linea de regresión lineal.
*
*	param x: lista de los valores independientes
*	param y: lista de los valores de respuesta
*	
*	return arreglo con los valores de intercept y slope de la linea de regresión
*/

var mean = function(elems) {
	var sum = 0.0;
	for(var i = 0; i < elems.length; i++) 
    	sum += elems[i]
	return sum / elems.length
}

var square = function(n) {
	return n * n
}

var cross_deviation = function(x,y) {
	var sum = 0.0
    var x_mean = mean(x)
    var y_mean = mean(y)
    var n = x.length
    for(var i = 0; i < n; i++) 
		sum += (x[i] - x_mean) * (y[i] - y_mean)
    return sum
}

var squared_deviation = function(x) {
	var x_mean = mean(x)
    var n = x.length
    var sum = 0.0
    for(var i = 0; i < n; i++ ) 
		sum += square(x[i] - x_mean)
	return sum
}

if(x.length != y.length || x.length < 2)
	return null

var slope = cross_deviation(x,y) / squared_deviation(x)
var y_intercept = mean(y) - slope * mean(x)

return [y_intercept, slope]
