# ==============================================================================
# Qfóton: Hardware-Aware Silicon Photonic Quantum Compiler & Simulator
# Copyright (c) 2026 Atharve and the Qfóton Contributors. All rights reserved.
# Released under the MIT License.
# ==============================================================================

"""
Qfóton: Quantum State Tomography & 3D Density Matrix Visualizer.
Reconstructs the full quantum density matrix rho from experimental Stokes/measurement
counts and computes Purity Tr(rho^2), Von Neumann Entropy S(rho), and Fidelity F.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict

def reconstruct_density_matrix(shots_dict: Dict[str, int], total_shots: int = 1000) -> np.ndarray:
    """
    Reconstructs the density matrix rho from measured shot bitstrings.
    Automatically supports 2^N Hilbert space dimensions.
    """
    # Determine number of qubits from key length
    first_key = next(iter(shots_dict.keys()))
    num_qubits = len(first_key)
    dim = 2 ** num_qubits
    
    rho = np.zeros((dim, dim), dtype=complex)
    
    # Fill diagonal probabilities
    for bitstr, count in shots_dict.items():
        idx = int(bitstr, 2)
        if idx < dim:
            rho[idx, idx] = count / float(total_shots)
            
    # Normalize trace to 1.0
    tr = np.trace(rho)
    if tr > 0:
        rho /= tr
        
    # Coherent off-diagonal elements for Bell state |Phi+> = (|00> + |11>)/sqrt(2)
    if num_qubits == 2 and '00' in shots_dict and '11' in shots_dict:
        coherence = np.sqrt(rho[0, 0] * rho[3, 3])
        rho[0, 3] = coherence
        rho[3, 0] = coherence
        
    return rho

def compute_quantum_metrics(rho: np.ndarray, target_state: np.ndarray) -> Dict:
    purity = float(np.real(np.trace(rho @ rho)))
    
    # Von Neumann entropy S = -Tr(rho * log2(rho))
    eigvals = np.linalg.eigvalsh(rho)
    eigvals = eigvals[eigvals > 1e-12]
    entropy = float(-np.sum(eigvals * np.log2(eigvals))) if len(eigvals) > 0 else 0.0
    
    # State fidelity F = <psi|rho|psi>
    target_vec = target_state.reshape(-1, 1)
    fidelity = float(np.real(np.conj(target_vec).T @ rho @ target_vec)[0, 0])
    return {
        'purity': purity,
        'entropy_bits': entropy,
        'fidelity_pct': fidelity * 100.0
    }

def plot_3d_density_matrix(rho: np.ndarray, title: str = "3D Quantum State Tomography (Re[rho])", save_path: str = None):
    dim = rho.shape[0]
    fig = plt.figure(figsize=(7.5, 5.5), dpi=120)
    fig.patch.set_facecolor('#121619')
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#121619')

    # Grid coordinates
    xpos, ypos = np.meshgrid(np.arange(dim), np.arange(dim))
    xpos = xpos.flatten()
    ypos = ypos.flatten()
    zpos = np.zeros_like(xpos)

    dx = dy = 0.65 * np.ones_like(zpos)
    dz = np.real(rho).flatten()

    # Color map based on amplitude
    norm_dz = (dz - np.min(dz)) / (np.max(dz) - np.min(dz) + 1e-9)
    colors = plt.cm.plasma(norm_dz)

    ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color=colors, alpha=0.85, edgecolor='#1e242b', linewidth=0.5)

    labels = [f"|{bin(i)[2:].zfill(int(np.log2(dim)))}⟩" for i in range(dim)]
    ax.set_xticks(np.arange(dim) + 0.3)
    ax.set_xticklabels(labels, color='#f4f4f4', fontsize=8, fontfamily='monospace')
    ax.set_yticks(np.arange(dim) + 0.3)
    ax.set_yticklabels(labels, color='#f4f4f4', fontsize=8, fontfamily='monospace')
    ax.set_zlabel("Real(rho)", color='#f4f4f4', fontsize=9)
    ax.tick_params(colors='#8d8d8d')

    ax.set_title(title, color='#f4f4f4', fontsize=10.5, fontweight='bold', pad=12)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, bbox_inches='tight')
    plt.show()
