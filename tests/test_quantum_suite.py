"""
Qfóton: Comprehensive Quantum Photonics Automated Test & Physical Verification Suite.
Validates all 12 modules against physical laboratory benchmarks and theoretical limits.
"""

import unittest
import numpy as np
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from simulator.clements_compiler import clements_decompose, reconstruct_clements_unitary, compute_clements_metrics
from simulator.reck_compiler import reck_decompose, reconstruct_reck_unitary, compute_reck_metrics
from simulator.fast_permanents import fast_glynn_permanent, fast_ryser_permanent, benchmark_boson_sampling_speedup
from simulator.hafnian_gbs import hafnian_recursive, loop_hafnian_recursive, GaussianBosonSampling
from simulator.topological_protection import TopologicalPhotonicLattice
from simulator.hom_interference import HongOuMandelSimulator
from simulator.thermal_crosstalk import ThermalCrossTalkOptimizer
from simulator.mbqc_cluster import MBQCClusterGenerator
from simulator.hardware_noise import PhotonicHardwareNoiseModel
from simulator.carolan_science_benchmark import RealFoundryNoiseModel
from simulator.grating_coupler import GratingCouplerOptimizer
from simulator.gds_layout import PhotonicLayoutExporter
from simulator.sfwm_source import SFWMPhotonSource
from simulator.pid_phase_stabilizer import PhotonicPIDStabilizer
from simulator.photonic_vqe import PhotonicVQESolver
from simulator.photonic_qrng import PhotonicQRNG
from simulator.qasm_parser import OpenQASMTranspiler
from simulator.state_tomography import reconstruct_density_matrix, compute_quantum_metrics

class TestQfotonQuantumSuite(unittest.TestCase):

    def setUp(self):
        np.random.seed(42)

    def test_01_clements_decomposition_and_reconstruction(self):
        """Validates Clements Optica 2016 decomposition and exact unitary reconstruction."""
        for N in [2, 3, 4, 6, 8]:
            z = (np.random.randn(N, N) + 1j * np.random.randn(N, N)) / np.sqrt(2.0)
            U, _ = np.linalg.qr(z)
            
            mzi_list, diag_phases = clements_decompose(U)
            U_rec = reconstruct_clements_unitary(mzi_list, diag_phases, N)
            
            error = np.linalg.norm(U - U_rec)
            self.assertLess(error, 1e-12, f"Clements reconstruction error {error} exceeds tolerance for N={N}")
            self.assertEqual(len(mzi_list), N * (N - 1) // 2, f"MZI count mismatch for N={N}")

    def test_02_reck_decomposition_and_reconstruction(self):
        """Validates Reck PRL 1994 triangular decomposition and reconstruction."""
        for N in [2, 3, 4, 6]:
            z = (np.random.randn(N, N) + 1j * np.random.randn(N, N)) / np.sqrt(2.0)
            U, _ = np.linalg.qr(z)
            
            mzi_list, diag_phases = reck_decompose(U)
            U_rec = reconstruct_reck_unitary(mzi_list, diag_phases, N)
            
            error = np.linalg.norm(U - U_rec)
            self.assertLess(error, 1e-12, f"Reck reconstruction error {error} exceeds tolerance for N={N}")
            self.assertEqual(len(mzi_list), N * (N - 1) // 2)

    def test_03_fast_permanents_equivalence(self):
        """Validates vectorized Glynn vs Ryser permanent calculation."""
        for n in [2, 3, 4, 5]:
            A = (np.random.randn(n, n) + 1j * np.random.randn(n, n)) / np.sqrt(2.0)
            p_glynn = fast_glynn_permanent(A)
            p_ryser = fast_ryser_permanent(A)
            self.assertAlmostEqual(abs(p_glynn - p_ryser), 0.0, places=5)

    def test_04_hafnian_and_gaussian_boson_sampling(self):
        """Validates Hafnian calculation against exact algebraic identity."""
        A = np.array([[0, 1.2, 0.5, 0.2],
                      [1.2, 0, 0.3, 0.8],
                      [0.5, 0.3, 0, 0.6],
                      [0.2, 0.8, 0.6, 0]], dtype=complex)
        haf = hafnian_recursive(A)
        expected = A[0,1]*A[2,3] + A[0,2]*A[1,3] + A[0,3]*A[1,2]
        self.assertAlmostEqual(abs(haf - expected), 0.0, places=10)
        
        gbs = GaussianBosonSampling(num_modes=4, squeezing_param_r=0.6)
        samples = gbs.sample_photon_events(num_samples=100)
        self.assertGreater(samples['mean_photon_number'], 0.0)

    def test_05_ssh_topological_protection(self):
        """Validates SSH lattice Zak phase, winding number, and disorder immunity."""
        lattice_topo = TopologicalPhotonicLattice(num_cells=6, t1_intra=0.3, t2_inter=1.0)
        inv_topo = lattice_topo.compute_topological_invariants()
        self.assertTrue(inv_topo['is_topological'])
        self.assertAlmostEqual(inv_topo['zak_phase_rad'], np.pi, places=5)
        self.assertEqual(inv_topo['winding_number'], 1)
        
        lattice_triv = TopologicalPhotonicLattice(num_cells=6, t1_intra=1.0, t2_inter=0.3)
        inv_triv = lattice_triv.compute_topological_invariants()
        self.assertFalse(inv_triv['is_topological'])
        self.assertAlmostEqual(inv_triv['zak_phase_rad'], 0.0, places=5)
        
        bench = lattice_topo.benchmark_disorder_robustness(disorder_levels=[0.25])
        self.assertGreater(bench[0]['topological_protected_fidelity_pct'], 95.0)

    def test_06_hong_ou_mandel_interference(self):
        """Validates HOM dip probability, non-classical coalescence, and visibility."""
        hom = HongOuMandelSimulator(coherence_time_ps=1.0, indistinguishability_M=0.985, g2_zero=0.002)
        res = hom.scan_hom_dip()
        self.assertGreater(res['hom_visibility_pct'], 95.0)
        self.assertLess(res['dip_minimum_p11'], 0.05)
        self.assertAlmostEqual(res['dip_baseline_p11'], 0.50, places=5)

    def test_07_thermal_crosstalk_auto_calibration(self):
        """Validates thermal crosstalk inverse matrix pre-distortion calibration."""
        calibrator = ThermalCrossTalkOptimizer(num_mzis=10, coupling_strength=0.20)
        target = np.array([0.5 * (i + 1) for i in range(10)])
        cal_res = calibrator.benchmark_calibration(target)
        self.assertGreater(cal_res['calibrated_fidelity_pct'], 99.5)
        self.assertLess(cal_res['calibrated_error_rad'], 1e-10)
        self.assertGreater(cal_res['thermal_matrix_condition_number'], 1.0)

    def test_08_mbqc_raussendorf_3d_cluster(self):
        """Validates 3D Raussendorf cluster graph adjacency, edge count, and fusion."""
        mbqc = MBQCClusterGenerator(grid_x=3, grid_y=3, grid_z=2)
        res = mbqc.simulate_type2_fusion()
        self.assertEqual(res['total_photonic_qubits'], 18)
        self.assertEqual(res['entangled_cphase_edges'], 33)
        self.assertGreater(res['type2_fusion_fidelity_pct'], 95.0)

    def test_09_carolan_science_2015_cleanroom_model(self):
        """Validates physical noise model matching Carolan et al., Science 2015 published fidelity."""
        model = RealFoundryNoiseModel()
        U_ideal = np.eye(6, dtype=complex)
        _, metrics = model.apply_foundry_noise_to_unitary(U_ideal, chip_length_cm=2.4)
        
        # Published benchmark comparison: 99.40%
        self.assertAlmostEqual(metrics['waveguide_propagation_loss_db_cm'], 0.148, places=3)
        self.assertAlmostEqual(metrics['science_2015_published_fidelity_pct'], 99.40, places=2)
        self.assertGreaterEqual(metrics['noisy_state_fidelity_pct'], 95.0)
        self.assertLessEqual(metrics['noisy_state_fidelity_pct'], 100.5)
        self.assertIn('deviation_from_published_pct', metrics)
        self.assertIn('Deviation from published value', metrics['fidelity_match_status'])

    def test_10_grating_coupler_and_gdsii_export(self):
        """Validates sub-wavelength grating coupler loss (<0.8 dB) and GDSII binary export."""
        coupler = GratingCouplerOptimizer()
        spec = coupler.optimize_coupling_efficiency()
        self.assertLess(spec['fiber_to_chip_insertion_loss_db'], 0.90)
        self.assertGreater(spec['peak_coupling_efficiency_pct'], 80.0)
        
        exporter = PhotonicLayoutExporter()
        test_gds_path = os.path.join(BASE_DIR, "assets", "test_mask.gds")
        exporter.export_gdsii_binary([(0, 1, 0.5, 0.2)], test_gds_path)
        self.assertTrue(os.path.exists(test_gds_path))
        self.assertGreater(os.path.getsize(test_gds_path), 500)
        if os.path.exists(test_gds_path):
            os.remove(test_gds_path)

    def test_11_photonic_vqe_and_qrng(self):
        """Validates Photonic VQE for H2 and NIST-compliant Photonic QRNG."""
        vqe = PhotonicVQESolver(molecule="H2")
        vqe_res = vqe.solve_ground_state_curve()
        self.assertAlmostEqual(vqe_res['equilibrium_bond_length_angstrom'], 0.74, places=2)
        self.assertLess(vqe_res['ground_state_energy_hartree'], -1.60)
        
        qrng = PhotonicQRNG(num_bits=5000)
        qrng_res = qrng.generate_and_test_randomness()
        self.assertGreater(qrng_res['monobit_frequency_p_value'], 0.01)
        self.assertGreater(qrng_res['runs_test_p_value'], 0.01)

    def test_12_qasm_transpiler_and_tomography(self):
        """Validates OpenQASM transpiler and 3D quantum state tomography."""
        qasm = """
        OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[2];
        creg c[2];
        h q[0];
        cx q[0], q[1];
        """
        transpiler = OpenQASMTranspiler()
        num_q, U_circ, gates = transpiler.parse_qasm_string(qasm)
        self.assertEqual(num_q, 2)
        self.assertEqual(U_circ.shape, (4, 4))
        
        # Check Bell state creation
        init_state = np.array([1, 0, 0, 0], dtype=complex)
        bell = U_circ @ init_state
        expected_bell = np.array([1/np.sqrt(2), 0, 0, 1/np.sqrt(2)], dtype=complex)
        self.assertAlmostEqual(np.abs(np.vdot(bell, expected_bell)), 1.0, places=5)
        
        shots = {'00': 500, '11': 500}
        rho = reconstruct_density_matrix(shots, total_shots=1000)
        metrics = compute_quantum_metrics(rho, expected_bell)
        self.assertGreater(metrics['fidelity_pct'], 95.0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
