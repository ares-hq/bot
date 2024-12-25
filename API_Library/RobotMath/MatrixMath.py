import numpy as np

class MatrixMath:
    '''Matrix Math Operations

    Example usage:
    --------------
    from MatrixMath import MatrixMath as mm

    matrixA = np.matrix([[1, 1, 0, 0], 
                         [0, 0, 1, 1]])
    matrixB = np.matrix([[16], [13]])

    result = mm.LSE(matrixA, matrixB)
    print(result)
    '''

    @staticmethod
    def LSE(matrixA: np.matrix, matrixB: np.matrix):
        '''Least Square Error'''
        return np.linalg.lstsq(matrixA, matrixB, rcond=None)[0]