/**
*	Función que devuelve la correlación entre dos arreglos
*	numéricos.
*
*	param x: primer arreglo numérico
*	param y: segundo arreglo numérico
*
*	return: valor de la correlación lineal
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

var stdev = function(elems) {
	var elems_mean = mean(elems)
	var sum = 0.0
    var n = elems.length
    for(var i = 0; i < n; i++)
		sum += square(elems[i] - elems_mean)
	return Math.sqrt(sum / n)
}

var covariance = function(x, y) {
 	var x_mean = mean(x) 
    var y_mean = mean(y)
    var sum = 0.0
    var n = x.length
    for(var i = 0; i < n; i++) 
		sum += (x[i] - x_mean) * (y[i] - y_mean)
	return sum / n
}

if(x.length != y.length || x.length < 2)
	return null

return covariance(x,y) / (stdev(x) * stdev(y))
