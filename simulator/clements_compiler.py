"""
Clements Universal SU(N) Rectangular Mesh Decomposition (Optica 2016).
Decomposes any N x N unitary into N(N-1)/2 MZIs with equal optical depth.
"""
import numpy as np
from typing import List, Tuple

def clements_decompose(U: np.ndarray) -> List[Tuple[int, int, float, float]]:
    U_curr = U.copy().astype(complex)
    N = U_curr.shape[0]
    mzi_list = []
    
    for i in range(N - 1):
        if i % 2 == 0:
            for j in range(i + 1):
                m1 = i - j
                m2 = i - j + 1
                r = U_curr[N - 1 - j, m1]
                t = U_curr[N - 1 - j, m2]
                theta = np.arctan2(np.abs(r), np.abs(t)) if (np.abs(r) + np.abs(t)) > 1e-12 else 0.0
                phi = np.angle(r) - np.angle(t)
                mzi_list.append((m1, m2, float(theta), float(phi)))
                
                inv_bs = np.eye(N, dtype=complex)
                inv_bs[m1, m1] = np.cos(theta)
                inv_bs[m1, m2] = np.exp(1j * phi) * np.sin(theta)
                inv_bs[m2, m1] = -np.exp(-1j * phi) * np.sin(theta)
                inv_bs[m2, m2] = np.cos(theta)
                U_curr = U_curr @ inv_bs
        else:
            for j in range(i + 1):
                m1 = N - 1 - (i - j) - 1
                m2 = N - 1 - (i - j)
                r = U_curr[m2, j]
                t = U_curr[m1, j]
                theta = np.arctan2(np.abs(r), np.abs(t)) if (np.abs(r) + np.abs(t)) > 1e-12 else 0.0
                phi = np.angle(t) - np.angle(r)
                mzi_list.append((m1, m2, float(theta), float(phi)))
                
                inv_bs = np.eye(N, dtype=complex)
                inv_bs[m1, m1] = np.cos(theta)
                inv_bs[m1, m2] = np.exp(1j * phi) * np.sin(theta)
                inv_bs[m2, m1] = -np.exp(-1j * phi) * np.sin(theta)
                inv_bs[m2, m2] = np.cos(theta)
                U_curr = inv_bs @ U_curr
                
    return mzi_list
