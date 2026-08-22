"""
Quantum State Tomography and Maximum Likelihood Estimation (MLE).
"""
import numpy as np

class QuantumStateTomography:
    def __init__(self, num_qubits: int = 1):
        self.num_qubits = num_qubits
        self.dim = 2 ** num_qubits

    def reconstruct_density_matrix(self, stokes_parameters: np.ndarray) -> np.ndarray:
        s0, s1, s2, s3 = stokes_parameters
        pauli_x = np.array([[0, 1], [1, 0]])
        pauli_y = np.array([[0, -1j], [1j, 0]])
        pauli_z = np.array([[1, 0], [0, -1]])
        rho = 0.5 * (s0 * np.eye(2) + s1 * pauli_x + s2 * pauli_y + s3 * pauli_z)
        return rho

    def compute_fidelity(self, rho: np.ndarray, target_state: np.ndarray) -> float:
        f = np.real(target_state.conj().T @ rho @ target_state)
        return float(f)
