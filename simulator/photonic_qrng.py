# ==============================================================================
# Qfóton: Hardware-Aware Silicon Photonic Quantum Compiler & Simulator
# Copyright (c) 2026 Atharve and the Qfóton Contributors. All rights reserved.
# Released under the MIT License.
# ==============================================================================

"""
Qfóton: QRNG Beam-Splitter Simulation & NIST SP 800-22 Statistical Validation.

Simulates a photonic 50:50 beam-splitter measurement process using stochastic
Bernoulli sampling and validates the output against NIST SP 800-22 randomness tests.

NOTE: This is a software simulation of a photonic QRNG measurement model.
It uses numpy pseudorandom sampling to model the beam-splitter output distribution.
It is NOT connected to physical quantum random number generation hardware.
"""

import numpy as np
from typing import Dict

class PhotonicQRNG:
    def __init__(self, num_bits: int = 10000):
        self.n_bits = num_bits

    def generate_and_test_randomness(self) -> Dict:
        # Model 50:50 beam-splitter output as Bernoulli(p=0.5) trials (software simulation)
        quantum_bits = np.random.binomial(n=1, p=0.5, size=self.n_bits)
        
        # 1. NIST Frequency (Monobit) Test
        s_obs = np.abs(np.sum(2 * quantum_bits - 1)) / np.sqrt(self.n_bits)
        p_val_monobit = float(np.exp(-0.5 * (s_obs ** 2)))
        
        # 2. NIST Runs Test
        v_obs = 1 + np.sum(quantum_bits[1:] != quantum_bits[:-1])
        pi_hat = np.mean(quantum_bits)
        p_val_runs = float(np.exp(-0.5 * (((v_obs - 2 * self.n_bits * pi_hat * (1 - pi_hat)) / (2 * np.sqrt(2 * self.n_bits) * pi_hat * (1 - pi_hat))) ** 2)))
        
        # Determine NIST SP 800-22 compliance from actual test p-values
        monobit_pass = p_val_monobit > 0.01
        runs_pass = p_val_runs > 0.01
        nist_status = 'PASSED' if (monobit_pass and runs_pass) else 'FAILED'
        
        # Min-entropy from observed bit bias: H_min = -log2(max(p, 1-p))
        p_bias = np.mean(quantum_bits)
        min_entropy = float(-np.log2(max(p_bias, 1.0 - p_bias, 0.5 + 1e-12)))
        
        return {
            'total_quantum_bits_generated': self.n_bits,
            'monobit_frequency_p_value': p_val_monobit,
            'runs_test_p_value': p_val_runs,
            'nist_sp800_22_compliance': f'{nist_status} (Monobit p={p_val_monobit:.4f}, Runs p={p_val_runs:.4f})',
            'entropy_per_bit': min_entropy
        }
