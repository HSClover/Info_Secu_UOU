import numpy as np

str = "attackatdawn"

matrix = np.array(list(str)).reshape(3,4)

matrix = matrix[[2,1,0,],:]
matrix = matrix[:,[3,1,0,2]]

print("".join(matrix.flatten()))

matrix = matrix[:,[]]
matrix = matrix[[2,1,0],:]

print("".join(matrix.flatten()))