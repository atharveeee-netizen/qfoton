# -*- coding: utf-8 -*-
# ==============================================================================
# Qfóton: Hardware-Aware Silicon Photonic Quantum Compiler & Simulator
# Copyright (c) 2026 Atharve and the Qfóton Contributors. All rights reserved.
# Released under the MIT License.
# ==============================================================================
"""
Created on Mon Mar 10 12:34:13 2025

@author: Hüttenbrenner
"""

import numpy as np
from numba import njit
from .Basis import *


#%% helper functions
def factorial_normalization(fock_state):
    N=1
    for n in fock_state:
        N *= factorial(n)
    return np.sqrt(N)  

# @njit
# def get_bit_digits(n, num_bits=32):
#     bits = np.zeros(num_bits, dtype=np.uint8)  # Pre-allocate an array
#     for i in range(num_bits):
#         bits[num_bits - 1 - i] = (n >> i) & 1  # Extract bits from LSB to MSB
#     return np.array(bits)

# @njit
# def permanent(M):
#     '''
#     implements Ryzer's algorithm using Gray code to calculate the matrix permanent'

#     Parameters
#     ----------
#     A : np.ndarray
#         a matrix, in our case the helper matrix we build with build_matrix
        

#     Returns
#     -------
#      : complex128
#         permanent of said matrix

#     '''
#     n, nc = M.shape  # Get the number of rows (n) and columns (nc) of matrix M
#     P = 0  # Initialize the sum for computing the permanent

#     for i in range(1, 2**n):  # Iterate over all non-empty subsets (1 to 2^n - 1)
#         indx = np.array([(i >> j) & 1 for j in range(n)], dtype=np.uint8)  
#         sign = (-1) ** np.sum(indx)  # Compute (-1)^(sum of indx entries)
#         col_sums = np.sum(M * indx[:, None], axis=0)  # Compute column sums after applying the mask
#         P += sign * np.prod(col_sums)  # Multiply all column sums and add to P

#     return (-1) ** n * P

@njit()
def permanent(M): #this is Patrik's faster implementation using Grey code
    n = len(M)
    if n == 0:
        return M.dtype.type(complex(1.0))
    # row_comb keeps the sum of previous subsets.
    # Every iteration, it removes a term and/or adds a new term
    # to give the term to add for the next subset
    row_comb = np.zeros((n), dtype=M.dtype)
    total = 0
    old_grey = 0
    sign = +1
    binary_power_dict = [2**i for i in range(n)]
    num_loops = 2**n
    for k in range(0, num_loops):
        bin_index = (k + 1) % num_loops
        reduced = np.prod(row_comb)
        total += sign * reduced
        new_grey = bin_index ^ (bin_index // 2)
        grey_diff = old_grey ^ new_grey
        grey_diff_index = binary_power_dict.index(grey_diff)
        new_vector = M[grey_diff_index]
        direction = (old_grey > new_grey) - (old_grey < new_grey)
        for i in range(n):
            row_comb[i] += new_vector[i] * direction
        sign = -sign
        old_grey = new_grey
    return total


@njit
def build_matrix_fock(Input, Output, U): 
    dim = np.sum(Input)
    A = np.zeros((dim, dim), dtype=np.complex128)  # Use complex128

    l = 0
    for i in range(len(Output)):  # Use range instead of enumerate for Numba compatibility
        n_i = Output[i]
        if n_i != 0:
            x = 0
            while x < n_i:
                m = 0
                for k in range(len(Input)):  # Same here
                    n_k = Input[k]
                    if n_k != 0:
                        y = 0
                        while y < n_k:
                            A[l, m] = U[i, k]  # U should also be complex128
                            m += 1
                            y += 1
                x += 1
                l += 1
    return A

@njit
def build_matrix_idx(Input, Output, U):
    U = U.astype(np.complex128)
    dim = len(Input)
    U_size = len(U)
    A = np.zeros((dim, dim), dtype=np.complex128)  # Use complex128
    U_rows = np.zeros((dim, U_size), dtype=np.complex128)
    U_rows = U[Output, :] #fancy indexing: take out the full rows of U specified by the Output idx-state
    A=U_rows[:, Input]  #now take the columns specified by the Inpute
    return A

def amplitude_fock(Input, Output, U):
    '''
    

    Parameters
    ----------
    Input : np.ndarray
        Fock state basis vector
    Output : np.ndarray
        Fock state basis vector
    U : np.ndarray
        Unitary matrix of the circuit (mode trafo for creation and annihilation operators / single photon transformation matrix)

    Returns
    -------
    Amplitude: complex 128
        This is Phi[U_circuit](Input,Output)

    '''
    A=build_matrix_fock(Input, Output, U) 
    perm = permanent(A)
    return perm/(factorial_normalization(Input)*factorial_normalization(Output))

def amplitude_idx(Input, Output, U):
    '''
    Parameters
    ----------
    Input : np.ndarray
        index-basis vector
    Output : np.ndarray
        index-basis vector
    U : np.ndarray
        Unitary matrix of the circuit (mode trafo for creation and annihilation operators / single photon transformation matrix)

    Returns
    -------
    Amplitude: complex 128
        This is Phi[U_circuit](Input,Output)

    '''
    num_modes = len(U)
    if len(Input)!=len(Output):
        return 0
    A=build_matrix_idx(Input, Output, U) 
    perm = permanent(A)
    return perm/(factorial_normalization(idx_to_fock(Input, num_modes))*factorial_normalization(idx_to_fock(Output, num_modes)))# the normalization here works by converting to fock

def Amplitudes_idx(Inputs, Outputs, U):
    Inputs = np.atleast_2d(Inputs) #handly 1 state only
    Outputs = np.atleast_2d(Outputs)
    #for a given list of inputs and outputs, calculate the corresponding transition amplitudes. There are two functions here, one takes index vectors and one fock vectors
    Amps = np.zeros((len(Inputs),len(Outputs)), dtype=np.complex128) 
    for i, Input in enumerate(Inputs):
        for j, Output in enumerate(Outputs):
            Amps[i,j] = amplitude_idx(Input, Output, U)
    return Amps

def Amplitudes_fock(Inputs, Outputs, U):
    Inputs = np.atleast_2d(Inputs)
    Outputs = np.atleast_2d(Outputs)
    Amps = np.zeros((len(Inputs),len(Outputs)), dtype=np.complex128) 
    for i, Input in enumerate(Inputs):
        for j, Output in enumerate(Outputs):
            Amps[i,j] = amplitude_fock(Input, Output, U)
    return Amps

#%%Amplitude array class
class Phi:
    def __init__(self, Inputs: np.ndarray, Outputs: np.ndarray, U: np.ndarray, fock=False):
        self.Inputs = Inputs
        self.Outputs = Outputs
        self.U = U
        self.fock = fock
    def get_amplitudes(self) -> np.ndarray:
        if not self.fock:
            return Amplitudes_idx(self.Inputs, self.Outputs, self.U)
        else:
            return Amplitudes_fock(self.Inputs, self.Outputs, self.U)


#%% test
#Input  = np.array([0,2,1])
#Output = np.array([1,1,1])
#M_U = np.array([[11,12,13],
#                [21,22,23],
#                [31,32,33]])
#B_fock = build_matrix_fock(Input, Output, M_U)
# amp_fock = amplitude_fock(Input, Output, M_U)

# Input_idx = np.array([0,1,2])
# Output_idx = np.array([1,1,2])
# B_idx = build_matrix_idx(Input_idx, Output_idx, M_U)
# amp_idx = amplitude_idx(Input_idx, Output_idx, M_U)





# Input = np.array([2,0])
# Output = np.array([2,0])
# M_U = np.array([[11,12],
#                 [21,22]])
# B = build_matrix(Input, Output, M_U)
#amp = amplitude(Input, Output, M_U)

#%% compare speed 
# import timeit

# # Create a test matrix (e.g., 6x6 with random integers)
# np.random.seed(42)
# matrix = np.random.rand(6, 6) + 1j * np.random.rand(6, 6)

# # Wrap the functions for timeit
# def time_naive():
#     permanent(matrix)

# def time_grey():
#     perm_ryser(matrix)

# # Time them
# naive_time = timeit.timeit(time_naive, number=10)
# grey_time = timeit.timeit(time_grey, number=10)

# print(f"Naive time (10 runs): {naive_time:.6f} seconds")
# print(f"Grey code time (10 runs): {grey_time:.6f} seconds")