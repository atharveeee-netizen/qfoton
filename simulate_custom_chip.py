# ==============================================================================
# Qfóton: Full-Stack Silicon Photonic Quantum Computing & Compiler Suite
# Copyright (c) 2026 Atharve and the Qfóton Contributors. All rights reserved.
# Released under the MIT License.
# ==============================================================================

"""
Qfóton: Universal Custom Chip Simulator & Gateway (simulate_custom_chip.py)
Allows users to paste or specify any arbitrary quantum circuit (OpenQASM, JSON, or Preset)
and compiles it into a physical Silicon Photonic MZI mesh with full physical simulation.
"""

import sys
import os
import argparse
import json
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from simulator.qasm_parser import OpenQASMTranspiler
from simulator.clements_compiler import clements_decompose
from simulator.thermal_crosstalk import ThermalCrossTalkOptimizer
from simulator.matlab_simulink_bridge import MatlabSimulinkBridge
from simulator.state_tomography import reconstruct_density_matrix, compute_quantum_metrics, plot_3d_density_matrix

PRESETS = {
    'bell': """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0], q[1];
measure q -> c;
""",
    'ghz3': """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg c[3];
h q[0];
cx q[0], q[1];
cx q[1], q[2];
measure q -> c;
""",
    'grover2': """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
h q[1];
cz q[0], q[1];
h q[0];
h q[1];
x q[0];
x q[1];
h q[1];
cx q[0], q[1];
h q[1];
x q[0];
x q[1];
h q[0];
h q[1];
measure q -> c;
""",
    'teleport': """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg c[3];
ry(pi/3) q[0];
h q[1];
cx q[1], q[2];
cx q[0], q[1];
h q[0];
measure q[0] -> c[0];
measure q[1] -> c[1];
"""
}

def simulate_custom_circuit(qasm_text: str, chip_name: str = "Custom Photonic QPU", headless: bool = False):
    print("=" * 80)
    print(f" Qfóton: COMPILING & SIMULATING CHIP -> [{chip_name}]")
    print("=" * 80)
    
    # 1. Parse QASM
    transpiler = OpenQASMTranspiler()
    num_qubits, U_circuit, gates = transpiler.parse_qasm_string(qasm_text)
    dim = 2 ** num_qubits
    num_photonic_modes = max(dim, 2 * num_qubits)
    
    print(f"Input Circuit: {num_qubits} Qubits | {len(gates)} Quantum Gates")
    print(f"Photonic Encoding: {num_photonic_modes} Dual-Rail Silicon Waveguides (SOI 220nm)")
    print()
    
    # 2. Decompose into Clements Silicon MZIs
    if dim < num_photonic_modes:
        U_mesh = np.eye(num_photonic_modes, dtype=complex)
        U_mesh[:dim, :dim] = U_circuit
    else:
        U_mesh = U_circuit
        
    mzi_schedule, diag_phases = clements_decompose(U_mesh)
    total_mzis = len(mzi_schedule)
    print(f"[+] Compiled into {total_mzis} Mach-Zehnder Interferometers (Optica 2016 Clements Architecture)")
    print(f"    First 3 Compiled MZI Phase Angles:")
    for idx, item in enumerate(mzi_schedule[:3]):
        if len(item) == 5:
            _, m1, m2, theta, phi = item
        else:
            m1, m2, theta, phi = item
        print(f"      MZI #{idx+1}: Modes ({m1}, {m2}) -> Theta: {theta:.4f} rad, Phi: {phi:.4f} rad")
    print()
    
    # 3. Simulate Thermal Cross-Talk & Auto-Calibration
    calibrator = ThermalCrossTalkOptimizer(num_mzis=total_mzis, coupling_strength=0.18)
    theta_targets = np.array([item[3] if len(item) == 5 else item[2] for item in mzi_schedule])
    cal_results = calibrator.benchmark_calibration(theta_targets)
    print(f"[+] Thermal Cross-Talk Analysis & Auto-Calibration:")
    print(f"    • Uncalibrated Fidelity (18% Thermal Bleed): {cal_results['uncalibrated_fidelity_pct']:.2f}% (Error: {cal_results['uncalibrated_error_rad']:.4f} rad)")
    print(f"    • Auto-Calibrated Pre-Distorted Fidelity:    {cal_results['calibrated_fidelity_pct']:.2f}% (Condition Number kappa = {cal_results['thermal_matrix_condition_number']:.2f})")
    print(f"    • Calibration Improvement Factor:          {cal_results['improvement_factor']:.1f}x")
    print()

    # 4. MATLAB / Simulink Control Script Generation
    bridge = MatlabSimulinkBridge(v_pi=3.2, heater_resistance_ohms=120.0)
    ctrl_signals = bridge.calculate_heater_voltages(mzi_schedule)
    matlab_out = os.path.join(BASE_DIR, "matlab", f"custom_chip_control.m")
    bridge.export_matlab_script(ctrl_signals, matlab_out)
    print(f"[+] Generated MATLAB/Simulink Electro-Thermal Model: matlab/custom_chip_control.m")
    print()

    # 5. Quantum State Output & Density Matrix
    initial_state = np.zeros(dim, dtype=complex)
    initial_state[0] = 1.0 # |00...0>
    final_state = U_circuit @ initial_state
    
    # Measurement shots simulation
    probs = np.abs(final_state) ** 2
    shots_dict = {}
    for idx, p in enumerate(probs):
        bitstr = bin(idx)[2:].zfill(num_qubits)
        shots_dict[bitstr] = int(round(p * 1000))
        
    rho = reconstruct_density_matrix(shots_dict, total_shots=1000)
    metrics = compute_quantum_metrics(rho, final_state)
    
    print(f"[+] Final Quantum State Metrics:")
    print(f"    • State Fidelity:       {metrics['fidelity_pct']:.2f}%")
    print(f"    • State Purity Tr(rho): {metrics['purity']:.4f}")
    print(f"    • Optical Transit Time: {0.03 * num_qubits:.2f} nanoseconds (Room Temp 300K)")
    print("=" * 80)
    
    is_headless = headless or os.environ.get("HEADLESS", "0") == "1" or os.environ.get("MPLBACKEND") == "Agg"
    if not is_headless and sys.stdout.isatty():
        print("\n[+] Plotting 3D Quantum State Tomography (Close 3D window to complete)...")
        plot_3d_density_matrix(rho, title=f"3D State Tomography: {chip_name} (Fidelity = {metrics['fidelity_pct']:.1f}%)")

def main():
    parser = argparse.ArgumentParser(description="Qfóton: Universal Custom Chip Simulator")
    parser.add_argument("--preset", choices=['bell', 'ghz3', 'grover2', 'teleport'], default='ghz3',
                        help="Run a built-in benchmark algorithm preset (bell, ghz3, grover2, teleport)")
    parser.add_argument("--qasm", type=str, default=None, help="Path to custom OpenQASM 2.0 file or inline QASM code")
    parser.add_argument("--chip-name", type=str, default="User Custom Chip", help="Display name for custom chip")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode without popup window")
    args = parser.parse_args()

    if args.qasm:
        if os.path.exists(args.qasm):
            with open(args.qasm, "r", encoding="utf-8") as f:
                qasm_str = f.read()
        else:
            qasm_str = args.qasm
        simulate_custom_circuit(qasm_str, chip_name=args.chip_name, headless=args.headless)
    else:
        preset_code = PRESETS[args.preset]
        simulate_custom_circuit(preset_code, chip_name=f"Preset: {args.preset.upper()} Algorithm", headless=args.headless)

if __name__ == '__main__':
    main()
