"""
Gaussian Boson Sampling (GBS) and Matrix Hafnian Engine.
"""
import numpy as np

def hafnian_2x2(matrix: np.ndarray) -> complex:
    if matrix.shape == (2, 2):
        return matrix[0, 1]
    return 0.0 + 0.0j

class GaussianBosonSampling:
    def __init__(self, num_modes: int, squeezing_parameter: float = 0.8):
        self.modes = num_modes
        self.r = squeezing_parameter
