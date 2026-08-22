"""
Fast Vectorized Glynn and Ryser Permanent Engine.
"""
import numpy as np

def fast_glynn_permanent(matrix: np.ndarray) -> complex:
    n = matrix.shape[0]
    if n == 0: return 1.0 + 0.0j
    if n == 1: return matrix[0, 0]
    
    total = 0.0 + 0.0j
    for k in range(1 << (n - 1)):
        delta = np.array([1 if (k & (1 << j)) else -1 for j in range(n - 1)] + [1])
        prod_delta = np.prod(delta)
        row_sums = np.sum(matrix * delta, axis=1)
        total += prod_delta * np.prod(row_sums)
    return total / (2 ** (n - 1))
