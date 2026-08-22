"""
Qfóton: Universal OpenQASM 2.0 Parser and Transpiler.
Parses standard quantum assembly (QASM) and converts it into unitary matrices
ready for Clements SU(N) silicon photonic MZI decomposition.
"""

import re
import numpy as np
from typing import Tuple, List, Dict

# Standard 1-qubit & 2-qubit matrices
PAULI_I = np.eye(2, dtype=complex)
PAULI_X = np.array([[0, 1], [1, 0]], dtype=complex)
PAULI_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
PAULI_Z = np.array([[1, 0], [0, -1]], dtype=complex)
HADAMARD = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2.0)

def rz_gate(phi: float) -> np.ndarray:
    return np.array([[np.exp(-1j * phi / 2), 0], [0, np.exp(1j * phi / 2)]], dtype=complex)

def ry_gate(theta: float) -> np.ndarray:
    return np.array([[np.cos(theta / 2), -np.sin(theta / 2)], [np.sin(theta / 2), np.cos(theta / 2)]], dtype=complex)

class OpenQASMTranspiler:
    def __init__(self):
        pass

    def parse_qasm_string(self, qasm_str: str) -> Tuple[int, np.ndarray, List[Dict]]:
        lines = [line.strip() for line in qasm_str.strip().split('\n') if line.strip() and not line.strip().startswith('//')]
        num_qubits = 2
        
        for l in lines:
            m = re.search(r'qreg\s+\w+\[(\d+)\];', l)
            if m:
                num_qubits = int(m.group(1))
                break
                
        dim = 2 ** num_qubits
        total_unitary = np.eye(dim, dtype=complex)
        gate_list = []

        for l in lines:
            # Hadamard: h q[0];
            m = re.search(r'^h\s+q\[(\d+)\];', l)
            if m:
                q = int(m.group(1))
                gate_list.append({'gate': 'h', 'qubit': q})
                U_step = self._embed_single_qubit_gate(HADAMARD, q, num_qubits)
                total_unitary = U_step @ total_unitary
                continue

            # Pauli X: x q[0];
            m = re.search(r'^x\s+q\[(\d+)\];', l)
            if m:
                q = int(m.group(1))
                gate_list.append({'gate': 'x', 'qubit': q})
                U_step = self._embed_single_qubit_gate(PAULI_X, q, num_qubits)
                total_unitary = U_step @ total_unitary
                continue

            # Pauli Z: z q[0];
            m = re.search(r'^z\s+q\[(\d+)\];', l)
            if m:
                q = int(m.group(1))
                gate_list.append({'gate': 'z', 'qubit': q})
                U_step = self._embed_single_qubit_gate(PAULI_Z, q, num_qubits)
                total_unitary = U_step @ total_unitary
                continue

            # Rz rotation: rz(pi/2) q[0];
            m = re.search(r'^rz\(([^)]+)\)\s+q\[(\d+)\];', l)
            if m:
                phi_str, q = m.group(1), int(m.group(2))
                phi = float(eval(phi_str.replace('pi', str(np.pi))))
                gate_list.append({'gate': 'rz', 'qubit': q, 'param': phi})
                U_step = self._embed_single_qubit_gate(rz_gate(phi), q, num_qubits)
                total_unitary = U_step @ total_unitary
                continue

            # Ry rotation: ry(pi/3) q[0];
            m = re.search(r'^ry\(([^)]+)\)\s+q\[(\d+)\];', l)
            if m:
                theta_str, q = m.group(1), int(m.group(2))
                theta = float(eval(theta_str.replace('pi', str(np.pi))))
                gate_list.append({'gate': 'ry', 'qubit': q, 'param': theta})
                U_step = self._embed_single_qubit_gate(ry_gate(theta), q, num_qubits)
                total_unitary = U_step @ total_unitary
                continue

            # CNOT: cx q[0], q[1];
            m = re.search(r'^cx\s+q\[(\d+)\],\s*q\[(\d+)\];', l)
            if m:
                q_ctrl, q_tgt = int(m.group(1)), int(m.group(2))
                gate_list.append({'gate': 'cx', 'ctrl': q_ctrl, 'tgt': q_tgt})
                U_step = self._build_cnot_matrix(q_ctrl, q_tgt, num_qubits)
                total_unitary = U_step @ total_unitary
                continue

        return num_qubits, total_unitary, gate_list

    def _embed_single_qubit_gate(self, G: np.ndarray, target: int, num_qubits: int) -> np.ndarray:
        op = np.array([[1.0]], dtype=complex)
        for i in range(num_qubits):
            op = np.kron(op, G if i == target else PAULI_I)
        return op

    def _build_cnot_matrix(self, ctrl: int, tgt: int, num_qubits: int) -> np.ndarray:
        dim = 2 ** num_qubits
        cnot = np.zeros((dim, dim), dtype=complex)
        for state in range(dim):
            bits = [(state >> (num_qubits - 1 - k)) & 1 for k in range(num_qubits)]
            if bits[ctrl] == 1:
                bits[tgt] = 1 - bits[tgt]
            new_state = 0
            for k, b in enumerate(bits):
                new_state |= (b << (num_qubits - 1 - k))
            cnot[new_state, state] = 1.0
        return cnot
