import numpy as np

class LSE(object):
    '''Least Square Error'''
    def __init__(self, matrixA: np.matrix, matrixB: np.matrix):
        self.matrixA = matrixA
        self.matrixB = matrixB
    
    def getLeastSquares(self):
        return np.linalg.lstsq(self.matrixA, self.matrixB, rcond=None)[0]
    
# matrixA = np.matrix([[1, 1, 0, 0], 
#                      [0, 0, 1, 1]])
# matrixB = np.matrix([[16], [13]])

# matrixMath = LSE(matrixA, matrixB)
# print(matrixMath.getLeastSquares())
