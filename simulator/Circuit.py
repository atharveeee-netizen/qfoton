# -*- coding: utf-8 -*-
# ==============================================================================
# Qfóton: Full-Stack Silicon Photonic Quantum Computing & Compiler Suite
# Copyright (c) 2026 Atharve and the Qfóton Contributors. All rights reserved.
# Released under the MIT License.
# ==============================================================================
"""
Created on Fri Mar  7 10:26:25 2025

@author: Hüttenbrenner
"""
from .Gates import *
import numpy as np
from typing import List



class Circuit:
    """Represents a quantum circuit consisting of multiple gates."""
    def __init__(self, gates: List[Gate], mode_number):
        if not isinstance(gates, list) or not all(isinstance(g, Gate) for g in gates):
            raise TypeError("gates must be a list of Gate objects")
        
        if len(gates) == 0:
            self.handle_empty_circuit()  

        self.gates = gates
        self.mode_number = mode_number
        self.unitary = self.get_unitary()

    def handle_empty_circuit(self):
        """Define behavior when no gates are provided."""
        print("Circuit is empty. Applying default behavior.")
        identity_matrix = np.eye(self.mode_number)  #Default: 2x2 identity matrix
        self.gates = [Gate(identity_matrix)]

    def get_matrices(self) -> List[np.ndarray]:
        """Returns a list of all matrices from the gates in the circuit."""
        return [gate.single_photon_matrix for gate in self.gates]

    def get_unitary(self) -> np.ndarray:
        """Computes the circuit's unitary matrix by multiplying gates from left to right."""
        matrices = self.get_matrices()
        if not matrices:
            raise ValueError("No matrices found in circuit.")
        
        # Multiply matrices from left to right
        unitary = matrices[0]            
        for matrix in matrices[1:]:
            unitary = np.dot(matrix, unitary)  # Left-to-right multiplication - assume matrices[0] is the leftmost quantum gate
        
        return unitary


#%%test
# inv_m = np.array([0,1])
# num_m = 2
# gate1 = Gate(np.array([[0, 1], [1, 0]]),inv_m,num_m)  # Pauli-X
# gate2 = Gate(np.array([[1, 0], [0, -1]]),inv_m,num_m)  # Pauli-Z
# gate3 = Gate(np.array([[0, -1j], [1j, 0]]),inv_m,num_m)  # Pauli-Y

# circuit = Circuit([gate1, gate2, gate3],num_m)
# unitary = circuit.get_unitary()