# ==============================================================================
# Qfóton: Hardware-Aware Silicon Photonic Quantum Compiler & Simulator
# Copyright (c) 2026 Atharve and the Qfóton Contributors. All rights reserved.
# Released under the MIT License.
# ==============================================================================

"""
Qfóton: MATLAB & Simulink Co-Simulation Bridge
Exports compiled Clements MZI phase angles to MATLAB (.m) and Simulink parameter blocks
for electro-thermal micro-heater voltage control and SPICE co-simulation.
"""

import os
import json
import numpy as np
from typing import List, Tuple, Dict

class MatlabSimulinkBridge:
    def __init__(self, v_pi: float = 3.2, heater_resistance_ohms: float = 120.0, dac_resolution_bits: int = 16):
        self.v_pi = v_pi
        self.r_heater = heater_resistance_ohms
        self.dac_bits = dac_resolution_bits

    def calculate_heater_voltages(self, mzi_schedule: List) -> List[Dict]:
        control_signals = []
        for idx, item in enumerate(mzi_schedule):
            if len(item) == 5:
                op, m1, m2, theta, phi = item
            else:
                m1, m2, theta, phi = item
                
            # Phase is proportional to dissipated electrical power: phi = pi * (V / V_pi)^2
            phi_norm = np.mod(phi, 2 * np.pi)
            v_phi = self.v_pi * np.sqrt(phi_norm / np.pi)
            
            # Beam splitter mixing angle voltage
            theta_norm = np.mod(theta, np.pi)
            v_theta = self.v_pi * np.sqrt(theta_norm / np.pi)
            
            power_mw = (v_phi ** 2 / self.r_heater) * 1000.0
            
            control_signals.append({
                'mzi_index': idx + 1,
                'modes': (int(m1), int(m2)),
                'theta_rad': float(theta),
                'theta_voltage_v': float(np.round(v_theta, 4)),
                'phi_rad': float(phi),
                'phi_voltage_v': float(np.round(v_phi, 4)),
                'dissipated_power_mw': float(np.round(power_mw, 2))
            })
        return control_signals

    def export_matlab_script(self, control_signals: List[Dict], output_path: str):
        lines = [
            "% Qfóton - MATLAB / Simulink Photonic Quantum Co-Simulation Script",
            "% Auto-generated for Silicon Photonic Thermal Phase Shifter DACs",
            "clear; clc;",
            f"V_pi = {self.v_pi}; % Pi-voltage for thermo-optic phase shifters (V)",
            f"R_heater = {self.r_heater}; % Heater resistance (Ohms)",
            f"DAC_bits = {self.dac_bits}; % Digital-to-Analog Converter resolution",
            "",
            "% MZI Channel Control Table [MZI_ID, Mode_A, Mode_B, V_theta (V), V_phi (V), Power (mW)]",
            "MZI_Control_Table = ["
        ]
        for s in control_signals:
            lines.append(f"    {s['mzi_index']}, {s['modes'][0]}, {s['modes'][1]}, {s['theta_voltage_v']}, {s['phi_voltage_v']}, {s['dissipated_power_mw']};")
        lines.extend([
            "];",
            "",
            "% Plot Thermal Dissipation per Channel",
            "figure('Name', 'Qfoton Silicon Photonic DAC Control Voltages', 'Color', 'w');",
            "bar(MZI_Control_Table(:, 1), MZI_Control_Table(:, 5), 'FaceColor', [0.02 0.71 0.83]);",
            "xlabel('Mach-Zehnder Interferometer (MZI) Index');",
            "ylabel('Phase Shifter DAC Voltage (V)');",
            "title('Qfóton: Silicon Photonic Thermo-Optic Phase Shifter Control Voltages');",
            "grid on;",
            "disp('Qfóton MATLAB / Simulink Control Vector Loaded Successfully.');"
        ])
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
