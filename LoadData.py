import numpy as np
import pandas as pd
import random

def loadData(csv_file, window_len, test_len, Y_size, drop_columns = 0, shuffle_data = True) :
	dataset = pd.read_csv(csv_file)
	dataset = dataset.drop('cct', 1)
	
	first_year = 1998
	for i in range(drop_columns) :
		dataset = dataset.drop(str(first_year + i), 1)
	
	assert(window_len + Y_size + test_len <= dataset.shape[1])
	assert(Y_size <= test_len)
	
	m = dataset.shape[0] * (dataset.shape[1] - test_len - Y_size - window_len + 1)
	m_test = dataset.shape[0] * test_len
	
	index = [i for i in range(m)]
	if shuffle_data :
		# Apply random shuffle to index
		random.seed(0)
		random.shuffle(index)
	
	x_train = np.zeros((window_len, m))
	y_train = np.zeros((Y_size, m))
	x_test = np.zeros((window_len, m_test))
	y_test = np.zeros((Y_size, m_test))
	
	m_count = 0
	m_test_count = 0
	
	print(m, m_test)
	
	for i in range(dataset.shape[0]) :
		row = np.array(dataset.loc[i])
		for j in range(window_len, dataset.shape[1] - Y_size + 1) :
			if j < dataset.shape[1] - test_len - Y_size + 1:
				# Train dataset
				x_train[:, index[m_count]] = row[j - window_len : j]
				y_train[:, index[m_count]] = row[j : j + Y_size]
				m_count += 1
				
			else :
				# Test dataset
				x_test[:, m_test_count] = row[j - window_len : j]
				y_test[:, m_test_count] = row[j : j + Y_size]
				m_test_count += 1
		
	assert(m_count == m)
	assert(m_test_count == m_test)
	
	return (x_train, y_train, x_test, y_test)


	
if __name__ == '__main__' :
	sortData('PrimariasPublicas.csv')
	
