# ==============================================================================
# Qfóton: Hardware-Aware Silicon Photonic Quantum Compiler & Simulator
# Copyright (c) 2026 Atharve and the Qfóton Contributors. All rights reserved.
# Released under the MIT License.
# ==============================================================================

"""
Photonic Quantum Graph Optimization Solver (Max-Clique and Dense Subgraph).
"""
import numpy as np
from typing import List, Tuple

class PhotonicGraphSolver:
    def __init__(self, adjacency_matrix: np.ndarray):
        self.adj = adjacency_matrix.astype(float)
        self.num_nodes = adjacency_matrix.shape[0]

    def solve_dense_subgraph(self, k_nodes: int = 3) -> Tuple[List[int], float]:
        eigvals, eigvecs = np.linalg.eigh(self.adj)
        scores = np.sum(eigvecs[:, -k_nodes:] ** 2, axis=1)
        selected_nodes = list(np.argsort(scores)[::-1][:k_nodes])
        subgraph = self.adj[np.ix_(selected_nodes, selected_nodes)]
        density = np.sum(subgraph) / max(1, k_nodes * (k_nodes - 1))
        return sorted(selected_nodes), float(density)
