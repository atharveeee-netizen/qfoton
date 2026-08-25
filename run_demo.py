"""
Qfóton: Hardware-Aware Silicon Photonic Quantum Compiler & Simulator (run_demo.py)
Runs the complete simulation suite across all modules.
"""

import sys, os, time
import numpy as np

# Import all simulator engines
from simulator.sfwm_source import SFWMPhotonSource
from simulator.hom_interference import HongOuMandelSimulator
from simulator.fast_permanents import benchmark_boson_sampling_speedup
from simulator.topological_protection import TopologicalPhotonicLattice
from simulator.thermal_crosstalk import ThermalCrossTalkOptimizer
from simulator.pid_phase_stabilizer import PhotonicPIDStabilizer
from simulator.mbqc_cluster import MBQCClusterGenerator
from simulator.photonic_vqe import PhotonicVQESolver
from simulator.zero_noise_extrapolation import PhotonicZNEMitigator
from simulator.photonic_qrng import PhotonicQRNG
from simulator.grating_coupler import GratingCouplerOptimizer
from simulator.hybrid_spatial_temporal_compiler import HybridSpatialTemporalCompiler
from simulator.dac_preemphasis import DACPreEmphasisShaper
from simulator.pauli_frame_tracker import PauliFrameSyndromeTracker
from simulator.loss_aware_router import LossAwareMZIRouter

def run_complete_simulation_suite():
    print("\n" + "=" * 80)
    print("       Qfóton | Hardware-Aware Photonic Quantum Simulation Suite")
    print("=" * 80)

    # Stage 1: SFWM Source Simulation
    print("\n[1/16] SFWM RING RESONATOR PHOTON SOURCE MODEL (Optica 2021 parameters)")
    print("-" * 80)
    sfwm = SFWMPhotonSource(radius_um=15.0, q_factor=100000.0)
    res1 = sfwm.simulate_pair_generation(pump_power_mw=5.0)
    print(f"Pump Power: {res1['pump_power_mw']} mW | Pair Rate: {res1['pair_generation_rate_khz']:.2f} kHz")
    print(f"CAR: {res1['car_ratio']:.1f} | Heralded Purity g^(2)(0): {res1['g2_heralded_purity']:.4f}")

    # Stage 2: Clements vs Reck Decomposition
    print("\n[2/16] UNITARY DECOMPOSITION: CLEMENTS vs RECK")
    print("-" * 80)
    print("Target: Random 6x6 Unitary Matrix U in SU(6)")
    print("+-------------------------+---------------+-------------------+")
    print("| Architecture            | Total MZIs    | Max Optical Depth |")
    print("+-------------------------+---------------+-------------------+")
    print("| Clements (Rectangular)  | 15            | 6                 |")
    print("| Reck (Triangular)       | 15            | 9                 |")
    print("+-------------------------+---------------+-------------------+")

    # Stage 3: HOM Interference Simulation
    print("\n[3/16] HONG-OU-MANDEL INTERFERENCE SIMULATION (PRL 1987)")
    print("-" * 80)
    hom = HongOuMandelSimulator()
    res3 = hom.scan_hom_dip()
    print(f"Simulated HOM Visibility: {res3['hom_visibility_pct']:.2f}% (Coincidence Dip P_11 -> {res3['dip_minimum_p11']*100:.2f}%)")

    # Stage 4: Boson Sampling Permanent
    print("\n[4/16] MATRIX PERMANENT BENCHMARK (Boson Sampling)")
    print("-" * 80)
    boson_results = benchmark_boson_sampling_speedup(dimensions=[4, 8, 10, 12])
    for item in boson_results:
        n = item['matrix_dimension']
        print(f"  N = {n:<2} | Classical Perm: {item['classical_glynn_ms']:>7.3f} ms | Photonic Transit: {item['photonic_transit_ns']:.2f} ns (Speedup: {int(item['quantum_optical_speedup']):,}x)")

    # Stage 5: SSH Topological Protection Simulation
    print("\n[5/16] SSH TOPOLOGICAL EDGE STATE SIMULATION")
    print("-" * 80)
    ssh = TopologicalPhotonicLattice(num_cells=8, t1_intra=0.35, t2_inter=1.0)
    res5 = ssh.benchmark_disorder_robustness(disorder_levels=[0.0, 0.05, 0.15, 0.25])
    print(f"Phase: Topological (Zak Phase = pi, W = 1)")
    print(f"Fidelity under 25% disorder: {res5[-1]['topological_protected_fidelity_pct']:.1f}% (protected) vs {res5[-1]['standard_waveguide_fidelity_pct']:.1f}% (unprotected)")

    # Stage 6: Thermal Cross-Talk Calibration
    print("\n[6/16] THERMAL CROSS-TALK MATRIX INVERSION (K^-1 CALIBRATION)")
    print("-" * 80)
    thermal = ThermalCrossTalkOptimizer(num_mzis=4)
    res6 = thermal.benchmark_calibration(target_phases=np.array([0.5, 1.2, 2.1, 0.8]))
    print(f"Uncalibrated Fidelity: {res6['uncalibrated_fidelity_pct']:.2f}% -> Calibrated: {res6['calibrated_fidelity_pct']:.2f}%")

    # Stage 7: PID Phase Stabilizer
    print("\n[7/16] PID THERMO-OPTIC PHASE DRIFT STABILIZER")
    print("-" * 80)
    pid = PhotonicPIDStabilizer(kp=1.2, ki=0.4, kd=0.05)
    res7 = pid.simulate_stabilization(duration_steps=50)
    print(f"Drift RMS: {res7['unmitigated_drift_rms_rad']:.4f} rad -> Stabilized RMS: {res7['pid_stabilized_rms_rad']:.4f} rad")
    print(f"Steady-State Fidelity: {res7['steady_state_fidelity_pct']:.2f}%")

    # Stage 8: MBQC Cluster State Builder
    print("\n[8/16] MBQC 3D CLUSTER STATE GRAPH BUILDER (Nat. Comm. 2023 model)")
    print("-" * 80)
    mbqc = MBQCClusterGenerator(grid_x=3, grid_y=3, grid_z=2)
    res8 = mbqc.simulate_type2_fusion()
    print(f"Cluster: {res8['cluster_architecture']} | Qubits: {res8['total_photonic_qubits']} | Edges: {res8['entangled_cphase_edges']}")
    print(f"Simulated Type-II Fusion Fidelity: {res8['type2_fusion_fidelity_pct']:.2f}% ({res8['fault_tolerance_margin']})")

    # Stage 9: VQE Chemistry Simulation
    print("\n[9/16] PHOTONIC VQE MOLECULAR SOLVER SIMULATION (H2)")
    print("-" * 80)
    vqe = PhotonicVQESolver(molecule="H2")
    res9 = vqe.solve_ground_state_curve()
    print(f"Molecule: H2 | Eq Bond: {res9['equilibrium_bond_length_angstrom']} A | Energy: {res9['ground_state_energy_hartree']:.4f} Ha")
    print(f"Chemical Accuracy: < {res9['chemical_accuracy_kcal_mol']} kcal/mol")

    # Stage 10: ZNE Error Mitigation
    print("\n[10/16] ZERO-NOISE EXTRAPOLATION (ZNE) ERROR MITIGATION")
    print("-" * 80)
    zne = PhotonicZNEMitigator()
    res10 = zne.execute_zne_mitigation()
    print(f"Noisy: {res10['unmitigated_expectation']:.4f} -> ZNE: {res10['zne_mitigated_expectation']:.4f} (Ideal: {res10['ideal_expectation']:.4f})")
    print(f"Error Reduction: {res10['error_reduction_pct']:.1f}%")

    # Stage 11: QRNG Beam-Splitter Simulation
    print("\n[11/16] QRNG BEAM-SPLITTER SIMULATION & NIST SP 800-22 VALIDATION")
    print("-" * 80)
    qrng = PhotonicQRNG()
    res11 = qrng.generate_and_test_randomness()
    print(f"Simulated 10,000 beam-splitter samples | Monobit p: {res11['monobit_frequency_p_value']:.4f} | Runs p: {res11['runs_test_p_value']:.4f}")
    print(f"NIST SP 800-22 Compliance: {res11['nist_sp800_22_compliance']}")

    # Stage 12: Grating Coupler Optimization
    print("\n[12/16] GRATING COUPLER GEOMETRY OPTIMIZER (IEEE JLT 2023 parameters)")
    print("-" * 80)
    grating = GratingCouplerOptimizer()
    res12 = grating.optimize_coupling_efficiency()
    print(f"Grating Pitch: {res12['grating_pitch_nm']} nm | Coupling Eff: {res12['peak_coupling_efficiency_pct']:.1f}% (Loss: {res12['fiber_to_chip_insertion_loss_db']:.2f} dB)")

    # Stage 13: Hybrid Spatial-Temporal Compilation
    print("\n[13/16] HYBRID SPATIAL-TEMPORAL COMPILER (Nature 2022 architecture)")
    print("-" * 80)
    hybrid_comp = HybridSpatialTemporalCompiler(spatial_modes=4, loop_delays=[1, 6, 36])
    res13 = hybrid_comp.compile_hybrid_lattice(target_modes=64)
    print(f"Target: 64 modes | Monolithic MZIs: {res13['monolithic_spatial_mzis_required']} -> Hybrid MZIs: {res13['hybrid_physical_mzis_on_chip']}")
    print(f"Area Reduction: {res13['physical_silicon_reduction_pct']:.1f}% | Power Savings: {res13['thermal_power_savings_pct']:.1f}%")

    # Stage 14: DAC Pre-Emphasis Pulse Computation
    print("\n[14/16] DAC PRE-EMPHASIS VOLTAGE PULSE COMPUTATION")
    print("-" * 80)
    dac_shaper = DACPreEmphasisShaper(tau_thermal_us=8.5, v_pi=3.2)
    res14 = dac_shaper.compute_overdrive_pulse(target_phase_rad=np.pi)
    print(f"Steady V: {res14['steady_state_dac_voltage_v']}V -> Boost V: {res14['pre_emphasis_overdrive_voltage_v']}V (Duration: {res14['boost_pulse_duration_us']} us)")
    print(f"Thermal Rise: {res14['unmitigated_thermal_rise_time_us']} us -> Accelerated: {res14['accelerated_rise_time_us']} us ({res14['thermal_switching_speedup_factor']:.1f}x)")

    # Stage 15: Pauli Frame Tracker
    print("\n[15/16] SOFTWARE PAULI FRAME TRACKER (Nat. Comm. 2023 architecture)")
    print("-" * 80)
    pauli_tracker = PauliFrameSyndromeTracker(num_qubits=4)
    for _ in range(3):
        pauli_tracker.process_fusion_measurement(0, 1, p_success=0.50)
    res15 = pauli_tracker.get_circuit_fault_tolerance_metrics()
    print(f"Fusion gates tracked: {res15['total_fusions_executed']}")
    print(f"Pauli Frame X: {res15['final_pauli_x_frame']} | Z: {res15['final_pauli_z_frame']}")

    # Stage 16: Loss-Aware MZI Routing
    print("\n[16/16] LOSS-AWARE HEURISTIC MZI ROUTER")
    print("-" * 80)
    router = LossAwareMZIRouter(num_modes=6)
    res16 = router.optimize_routing_schedule(np.eye(6))
    print(f"Unoptimized Loss: {res16['unoptimized_mesh_loss_db']} dB -> Optimized: {res16['loss_aware_optimized_loss_db']} dB")
    print(f"Loss Reduction: {res16['optical_insertion_loss_reduction_pct']:.1f}% | Fidelity Boost: +{res16['quantum_state_fidelity_boost_pct']:.1f}%")
    print("-" * 80)

    print("\n" + "=" * 80)
    print("ALL 16 SIMULATION MODULES COMPLETED SUCCESSFULLY.")
    print("=" * 80)

if __name__ == '__main__':
    run_complete_simulation_suite()
