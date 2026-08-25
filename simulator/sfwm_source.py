# ==============================================================================
# Qfóton: Hardware-Aware Silicon Photonic Quantum Compiler & Simulator
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
    """
    Spontaneous Four-Wave Mixing photon-pair source in a silicon micro-ring resonator.

    Calibrated against published experimental results:
      - Silverstone et al., Nat. Photon. 8, 104 (2014): ~1 MHz pairs at 0.5 mW
      - Grassani et al., Optica 2, 88 (2015): ~10 MHz pairs at 1 mW in high-Q ring
      - Reimer et al., Science 351, 6278 (2016): Q~2.4e5, CAR ~1000 at low pump

    Pair rate scales as P^2 (SFWM is chi^(3), four-photon process).
    CAR = R_pair / R_acc where R_acc = 2 * tau_coinc * R_s * R_i (Mandel & Wolf).
    """
    def __init__(self, q_factor: float = 1e5, radius_um: float = 15.0, gamma_n2: float = 300.0,
                 tau_coincidence_ns: float = 1.0, dark_count_rate_hz: float = 12.0,
                 n_group: float = 4.2):
        self.q = q_factor
        self.radius = radius_um
        self.gamma = gamma_n2           # Nonlinear parameter (W^-1 m^-1)
        self.wavelength_pump_nm = 1550.0
        self.tau_coinc = tau_coincidence_ns * 1e-9  # Coincidence window (s)
        self.R_dark = dark_count_rate_hz            # SNSPD dark count rate (Hz)
        self.n_g = n_group                          # Group index in 220nm SOI

    def simulate_pair_generation(self, pump_power_mw: float = 5.0) -> Dict:
        p_w = pump_power_mw * 1e-3  # Bus waveguide power (W)

        # --- Pair generation rate ---
        # SFWM pair rate in a micro-ring: R_pair = eta * P^2
        # where eta is the generation efficiency (pairs / s / W^2)
        # Calibration: Grassani et al. (Optica 2015) report ~10 MHz at 1 mW
        # in a Q ~ 10^5 silicon ring (R = 15 um, gamma ~ 300 W^-1 m^-1).
        # This gives eta ~ 10e6 / (1e-3)^2 = 1e13 pairs/s/W^2 at Q = 1e5.
        # eta scales as Q^2 (cavity enhancement of pump circulating power).
        eta_ref = 1e13  # pairs/s/W^2 at Q_ref = 1e5
        q_ref = 1e5
        eta = eta_ref * (self.q / q_ref) ** 2
        pair_rate_hz = eta * (p_w ** 2)

        # --- CAR computation (Mandel & Wolf, Optical Coherence) ---
        # Singles rates: each detector sees pair photons + dark counts + stray light
        R_signal = pair_rate_hz + self.R_dark
        R_idler = pair_rate_hz + self.R_dark

        # Accidental coincidence rate:
        #   R_acc = 2 * tau_coinc * R_signal * R_idler
        # At low pair rates (R_pair << 1/tau_coinc), CAR ~ 1 / (2 * tau * R_pair)
        # At high pair rates, multi-pair contamination dominates
        R_accidental = 2.0 * self.tau_coinc * R_signal * R_idler

        # CAR = R_pair / R_acc (floor at 1.0 by definition)
        car = max(1.0, float(pair_rate_hz / (R_accidental + 1e-30)))

        # Heralded g^(2)(0) from multi-pair contamination
        # For thermal-like SFWM: g^(2)(0) ~ 2*mu where mu = R_pair * tau_coinc
        # is the mean photon pair number per coincidence window
        mu = pair_rate_hz * self.tau_coinc
        g2_zero = float(max(2.0 * mu, 1e-4))

        return {
            'pump_power_mw': pump_power_mw,
            'pair_generation_rate_khz': pair_rate_hz / 1000.0,
            'car_ratio': car,
            'g2_heralded_purity': g2_zero,
            'spectral_brightness': pair_rate_hz / (pump_power_mw * 0.05),
            'accidental_rate_hz': float(R_accidental),
            'coincidence_window_ns': self.tau_coinc * 1e9,
            'generation_efficiency_per_w2': float(eta),
            'mean_pairs_per_window': float(mu)
        }


