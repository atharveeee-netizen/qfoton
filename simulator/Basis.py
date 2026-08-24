# -*- coding: utf-8 -*-
# ==============================================================================
# Qfóton: Full-Stack Silicon Photonic Quantum Computing & Compiler Suite
# Copyright (c) 2026 Atharve and the Qfóton Contributors. All rights reserved.
# Released under the MIT License.
# ==============================================================================
"""
Created on Thu Mar  6 11:05:45 2025

@author: Hüttenbrenner
"""

'''
To do:
   
'''
import numpy as np
from numba import njit
import itertools as it
from typing import List, Tuple, Optional

#%% helper functions
def generate_idx_basis(num_photons, num_modes):
    #idx is mode of each photon: the index is the photon index, and the number written in the element is which mode the photon is in: ie [0,0] means two photons, both in mode zero. Note that we cannot infer the total number of modes from this
    idx_basis = (it.combinations_with_replacement(range(num_modes), num_photons))
    return np.array(list(idx_basis))


def generate_idx_basis_adv(
    num_photons: int,
    num_modes: int,
    clicks: Optional[List[int]] = None,
    no_clicks: Optional[List[int]] = None,
    remove_bunching: Optional[List[int]] = None,
) -> np.ndarray:
    """
    Generate idx basis (rows of length num_photons with sorted mode indices) under constraints:
      - clicks: modes that must contain >=1 photon
      - no_clicks: modes that must contain 0 photons
      - remove_bunching: modes that must contain <=1 photon

    Returns: np.ndarray with shape (K, num_photons), dtype=int.
             If constraints are impossible, returns empty array with shape (0, num_photons).
    """
    clicks = set(clicks or [])
    no_clicks = set(no_clicks or [])
    remove_bunching = set(remove_bunching or [])

    # basic validation
    if any(m < 0 or m >= num_modes for m in clicks | no_clicks | remove_bunching):
        raise ValueError("Mode indices out of range.")
    if clicks & no_clicks:
        return np.empty((0, num_photons), dtype=int)
    if num_photons < len(clicks):
        return np.empty((0, num_photons), dtype=int)

    # per-mode min/max occupancies
    occ_min = [0] * num_modes
    occ_max = [num_photons] * num_modes
    for m in range(num_modes):
        if m in no_clicks:
            occ_min[m] = 0
            occ_max[m] = 0
        elif m in clicks and m in remove_bunching:
            # exactly one
            occ_min[m] = 1
            occ_max[m] = 1
        elif m in clicks:
            occ_min[m] = 1
            occ_max[m] = num_photons
        elif m in remove_bunching:
            occ_min[m] = 0
            occ_max[m] = 1
        else:
            occ_min[m] = 0
            occ_max[m] = num_photons
        if occ_min[m] > occ_max[m]:
            return np.empty((0, num_photons), dtype=int)

    min_total = sum(occ_min)
    if min_total > num_photons:
        return np.empty((0, num_photons), dtype=int)

    remaining = num_photons - min_total
    caps = [occ_max[m] - occ_min[m] for m in range(num_modes)]

    # order modes by tightest capacity first to prune early
    mode_order = sorted(range(num_modes), key=lambda m: (caps[m], occ_min[m]))

    # precompute suffix capacity: total capacity available after position i
    suffix_cap = [0] * (len(mode_order) + 1)
    for i in range(len(mode_order) - 1, -1, -1):
        suffix_cap[i] = suffix_cap[i + 1] + caps[mode_order[i]]

    rows: List[List[int]] = []
    delta = [0] * num_modes
    modes_arr = np.arange(num_modes, dtype=int)

    def backtrack(i: int, rem: int):
        if i == len(mode_order):
            if rem == 0:
                # build occupancy and convert to idx row
                occ = [occ_min[m] + delta[m] for m in range(num_modes)]
                row = np.repeat(modes_arr, occ).tolist()
                rows.append(row)
            return

        # prune if even filling all remaining caps can't absorb rem
        if rem > suffix_cap[i]:
            return

        m = mode_order[i]
        ub = min(caps[m], rem)  # we already accounted for occ_min in 'remaining'
        # try allocating x extra photons to mode m
        for x in range(ub + 1):
            need = rem - x
            # further prune: need must be <= capacity of future modes
            if need > suffix_cap[i + 1]:
                continue
            delta[m] = x
            backtrack(i + 1, need)
        delta[m] = 0

    backtrack(0, remaining)

    if not rows:
        return np.empty((0, num_photons), dtype=int)
    return np.asarray(rows, dtype=int)


@njit()
def fock_to_idx(fock_state):
    count = 0
    idx_state = np.zeros(np.sum(fock_state),dtype=np.dtype('int64')) #this fails if the photon number is changed midway, but then the entire fock basis is wrong anyways
    for j, photons in enumerate(fock_state):
        while photons > 0:
            idx_state[count] = j
            count += 1
            photons -= 1
    return idx_state


def fock_list_to_idx_list(fock_states):
    idx_states = []
    for i,fock_state in enumerate(fock_states):
        count = 0
        idx_state = np.zeros(np.sum(fock_state),dtype=np.dtype('int64')) #this fails if the photon number is changed midway, but then the entire fock basis is wrong anyways
        for j, photons in enumerate(fock_state):
            while photons > 0:
                idx_state[count] = j
                count += 1
                photons -= 1
        idx_states.append(tuple(idx_state))
    idx_states = np.array(idx_states)
    return idx_states

@njit()
def factorial(n):
    result = np.prod(np.arange(1,n+1,dtype=np.dtype('uint64')))
    return result
@njit()
def BE(N,k):
    '''
    

    Parameters
    ----------
    N : integer
        photon number.
    k : integer
        mode number.

    Returns
    -------
    Number of possible combinations when distributing N indistinguishable particles onto k cells (modes)

    '''
    return np.int64(factorial(N+k-1)/(factorial(k-1)*factorial(N)))


def fock_to_Rn(fock_state):
    count = 0
    N = np.sum(fock_state)
    k = fock_state.size
    C=BE(N,k)
    Rn_state = np.zeros(C,dtype=np.dtype('int64'))
    for j, photons in enumerate(fock_state):
        N-=photons
        count += N
        if N == 0:
            Rn_state[count]=1
            N = - 1
    return Rn_state

def idx_to_fock(idx_state, num_modes):
    fock_state = np.zeros(num_modes, dtype=int)
    unique, counts = np.unique(idx_state, return_counts=True)
    fock_state[unique] = counts
    return fock_state

def idx_list_to_fock_list(idx_states, num_modes):
    fock_basis = []
    for i, idx_state in enumerate(idx_states):
        fock_state = np.zeros(num_modes, dtype=int)
        unique, counts = np.unique(idx_state, return_counts=True)
        fock_state[unique] = counts
        fock_basis.append(tuple(fock_state))
        photons_per_mode = np.array(fock_basis,dtype=np.dtype('int'))
    return photons_per_mode #this is the fock basis

#%%Class Methods
def MakePhotonsPerMode(num_photons, num_modes):
    '''
    This is the Fock Basis in Patrik's code

    Parameters
    ----------
    photon_number : integer specifying number of photons
    mode_number : integer specifying number of modes

    Returns
    -------
    np.array photons_per_mode
        Corresponds to Fock-Basis in Patrik's code
        Each basis vetor i corresponds to p out of P photons in mode m, while there are M modes in total
        photons_per_mode[i] = numpy array that tells us what the i_th basis vector means in terms of photon distribution
        photons_per_mode[i,m] = number of photons that are in mode m when considering Basis vector i 

    '''
    idx_basis = generate_idx_basis(int(num_photons), int(num_modes))
    fock_basis = []
    for i, idx_state in enumerate(idx_basis):
        fock_state = np.zeros(num_modes, dtype=int)
        unique, counts = np.unique(idx_state, return_counts=True)
        fock_state[unique] = counts
        fock_basis.append(tuple(fock_state))
        photons_per_mode = np.array(fock_basis,dtype=np.dtype('int'))
    return photons_per_mode #this is the fock basis


def MakeRnBasis(num_photons, num_modes):
    N=BE(num_photons, num_modes)
    Basis = np.eye(N)
    return Basis


#%%Class

class Basis:
    def __init__(self, photon_number: int, mode_number: int):
        """Constructor to initialize two public integer members for photon and mode number."""
        self.photon_number    = photon_number
        self.mode_number      = mode_number
        self.Rn               = MakeRnBasis(photon_number, mode_number)  
        self.idx              = generate_idx_basis(photon_number, mode_number)
        self.fock             = MakePhotonsPerMode(photon_number, mode_number)#these correspond to the basis vector with the same index
        self.dimension        = BE(photon_number, mode_number)



    def set_numbers(self, new_photon_number, new_mode_number):
        """Updates members and makes a new basis. Photon and Mode number needs to be set updated this, so the basis is renewed"""
        self.photon_number    = new_photon_number
        self.mode_number      = new_mode_number
        self.Rn               = MakeRnBasis(new_photon_number, new_mode_number)
        self.idx              = generate_idx_basis(new_photon_number, new_mode_number)
        self.fock             = MakePhotonsPerMode(new_photon_number,new_mode_number)#these correspond to the basis vector with the same index
        self.dimension        = BE(new_photon_number, new_mode_number)



#%% test 
# p=2
# m=2

# idx = generate_idx_basis(p, m)

# F = MakePhotonsPerMode(p, m)
# #print(F)
# print('-----')
# #print(MakeRnBasis(F))


# from scipy.special import comb

# def BE_array(N, k):
#     return comb(N + k - 1, N, exact=True)


# BE_arr = BE_array(10, 16)

# Be_mine = BE(10,16) #overflows and gives 1 / 1 because the factorials get too large!