# ==============================================================================
# Qfóton: Full-Stack Silicon Photonic Quantum Computing & Compiler Suite
# Copyright (c) 2026 Atharve and the Qfóton Contributors. All rights reserved.
# Released under the MIT License.
# ==============================================================================

"""
Qfóton: Spontaneous Four-Wave Mixing (SFWM) Photon-Pair Source (Optica 2021).
Simulates on-chip third-order non-linear chi^(3) single-photon generation in silicon micro-rings.
"""

import numpy as np
from typing import Dict

class SFWMPhotonSource:
    def __init__(self, q_factor: float = 1e5, radius_um: float = 15.0, gamma_n2: float = 300.0):
        self.q = q_factor
        self.radius = radius_um
        self.gamma = gamma_n2 # Non-linear parameter (W^-1 m^-1)
        self.wavelength_pump_nm = 1550.0

    def simulate_pair_generation(self, pump_power_mw: float = 5.0) -> Dict:
        p_w = pump_power_mw * 1e-3
        # Generation rate R = (gamma * L * P)^2 * (FSR / 2pi)
        length_m = 2 * np.pi * self.radius * 1e-6
        pair_rate_hz = (self.gamma * length_m * p_w)**2 * 1.2e8
        
        # Coincidence-to-Accidental Ratio (CAR)
        accidental_rate = (pair_rate_hz * 1e-9)**2 * 1e9
        car = pair_rate_hz / (accidental_rate + 1e-6)
        car = float(np.clip(car, 100.0, 3500.0))
        
        # Heralded single photon purity g^(2)(0)
        g2_zero = float(0.002 + 0.0005 * pump_power_mw)
        
        return {
            'pump_power_mw': pump_power_mw,
            'pair_generation_rate_khz': pair_rate_hz / 1000.0,
            'car_ratio': car,
            'g2_heralded_purity': g2_zero,
            'spectral_brightness': pair_rate_hz / (pump_power_mw * 0.05)
        }
