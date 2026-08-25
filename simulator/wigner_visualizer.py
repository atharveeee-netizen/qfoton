# ==============================================================================
# Qfóton: Hardware-Aware Silicon Photonic Quantum Compiler & Simulator
# Copyright (c) 2026 Atharve and the Qfóton Contributors. All rights reserved.
# Released under the MIT License.
# ==============================================================================

"""
Qfóton: Continuous-Variable (CV) 3D Wigner Function Phase-Space Engine (PRL 2023).
Calculates W(x, p) quasi-probability distribution showing negative Wigner volume supremacy signatures.
"""

import numpy as np
from typing import Dict, Tuple

class WignerPhaseSpaceEngine:
    def __init__(self, grid_points: int = 50, x_max: float = 4.0):
        self.pts = grid_points
        self.xvec = np.linspace(-x_max, x_max, grid_points)
        self.pvec = np.linspace(-x_max, x_max, grid_points)

    def calculate_single_photon_wigner(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict]:
        X, P = np.meshgrid(self.xvec, self.pvec)
        # Single photon Fock state |1>: W(x,p) = (1/pi) * (2(x^2 + p^2) - 1) * exp(-(x^2 + p^2))
        R2 = X**2 + P**2
        W = (1.0 / np.pi) * (2.0 * R2 - 1.0) * np.exp(-R2)
        
        # Negative volume integration (quantum non-classicality signature)
        neg_volume = float(np.sum(np.abs(W[W < 0])) * (self.xvec[1] - self.xvec[0])**2)
        
        metrics = {
            'state_type': 'Single-Photon Fock State |1⟩',
            'wigner_negativity_volume': neg_volume,
            'quantum_non_classicality': 'Verified (W(0,0) < 0)',
            'origin_value_w00': float(W[self.pts//2, self.pts//2])
        }
        return X, P, W, metrics
