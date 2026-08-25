# ==============================================================================
# Qfóton: Hardware-Aware Silicon Photonic Quantum Compiler & Simulator
# Copyright (c) 2026 Atharve and the Qfóton Contributors. All rights reserved.
# Released under the MIT License.
# ==============================================================================

"""
Qfóton: Reck Universal Triangular SU(N) Mesh Compiler (PRL 1994).
Grounding:
  "Experimental realization of any discrete unitary operator",
  M. Reck, A. Zeilinger, H. J. Bernstein, P. Bertani,
  Phys. Rev. Lett. 73, 58-61 (1994). https://doi.org/10.1103/PhysRevLett.73.58

Decomposes any N x N unitary into a triangular mesh of N(N-1)/2 MZIs.
Optical Depth = 2N - 3 (Asymmetric depth, double Clements architecture).
"""

import numpy as np
from typing import List, Tuple, Dict

def reck_decompose(U: np.ndarray) -> Tuple[List[Tuple[int, int, float, float]], np.ndarray]:
    """
    Decomposes an N x N unitary matrix U into a triangular Reck MZI mesh.
    
    Returns:
        mzi_list: List of tuples (mode_1, mode_2, theta, phi)
        diag_phases: 1D array of diagonal phase screen angles
    """
    N = U.shape[0]
    U_curr = U.copy().astype(complex)
    mzi_list = []
    
    for i in range(N - 1, 0, -1):
        for j in range(i):
            m1 = j
            m2 = j + 1
            u1 = U_curr[i, m1]
            u2 = U_curr[i, m2]
            
            if np.abs(u1) < 1e-15:
                theta = 0.0
                phi = 0.0
            else:
                phi = float(np.angle(u1) - np.angle(u2))
                theta = float(np.arctan2(np.abs(u1), np.abs(u2)))
            
            c = np.cos(theta)
            s = np.sin(theta)
            T_dag_2x2 = np.array([
                [np.exp(-1j * phi) * c, np.exp(-1j * phi) * s],
                [-s, c]
            ], dtype=complex)
            
            T_dag = np.eye(N, dtype=complex)
            T_dag[m1:m2+1, m1:m2+1] = T_dag_2x2
            U_curr = U_curr @ T_dag
            mzi_list.append((m1, m2, theta, phi))
            
    diag_phases = np.diag(U_curr)
    return mzi_list, diag_phases

def reconstruct_reck_unitary(mzi_list: List[Tuple], diag_phases: np.ndarray, N: int) -> np.ndarray:
    """
    Reconstructs the original N x N unitary matrix from Reck MZI parameters.
    """
    U_rec = np.diag(diag_phases)
    for m1, m2, theta, phi in reversed(mzi_list):
        c = np.cos(theta)
        s = np.sin(theta)
        T_2x2 = np.array([
            [np.exp(1j * phi) * c, -s],
            [np.exp(1j * phi) * s, c]
        ], dtype=complex)
        T = np.eye(N, dtype=complex)
        T[m1:m2+1, m1:m2+1] = T_2x2
        U_rec = U_rec @ T
    return U_rec

def compute_reck_metrics(U: np.ndarray) -> Dict:
    """
    Computes comparative metrics for Reck triangular architecture vs Clements.
    """
    N = U.shape[0]
    mzi_list, diag_phases = reck_decompose(U)
    U_rec = reconstruct_reck_unitary(mzi_list, diag_phases, N)
    recon_error = float(np.linalg.norm(U - U_rec))
    
    return {
        'num_modes': N,
        'total_mzi_count': len(mzi_list),
        'max_optical_depth': max(1, 2 * N - 3),
        'reconstruction_error': recon_error,
        'mzi_schedule': mzi_list,
        'diagonal_phases': diag_phases
    }
