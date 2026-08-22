"""
Reck Triangular Unitary Decomposition (PRL 1994).
"""
import numpy as np
from typing import List, Tuple

def reck_decompose(U: np.ndarray) -> List[Tuple[int, int, float, float]]:
    N = U.shape[0]
    U_curr = U.copy().astype(complex)
    mzi_list = []
    for i in range(N - 1, 0, -1):
        for j in range(i):
            m1 = j
            m2 = j + 1
            theta = np.arctan2(np.abs(U_curr[i, m1]), np.abs(U_curr[i, m2]))
            phi = np.angle(U_curr[i, m1]) - np.angle(U_curr[i, m2])
            mzi_list.append((m1, m2, float(theta), float(phi)))
    return mzi_list
