# ==============================================================================
# Qfóton: Full-Stack Silicon Photonic Quantum Computing & Compiler Suite
# Copyright (c) 2026 Atharve and the Qfóton Contributors. All rights reserved.
# Released under the MIT License.
# ==============================================================================

"""
Knill-Laflamme-Milburn (KLM) Photonic Controlled-NOT (CNOT) Gate.
"""
from typing import Tuple

class KLMPhotonicCNOT:
    def __init__(self):
        self.success_probability = 1.0 / 9.0
        self.fidelity = 0.994

    def apply_cnot_truth_table(self, control: int, target: int) -> Tuple[int, int]:
        c_out = control
        t_out = target ^ control
        return c_out, t_out
