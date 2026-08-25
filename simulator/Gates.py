# -*- coding: utf-8 -*-
# ==============================================================================
# Qfóton: Hardware-Aware Silicon Photonic Quantum Compiler & Simulator
# Copyright (c) 2026 Atharve and the Qfóton Contributors. All rights reserved.
# Released under the MIT License.
# ==============================================================================
"""
Created on Fri Mar  7 09:24:16 2025

@author: Hüttenbrenner

Here, the different logic gates are implemented as matrices
"""
import numpy as np
from numba import njit
#%%Functions to generate gates that have dependency on parameters

#convert degre to radiant with np.radians(Angle_array) / radian to degree with np.degrees(Angle_array)


#phase shifter
def P(phi,mode): #mode specifies which mode gets the phase shift (0 or one)
    #input as degree! convert to radians
    phi = np.radians(phi)
    P=np.eye(2, dtype= np.complex128)
    P[mode,mode] = np.exp(1j*phi)
    return P
#NS BS
def BS_NS(theta, phi): 
    #Input as degree! convert angles to radians!
    theta = np.radians(theta)
    phi = np.radians(phi)
    BS = np.array([[np.cos(theta), -np.exp(1j*phi)*np.sin(theta)],
                   [np.exp(-1j*phi)*np.sin(theta), np.cos(theta)]], dtype=np.complex128)
    return BS
#standard beamsplitter
def BS(theta, phi): #might want to use phi_T and phi_R instead of just phi later
    #Input as degree! convert angles to radians!
    theta = np.radians(theta)
    phi = np.radians(phi)
    BS = np.array([[np.exp(1j*phi)*np.sin(theta), np.exp(-1j*phi)*np.cos(theta)],
                   [np.exp(1j*phi)*np.cos(theta), -np.exp(-1j*phi)*np.sin(theta)]], dtype=np.complex128)
    return BS


#general beamsplitter
def BS_gen(theta, phi_0, phi_R, phi_T): #might want to use phi_T and phi_R instead of just phi later
    #Input as degree! convert angles to radians!
    theta = np.radians(theta)
    phi_R = np.radians(phi_R)
    phi_T = np.radians(phi_T)
    phi_0 = np.radians(phi_0)
    BS = np.exp(1j*phi_0)*np.array([[np.exp(1j*phi_R)*np.sin(theta), np.exp(-1j*phi_T)*np.cos(theta)],
                   [np.exp(1j*phi_T)*np.cos(theta), -np.exp(-1j*phi_R)*np.sin(theta)]], dtype=np.complex128)
    return BS


#DFT
def DFT(N):
    w = np.exp(-1j*2*np.pi/N)
    W = np.zeros((N,N), dtype=np.complex128)
    for i in range(N):
        for j in range(N):
            W[i,j] = w**(i*j)
            
    return 1/np.sqrt(N) * W 


#%% yet another way of specifying BS

def bs_from_transmission_amplitude(t_amp, phi=0.0, BS_callback=BS):
    """
    Build a beamsplitter matrix in your convention from a transmission amplitude.

    Args
    ----
    t_amp : float
        Transmission amplitude (not intensity). Can be negative; sign is folded into phi.
        Must satisfy |t_amp| <= 1.
    phi : float, optional
        Phase (degrees) in your BS(...) convention.
    BS_callback : callable
        Your BS(theta, phi) function (angles in degrees).

    Returns
    -------
    np.ndarray
        2x2 complex beamsplitter matrix in your convention.
    """
    t_mag = abs(float(t_amp))
    if t_mag > 1 + 1e-12:
        raise ValueError("Transmission amplitude magnitude must be ≤ 1.")

    # Map |t| -> cos(theta)
    theta_deg = np.degrees(np.arccos(t_mag))

    # If t_amp is negative, fold the sign into a 180° phase shift for phi so that
    # the transmitted amplitude picks up the minus sign via e^{-i phi}.
    phi_eff = float(phi) + (180.0 if t_amp < 0 else 0.0)

    return BS_callback(theta_deg, phi_eff)

# (Optional) If someone hands you transmission INTENSITY T instead of amplitude:
def bs_from_transmission_intensity(T, phi=0.0, BS_callback=BS):
    """
    Build a BS from transmission intensity T (0..1) in your convention.
    """
    if T < -1e-12 or T > 1 + 1e-12:
        raise ValueError("Transmission intensity must be in [0, 1].")
    t_amp = np.sqrt(max(0.0, min(1.0, T)))
    return bs_from_transmission_amplitude(t_amp, phi=phi, BS_callback=BS)


#%% provide all used gates as np array

#hadamard
H = 1/np.sqrt(2)*np.array([[1,1],
                            [1,-1]], dtype = np.complex128)

Hi = 1/np.sqrt(2)*np.array([[1,1j],
                            [1j,1]], dtype = np.complex128)

H_ = 1/np.sqrt(2)*np.array([[-1,1],
                            [1,1]], dtype = np.complex128)

#%% make superpos with BS
def bs_from_superposition(a, b, atol=1e-12):
    """
    Given complex coefficients a, b (not necessarily normalized),
    return (theta_deg, phi_deg, delta_deg) such that

        BS(theta, phi) |1,0>  = e^{i phi} ( sin(theta) |1,0> + cos(theta) |0,1> )
        [Phase shifter on |0,1> output adds e^{i delta}]

    Together they realize:
        |1,0>  ->  a|1,0> + b|0,1>

    Returns angles in DEGREES.
    """
    # normalize (in case user didn’t)
    v = np.array([a, b], dtype=np.complex128)
    nrm = np.linalg.norm(v)
    if nrm < atol:
        raise ValueError("a and b cannot both be zero.")
    a, b = v / nrm

    # Magnitudes set theta
    sin_th = np.clip(np.abs(a), 0.0, 1.0)
    cos_th = np.clip(np.abs(b), 0.0, 1.0)
    # Guard against tiny numerical drift
    if abs(sin_th**2 + cos_th**2 - 1) > 1e-10:
        # Renormalize magnitudes if needed
        s = np.hypot(sin_th, cos_th)
        sin_th /= s
        cos_th /= s

    theta = np.arctan2(sin_th, cos_th)   # radians

    # Phases: choose global phase to match phase of 'a'
    phi = np.angle(a)                     # radians
    # Relative phase needed on the |0,1> arm to match 'b'
    delta = (np.angle(b) - np.angle(a))   # radians, can be any 2π equivalent

    return np.degrees(theta), np.degrees(phi), np.degrees(delta)


def bs_from_superposition_no_extra_phase(a, b, phase_tol_deg=1e-6):
    """
    Same as above but assumes NO extra phase shifter on outputs.
    Only works if a and b share the same phase (within tolerance).
    Returns (theta_deg, phi_deg). Raises if not achievable.
    """
    theta_deg, phi_deg, delta_deg = bs_from_superposition(a, b)
    # Needs delta ≈ 0 mod 360°
    # Wrap to (-180, 180]
    delta_wrapped = (delta_deg + 180) % 360 - 180
    if abs(delta_wrapped) > phase_tol_deg:
        raise ValueError(
            "Target superposition has a nonzero relative phase between a and b. "
            "With the current BS parameterization, add an output phase δ on the |0,1> mode "
            f"of about {delta_wrapped:.6f} degrees, or extend the BS to have independent φ_T, φ_R."
        )
    return theta_deg, phi_deg

# # Example: target state (a, b) = (1/√2, i/√2)
# a = 1/np.sqrt(2)
# b = 1j/np.sqrt(2)

# theta_deg, phi_deg, delta_deg = bs_from_superposition(a, b)
# print(theta_deg, phi_deg, delta_deg)
# # -> theta ≈ 45°, set BS φ = arg(a) = 0°, and add output phase δ ≈ +90° on the |0,1> arm.

#%%Helper functions


def GenerateMatrix(matrix, involved_modes, num_modes):
    '''
    

    Parameters
    ----------
    matrix : np.ndarray
        Matrix that specifies how the gate acts on a single photon state between the specified modes
    involved_modes : np.ndarray
        index of the relevant modes, starting from ZERO from top down
    num_modes : int
        Number of modes in the total system

    Returns
    -------
    Lifted matrix that lives in a space of size num_modes x num_modes and acts on single photon states

    '''
    single_photon_matrix = np.eye(num_modes, dtype=np.complex128)
    for i, mode_j in enumerate(involved_modes):
        for k, mode_l in enumerate(involved_modes):
            single_photon_matrix[mode_j, mode_l] = matrix[i,k]
    
    return single_photon_matrix

#%%Class

class Gate:
    def __init__(self, matrix: np.ndarray, involved_modes, num_modes: int): #involved modes is a list or a numpy array
        self.involved_modes = np.array(involved_modes)
        self.matrix = matrix
        self.num_modes = num_modes
        self.single_photon_matrix = GenerateMatrix(matrix, involved_modes, num_modes)      






#%%test

# matrix = 1/np.sqrt(2)*np.array([[1,1],
#                                 [1,1]])

# involved_modes = np.array([0,1])
# num_modes = 6

# M = GenerateMatrix(matrix, involved_modes, num_modes)
