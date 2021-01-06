import numpy as np

class Normalizator:
	
	def normalize(self, data) :
		"""Método que aplica la normalización de los datos"""
		pass
	
	def denormalize(self, data):
		"""Método que aplica la desnormalización de los datos"""
		pass

class MinMaxNormalizator(Normalizator) :
	"""
	y' = a + ((y - min(Y)) * (b - a)) / (max(Y) - min(Y))

	Referencia:
	https://en.wikipedia.org/wiki/Feature_scaling

	"""

	def __init__(self, data, a = -1, b = 1) :
		self.max = np.max(data)
		self.min = np.min(data)
		self.a = a
		self.b = b
		assert(a < b)
	
	def normalize(self, data) :
		if self.max == self.min :
			# Caso especial, si todos los números son iguales MinMaxNormalizator se
			# convierte en DummyNormalizator
			return data
		return self.a + ((data - self.min) * (self.b - self.a)) / (self.max - self.min)
	
	def denormalize(self, data) :
		if self.max == self.min :
			# Caso especial, si todos los números son iguales MinMaxNormalizator se
			# convierte en DummyNormalizator
			return data
		return self.min + ((data - self.a) * (self.max - self.min)) / (self.b - self.a)

class DifferencingNormalizator(Normalizator) :
	"""
	y_i' = y_i - y_(i - 1)
	"""
	
	def __init__(self, data) :
		pass
	
	def normalize(self, data) :
		self.last_value = data[-1]
		return np.array([data[i] - data[i - 1] for i in range(1, len(data))])
		
	def denormalize(self, data) :
		data[0] += self.last_value
		for i in range(1, len(data)) :
			data[i] += data[i - 1]
		return data

class DummyNormalizator(Normalizator) :
	"""
	y' = y
	"""

	def __init__(self) :
		pass
	
	def normalize(self, data) :
		return data
	
	def denormalize(self, data):
		return data

if __name__ == "__main__" :
	data = np.array([5,2,8,3,-1])
	normalizator = MinMaxNormalizator(data, -1, 1)
	data = normalizator.normalize(data)
	data = normalizator.denormalize(data)
	print(data)
