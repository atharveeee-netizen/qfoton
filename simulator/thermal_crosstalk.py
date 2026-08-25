# ==============================================================================
# Qfóton: Hardware-Aware Silicon Photonic Quantum Compiler & Simulator
# Copyright (c) 2026 Atharve and the Qfóton Contributors. All rights reserved.
# Released under the MIT License.
# ==============================================================================

"""
Qfóton: Silicon Photonic Thermal Cross-Talk & Real-Time Auto-Calibration Optimizer.
Grounding:
  "Mitigation of thermal crosstalk in reconfigurable silicon photonic networks",
  K. Milanizadeh et al., IEEE J. Sel. Top. Quantum Electron. 26, 6100508 (2020).
  "Universal Linear Optics",
  J. Carolan et al., Science 349, 711-716 (2015).

Models 2D thermal diffusion across micro-heaters K_{ij} = exp(-d_{ij} / lambda),
simulates parasitic phase bleed, and computes Moore-Penrose pseudo-inverse pre-distorted
DAC drive voltages to achieve 100% calibration restoration (> 99.8% fidelity).
"""

import numpy as np
from typing import List, Tuple, Dict

class ThermalCrossTalkOptimizer:
    def __init__(self, num_mzis: int, coupling_strength: float = 0.18, decay_length: float = 1.6):
        self.num_mzis = num_mzis
        self.alpha = coupling_strength
        self.decay = decay_length
        self.thermal_matrix = self._build_thermal_coupling_matrix()

    def _build_thermal_coupling_matrix(self) -> np.ndarray:
        K = np.zeros((self.num_mzis, self.num_mzis), dtype=float)
        for i in range(self.num_mzis):
            for j in range(self.num_mzis):
                dist = abs(i - j)
                if dist == 0:
                    K[i, j] = 1.0
                else:
                    K[i, j] = self.alpha * np.exp(-dist / self.decay)
        return K

    def apply_thermal_distortion(self, applied_phases: np.ndarray) -> np.ndarray:
        """Physical phase experienced on silicon chip = K * applied_phases"""
        return self.thermal_matrix @ applied_phases

    def calibrate_heater_drives(self, target_phases: np.ndarray) -> Tuple[np.ndarray, float]:
        """Calculates inverse pre-distorted phase commands: Phase_cmd = K^(-1) * Phase_target"""
        K_inv = np.linalg.pinv(self.thermal_matrix)
        calibrated_drives = K_inv @ target_phases
        
        # Verify physical phase after calibration
        actual_physical_phases = self.apply_thermal_distortion(calibrated_drives)
        residual_error = float(np.linalg.norm(actual_physical_phases - target_phases))
        return calibrated_drives, residual_error

    def benchmark_calibration(self, target_phases: np.ndarray) -> Dict:
        # 1. Uncalibrated case
        uncal_actual = self.apply_thermal_distortion(target_phases)
        uncal_err = float(np.mean(np.abs(uncal_actual - target_phases)))
        uncal_fid = float(np.clip(1.0 - 1.8 * uncal_err, 0.0, 1.0)) * 100.0

        # 2. Pre-distorted calibrated case (no artificial floor)
        cal_drives, residual = self.calibrate_heater_drives(target_phases)
        cal_actual = self.apply_thermal_distortion(cal_drives)
        cal_err = float(np.mean(np.abs(cal_actual - target_phases)))
        cal_fid = float(np.clip(1.0 - 1.8 * cal_err, 0.0, 1.0)) * 100.0

        # Matrix conditioning for research-grade thermal inverse analysis
        cond_number = float(np.linalg.cond(self.thermal_matrix))

        return {
            'num_mzis': self.num_mzis,
            'thermal_coupling_pct': self.alpha * 100.0,
            'uncalibrated_fidelity_pct': uncal_fid,
            'uncalibrated_error_rad': uncal_err,
            'calibrated_fidelity_pct': cal_fid,
            'calibrated_error_rad': cal_err,
            'residual_l2_norm': residual,
            'thermal_matrix_condition_number': cond_number,
            'improvement_factor': uncal_err / (cal_err + 1e-9)
        }

    def render_ascii_calibration_bars(self, target_phases: np.ndarray) -> str:
        """
        Renders an ASCII bar chart comparing uncalibrated vs calibrated phase errors per MZI.
        """
        uncal_actual = self.apply_thermal_distortion(target_phases)
        cal_drives, _ = self.calibrate_heater_drives(target_phases)
        cal_actual = self.apply_thermal_distortion(cal_drives)
        
        lines = []
        lines.append("  MZI# │ Target (rad) │ Uncalibrated (Bleed) │ Auto-Calibrated │ Error Restored")
        lines.append("  ─────┼──────────────┼──────────────────────┼─────────────────┼───────────────")
        for i in range(min(self.num_mzis, 8)):
            t = target_phases[i]
            u = uncal_actual[i]
            c = cal_actual[i]
            err_u = abs(u - t)
            err_c = abs(c - t)
            lines.append(f"  #{i+1:2d}  │    {t:6.3f}    │    {u:6.3f} (Δ={err_u:.3f}) │  {c:6.3f} (Δ={err_c:.4f}) │ ◄ [CALIBRATED]")
        lines.append("  ─────┴──────────────┴──────────────────────┴─────────────────┴───────────────")
        return "\n".join(lines)
