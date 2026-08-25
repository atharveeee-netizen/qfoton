# -*- coding: utf-8 -*-
# ==============================================================================
# Qfóton: Hardware-Aware Silicon Photonic Quantum Compiler & Simulator
# Copyright (c) 2026 Atharve and the Qfóton Contributors. All rights reserved.
# Released under the MIT License.
# ==============================================================================
"""
Created on Fri Mar 21 13:32:34 2025

@author: Hüttenbrenner
"""
import numpy as np
from numba import njit
from .Basis import *

def apply_click_mask(Fock_Basis, photon_present, no_photon_present):
    '''
    

    Parameters
    ----------
    Fock_Basis : TYPE
        List of (all) fock basis states.
    photon_present : TYPE
        Specifies in which mode there must be atleast one photon. A detector (non number resolving) would click if inserted at this point.
    no_photon_present : TYPE
        Specifies in which mode there must not be a photon. A detector must not click if inserted at this point.

    Returns
    -------
    TYPE
        The Basis states that fullfil the click-mask's conditions.

    '''
    # Get indices of conditions
    must_be_nonzero_idx = photon_present.nonzero()[0]        # Indices where values must be ≥1
    must_be_zero_idx = no_photon_present.nonzero()[0]        # Indices where values must be 0

    # Create boolean masks
    condition_nonzero = np.all(Fock_Basis[:, must_be_nonzero_idx] >= 1, axis=1)  # All required positions must be ≥1
    condition_zero = np.all(Fock_Basis[:, must_be_zero_idx] == 0, axis=1)        # All required positions must be 0

    # Combine both conditions
    valid_rows = condition_nonzero & condition_zero

    # Extract valid rows
    return Fock_Basis[valid_rows]

def remove_collision_states(Fock_states):
    # Create an empty list to store valid rows
    valid_rows = []
    
    # Iterate over each row in Fock_states
    for fock_state in Fock_states:
        # If no photon number is greater than 1, add the row to valid_rows
        if all(photon_number <= 1 for photon_number in fock_state):
            valid_rows.append(fock_state)
    
    # Convert valid_rows back into a numpy array and return it
    return np.array(valid_rows)

def remove_collision_free_states(Fock_states):
    # Create an empty list to store valid rows
    valid_rows = []
    
    # Iterate over each row in Fock_states
    for fock_state in Fock_states:
        # If no photon number is greater than 1, add the row to valid_rows
        if not all(photon_number <= 1 for photon_number in fock_state):
            valid_rows.append(fock_state)
    
    # Convert valid_rows back into a numpy array and return it
    return np.array(valid_rows)


def apply_mask(Fock_states, Modes_with_restriction, Required_photon_numbers, exclude = 0):
    '''
    Parameters
    ----------
    Fock_states: np.ndarray of all Fock states we want test for the condition, maybe the entire basis
    Modes_with_restriction : np.ndarray
        Array of all mode indices, where a certain photon number needs to/ must not be present
    Required_photon_numbers : np.ndarray
        Photon numbers for said modes
    exclude : Int, optional
        If it is 0, states that agree in all specifications are returned.
        If it is 1, states that share any similarity with the specificaion are returned
        If it is 2, all states that match exactly the specifications are excluded. 
        If 3, states that share any similarity with the specified requirements (i.e. a single photon number for a given mode) are excluded. 
        The default is 0.

    Returns
    -------
    valid_rows: np.ndarray
        Array of all valid states.

    '''
    if exclude >3 or exclude <0:
        print('exclude paramter must be 0,1,3 or 2')
    
    valid_rows = []
    
    if exclude == 0:
        for fock_state in Fock_states:
            if all(photon_number == required_photon_number for (photon_number, required_photon_number) in zip(fock_state[Modes_with_restriction], Required_photon_numbers)): 
                valid_rows.append(fock_state)
        return np.array(valid_rows)
    
    if exclude == 1:
        for fock_state in Fock_states:
            if any(photon_number == required_photon_number for (photon_number, required_photon_number) in zip(fock_state[Modes_with_restriction], Required_photon_numbers)): 
                valid_rows.append(fock_state)
        return np.array(valid_rows)    
           
     
    if exclude == 2:
         for fock_state in Fock_states:
             if not all(photon_number == required_photon_number for (photon_number, required_photon_number) in zip(fock_state[Modes_with_restriction], Required_photon_numbers)):
                 valid_rows.append(fock_state)
         return np.array(valid_rows)  
     
        
    if exclude == 3:
         for fock_state in Fock_states:
             if not any(photon_number == required_photon_number for (photon_number, required_photon_number) in zip(fock_state[Modes_with_restriction], Required_photon_numbers)):
                 valid_rows.append(fock_state)
         return np.array(valid_rows)

def round_array(Arr, digits):
    return np.round(Arr.real, digits) + 1j * np.round(Arr.imag, digits)    
#%%Test
# num_photons = 4
# num_modes = 4

# basis = Basis(num_photons, num_modes)
# cut_down_basis = apply_mask(basis.fock, [1,1,1], [0,1,2], 1) #this removes all states with 0,1, or 2 photons in mode 1
