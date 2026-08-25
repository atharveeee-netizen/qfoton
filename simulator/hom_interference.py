# ==============================================================================
# Qfóton: Hardware-Aware Silicon Photonic Quantum Compiler & Simulator
# Copyright (c) 2026 Atharve and the Qfóton Contributors. All rights reserved.
# Released under the MIT License.
# ==============================================================================

"""
Qfóton: Hong-Ou-Mandel (HOM) Two-Photon Quantum Interference Engine.
Grounding:
  "Measurement of subpicosecond time intervals between two photons by interference",
  C. K. Hong, Z. Y. Ou, L. Mandel,
  Phys. Rev. Lett. 59, 2044-2046 (1987). https://doi.org/10.1103/PhysRevLett.59.2044

Simulates quantum bosonic coalescence at a 50:50 directional coupler,
spectral wavepacket overlap, temporal delay scan Delta tau, and calculates
non-classical coincidence visibility:
  V = M * (1 - g^(2)(0)) / (1 + g^(2)(0))
"""

import numpy as np
from typing import Dict, Tuple, List

class HongOuMandelSimulator:
    def __init__(self, coherence_time_ps: float = 0.85, indistinguishability_M: float = 0.982, g2_zero: float = 0.0038):
        self.tau_c = coherence_time_ps # Coherence time (ps)
        self.M = indistinguishability_M # Spatial/polarization overlap
        self.g2 = g2_zero # Second-order autocorrelation g^(2)(0)
        
        # HOM dip visibility
        self.visibility = self.M * ((1.0 - self.g2) / (1.0 + self.g2))

    def compute_coincidence_probability(self, delay_ps: float) -> float:
        """
        Calculates P_11 coincidence probability at relative delay delta_tau:
        P_11(Delta tau) = 0.5 * (1 - V * exp(-(Delta tau / tau_c)^2))
        """
        dip = self.visibility * np.exp(- (delay_ps / self.tau_c) ** 2)
        p11 = 0.5 * (1.0 - dip)
        return float(p11)

    def scan_hom_dip(self, delay_range_ps: float = 3.0, num_points: int = 51) -> Dict:
        delays = np.linspace(-delay_range_ps, delay_range_ps, num_points)
        coincidences = [self.compute_coincidence_probability(d) for d in delays]
        
        min_p11 = self.compute_coincidence_probability(0.0)
        max_p11 = 0.50
        
        return {
            'delays_ps': delays.tolist(),
            'coincidence_probabilities': coincidences,
            'hom_visibility_pct': self.visibility * 100.0,
            'dip_minimum_p11': min_p11,
            'dip_baseline_p11': max_p11,
            'coherence_time_ps': self.tau_c,
            'photon_indistinguishability_pct': self.M * 100.0,
            'heralded_g2_zero': self.g2
        }

    def render_ascii_hom_dip(self, width: int = 50, height: int = 12) -> str:
        """
        Renders a high-density ASCII / Unicode graph of the HOM coincidence dip.
        """
        delays = np.linspace(-2.5, 2.5, width)
        probs = [self.compute_coincidence_probability(d) for d in delays]
        
        y_min, y_max = 0.0, 0.55
        grid = [[' ' for _ in range(width)] for _ in range(height)]
        
        for x_idx, p in enumerate(probs):
            y_idx = int((p - y_min) / (y_max - y_min) * (height - 1))
            y_idx = max(0, min(height - 1, y_idx))
            grid[height - 1 - y_idx][x_idx] = '█' if abs(delays[x_idx]) < 0.2 else '■'
            
        lines = []
        lines.append(f"  P_11  ▲  HOM Coincidence Rate vs Relative Delay Δτ (Visibility = {self.visibility*100:.1f}%)")
        for r in range(height):
            val = y_max - (r / (height - 1)) * (y_max - y_min)
            label = f"{val:4.2f} │"
            row_str = "".join(grid[r])
            lines.append(f"{label}{row_str}")
        lines.append(f" 0.00 └" + "─" * width + "▶ Δτ (ps)")
        lines.append(f"       -2.5 ps                 0.0 ps (DIP)                 +2.5 ps")
        return "\n".join(lines)
