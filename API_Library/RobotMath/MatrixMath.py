import numpy as np

class MatrixMath:
    '''
    Matrix Math Operations

    This class provides static methods for performing matrix operations such as
    Least Square Error (LSE) and Singular Value Decomposition (SVD).

    Example usage:
    --------------
    from MatrixMath import MatrixMath as mm

    matrixA = np.matrix([[1, 1, 0, 0], 
                         [0, 0, 1, 1]])
    matrixB = np.matrix([[16], [13]])

    result = mm.LSE(matrixA, matrixB)
    print(result)

    U, S, Vt = mm.SVD(matrixA)
    print("U:", U)
    print("S:", S)
    print("Vt:", Vt)
    '''
    @staticmethod
    def LSE(A: np.matrix, B: np.matrix):
        '''
        Least Square Error

        Solves the equation Ax = B by computing a vector x that minimizes the Euclidean 2-norm || B - Ax ||^2.

        Parameters
        ----------
        A : np.matrix
            Coefficient matrix.
        B : np.matrix
            Ordinate or "dependent variable" values.

        Returns
        -------
        x : np.ndarray
            Least-squares solution.
        
        Example
        -------
        >>> A = np.matrix([[1, 1, 0, 0], [0, 0, 1, 1]])
        >>> B = np.matrix([[16], [13]])
        >>> MatrixMath.LSE(A, B)
        array([[16.],
               [16.],
               [13.],
               [13.]])
        '''
        return np.linalg.lstsq(A, B, rcond=None)[0]

    @staticmethod
    def SVD(matrix: np.matrix):
        '''
        Singular Value Decomposition

        Factorizes the matrix into three matrices U, S, and Vt such that matrix = U * S * Vt.

        Parameters
        ----------
        matrix : np.matrix
            The input matrix to be decomposed.

        Returns
        -------
        U : np.ndarray
            Unitary matrix having left singular vectors as columns.
        S : np.ndarray
            The singular values, sorted in non-increasing order.
        Vt : np.ndarray
            Unitary matrix having right singular vectors as rows.
        
        Example
        -------
        >>> matrix = np.matrix([[1, 1, 0, 0], [0, 0, 1, 1]])
        >>> U, S, Vt = MatrixMath.SVD(matrix)
        >>> print("U:", U)
        >>> print("S:", S)
        >>> print("Vt:", Vt)
        '''
        U, S, Vt = np.linalg.svd(matrix, full_matrices=False)
        return U, S, Vt