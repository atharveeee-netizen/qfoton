# -*- coding: utf-8 -*-
# ==============================================================================
# Qfóton: Hardware-Aware Silicon Photonic Quantum Compiler & Simulator
# Copyright (c) 2026 Atharve and the Qfóton Contributors. All rights reserved.
# Released under the MIT License.
# ==============================================================================
"""
Created on Fri May 23 12:20:31 2025

@author: Hüttenbrenner
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 12:34:13 2025

@author: Hüttenbrenner
"""

'''
create a fuction that makes the W tensor. 
just make B as usual and then make the W tensor with indizes
make new way to calculate permanent
then, reuse the normalization
then, make a phi class that takes an S as input -> the functions in the beginning will also need S as input
'''

import numpy as np
from numba import njit
from .Basis import *
from .Phi_func import *
import itertools


#%% helper functions
@njit()
def W_tensor(B, S):
    '''
    Parameters: B and S, two numpy arrays, one being the distinguishability matrix S and the other the B matrix we make also in the regular case with combinatorical considerations
    returns: the W tensor whose permanent we want to calculate later
    '''
    num_modes = len(B)
    W = np.zeros((num_modes, num_modes, num_modes),dtype=np.complex128)
    for k in range(num_modes):
        for l in range(num_modes):
            for j in range(num_modes):
                W[k,l,j]=B[k,j]*np.conj(B[l,j])*S[l,k]
    return W

#@njit()
# def perm_tensor(W):
#     N = len(W)
#     perms = list(itertools.permutations(range(N), N))
#     perms = np.array(perms, dtype=int)
#     summe = 0
#     for sigma in perms:
#         for rho in perms:
#             product = 1
#             for j in range(N):
#                 product*=W[sigma[j],rho[j],j]
#             summe+=product
            
#     return summe


def perm_tensor(W):
    N = W.shape[2]
    perms = list(itertools.permutations(range(N)))
    j = np.arange(N)
    return sum(
        np.prod(W[np.array(sigma), np.array(rho), j])
        for sigma in perms
        for rho   in perms
    )


def dist_amplitude_fock(Input, Output, U, S):
    '''
    

    Parameters
    ----------
    Input : np.ndarray
        Fock state basis vector
    Output : np.ndarray
        Fock state basis vector
    U : np.ndarray
        Unitary matrix of the circuit (mode trafo for creation and annihilation operators / single photon transformation matrix)
    S : the distinguishability matrix
    
    Returns
    -------
    Amplitude: complex 128
        This is Phi[U_circuit](Input,Output)

    '''
    B=build_matrix_fock(Input, Output, U) 
    W = W_tensor(B, S)
    perm = perm_tensor(W)
    return perm/(factorial_normalization(Input)*factorial_normalization(Output))**2 #we need to square here because the result is the probability this time and not the amplitude

def dist_amplitude_idx(Input, Output, U, S):
    '''
    Parameters
    ----------
    Input : np.ndarray
        index-basis vector
    Output : np.ndarray
        index-basis vector
    U : np.ndarray
        Unitary matrix of the circuit (mode trafo for creation and annihilation operators / single photon transformation matrix)
    S : the distinguishability matrix
    
    Returns
    -------
    Amplitude: complex 128
        This is Phi[U_circuit](Input,Output)
    '''
    num_modes = len(U)
    if len(Input)!=len(Output):
        return 0
    B=build_matrix_idx(Input, Output, U) 
    W = W_tensor(B, S)
    perm = perm_tensor(W)
    return perm/(factorial_normalization(idx_to_fock(Input, num_modes))*factorial_normalization(idx_to_fock(Output, num_modes)))**2 

#generalize to lists of input and output states:
def Dist_Amplitudes_idx(Inputs, Outputs, U, S):
    Inputs = np.atleast_2d(Inputs) #handly 1 state only
    Outputs = np.atleast_2d(Outputs)
    #for a given list of inputs and outputs, calculate the corresponding transition amplitudes. There are two functions here, one takes index vectors and one fock vectors
    Amps = np.zeros((len(Inputs),len(Outputs)), dtype=np.complex128) 
    for i, Input in enumerate(Inputs):
        for j, Output in enumerate(Outputs):
            Amps[i,j] = dist_amplitude_idx(Input, Output, U, S)
    return Amps

def Dist_Amplitudes_fock(Inputs, Outputs, U, S):
    Inputs = np.atleast_2d(Inputs)
    Outputs = np.atleast_2d(Outputs)
    Amps = np.zeros((len(Inputs),len(Outputs)), dtype=np.complex128) 
    for i, Input in enumerate(Inputs):
        for j, Output in enumerate(Outputs):
            Amps[i,j] = dist_amplitude_fock(Input, Output, U, S)
    return Amps




#%%Amplitude array class
class Dist_Prob_Phi:
    #in contrast to the other phi function, this already calculates the probability as in ||^2, hence the BB* in the calculation above
    def __init__(self, Inputs: np.ndarray, Outputs: np.ndarray, U: np.ndarray, S: np.ndarray, fock=False):
        self.Inputs = Inputs
        self.Outputs = Outputs
        self.U = U
        self.S = S
        self.fock = fock
    def get_probabilities(self) -> np.ndarray:
        if not self.fock:
            return Dist_Amplitudes_idx(self.Inputs, self.Outputs, self.U, self.S)
        else:
            return Dist_Amplitudes_fock(self.Inputs, self.Outputs, self.U, self.S)


