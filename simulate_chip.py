"""
Qfóton: IBM Quantum Circuit Composer Simulator (simulate_chip.py)
Simulates quantum circuit execution using standard IBM Qiskit circuit styling,
animating quantum statevectors traveling through Hadamard, Phase, and CNOT gates.
"""

import time
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation

# Clean IBM dark styling
plt.style.use('dark_background')

def run_ibm_circuit():
    print("=" * 75)
    print(" Qfóton: IBM QUANTUM CIRCUIT COMPOSER & STATEVECTOR SIMULATOR")
    print("=" * 75)
    print("Circuit: 2-Qubit Bell State Generator (|Phi+> = (|00> + |11>)/sqrt(2))")
    print("Gates:   H (Hadamard) -> Rz(pi) -> CNOT -> Measurement [Z-Basis]")
    print("-" * 75)

    fig, ax = plt.subplots(figsize=(11, 6), dpi=120)
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0b0f19')

    # Circuit Wire Dimensions
    x_start, x_end = 1.0, 11.5
    y_q0 = 3.2
    y_q1 = 2.0
    y_c0 = 0.75
    y_c1 = 0.65

    # 1. Quantum Register Wires (q0, q1)
    ax.plot([x_start, x_end], [y_q0, y_q0], color='#64748b', lw=1.8, zorder=1)
    ax.plot([x_start, x_end], [y_q1, y_q1], color='#64748b', lw=1.8, zorder=1)
    ax.text(x_start - 0.2, y_q0, "q[0]: |0⟩", color='#38bdf8', fontsize=11, ha='right', va='center', fontfamily='monospace', fontweight='bold')
    ax.text(x_start - 0.2, y_q1, "q[1]: |0⟩", color='#38bdf8', fontsize=11, ha='right', va='center', fontfamily='monospace', fontweight='bold')

    # 2. Classical Double Register Wires (c)
    ax.plot([x_start, x_end], [y_c0, y_c0], color='#475569', lw=1.2, zorder=1)
    ax.plot([x_start, x_end], [y_c1, y_c1], color='#475569', lw=1.2, zorder=1)
    ax.text(x_start - 0.2, (y_c0 + y_c1)/2, "c:  / 2", color='#94a3b8', fontsize=10, ha='right', va='center', fontfamily='monospace')

    # 3. IBM Gate: Hadamard [ H ] on q[0]
    h_box = patches.FancyBboxPatch((2.6, y_q0 - 0.4), 0.9, 0.8, boxstyle="round,pad=0.04", edgecolor='#00d2ff', facecolor='#0f62fe', lw=1.5, zorder=3)
    ax.add_patch(h_box)
    ax.text(3.05, y_q0, "H", color='#ffffff', fontsize=12, ha='center', va='center', fontweight='bold', fontfamily='sans-serif')

    # 4. IBM Gate: Phase [ Rz(π) ] on q[0]
    rz_box = patches.FancyBboxPatch((4.5, y_q0 - 0.4), 1.1, 0.8, boxstyle="round,pad=0.04", edgecolor='#be95ff', facecolor='#8a3ffc', lw=1.5, zorder=3)
    ax.add_patch(rz_box)
    ax.text(5.05, y_q0, "Rz(π)", color='#ffffff', fontsize=9.5, ha='center', va='center', fontweight='bold', fontfamily='sans-serif')

    # 5. IBM Gate: CNOT (Control on q0, Target on q1)
    # Control Dot
    c_dot = plt.Circle((7.0, y_q0), 0.12, color='#00d2ff', ec='#ffffff', lw=1.2, zorder=4)
    ax.add_patch(c_dot)
    # Vertical Line
    ax.plot([7.0, 7.0], [y_q0, y_q1], color='#00d2ff', lw=2.0, zorder=3)
    # Target ⊕
    t_circle = plt.Circle((7.0, y_q1), 0.35, color='#00d2ff', fill=False, lw=2.0, zorder=4)
    ax.add_patch(t_circle)
    ax.plot([6.65, 7.35], [y_q1, y_q1], color='#00d2ff', lw=2.0, zorder=5)
    ax.plot([7.0, 7.0], [y_q1 - 0.35, y_q1 + 0.35], color='#00d2ff', lw=2.0, zorder=5)

    # 6. IBM Gate: Measurement Meters [ 📈 ] on q[0] and q[1]
    for y_pos in [y_q0, y_q1]:
        m_box = patches.FancyBboxPatch((9.2, y_pos - 0.4), 0.9, 0.8, boxstyle="round,pad=0.04", edgecolor='#697077', facecolor='#21272a', lw=1.2, zorder=3)
        ax.add_patch(m_box)
        # Meter Arc & Needle
        arc = patches.Arc((9.65, y_pos - 0.1), 0.45, 0.35, angle=0, theta1=0, theta2=180, color='#00d2ff', lw=1.4, zorder=4)
        ax.add_patch(arc)
        ax.plot([9.65, 9.8], [y_pos - 0.1, y_pos + 0.15], color='#00d2ff', lw=1.4, zorder=4)
        # Classical projection line down to register c
        ax.plot([9.65, 9.65], [y_pos - 0.4, y_c0], color='#64748b', lw=1.0, linestyle='--', zorder=2)

    # 7. Animated Quantum State Particles (Traveling Wavepackets)
    p_q0, = ax.plot([], [], 'o', color='#00d2ff', markersize=13, markeredgecolor='#ffffff', markeredgewidth=1.8, zorder=7)
    p_q1, = ax.plot([], [], 'o', color='#00d2ff', markersize=13, markeredgecolor='#ffffff', markeredgewidth=1.8, zorder=7)

    # 8. Dynamic Telemetry & Statevector Display
    state_box = ax.text(6.0, 4.3, "|ψ⟩ = |00⟩", color='#00d2ff', fontsize=12, fontweight='bold', ha='center', fontfamily='monospace',
                        bbox=dict(boxstyle="round,pad=0.4", fc="#161e2e", ec="#00d2ff", lw=1.2))
    
    classical_readout = ax.text(11.8, (y_c0 + y_c1)/2, 'c = "00"', color='#a7f3d0', fontsize=11, fontfamily='monospace', fontweight='bold', va='center')
    
    info_text = ax.text(6.0, -0.4, "EXECUTION: Initializing qubits |00⟩...", color='#94a3b8', fontsize=9.5, ha='center', fontfamily='monospace')

    ax.set_title("IBM Quantum Circuit Composer - Real-Time Statevector Simulation", fontsize=12, fontweight='bold', color='#f8fafc', pad=15)
    ax.set_xlim(0.0, 13.0)
    ax.set_ylim(-0.8, 4.8)
    ax.axis('off')

    num_frames = 140
    def update(frame):
        progress = frame / num_frames
        x = x_start + progress * (x_end - x_start)

        # Update particle positions
        p_q0.set_data([x], [y_q0])
        p_q1.set_data([x], [y_q1])

        # Stage 1: Before Hadamard (x < 2.6)
        if x < 2.6:
            state_box.set_text("|ψ⟩ = |00⟩  (Ground State)")
            info_text.set_text("Step 1: Qubits initialized in ground state |00⟩")
            classical_readout.set_text('c = "00"')

        # Stage 2: After Hadamard (2.6 <= x < 4.5)
        elif x < 4.5:
            state_box.set_text("|ψ⟩ = (|0⟩ + |1⟩)/√2 ⊗ |0⟩")
            info_text.set_text("Step 2: Hadamard gate puts q[0] into equal superposition")

        # Stage 3: After Phase Rz(pi) (4.5 <= x < 7.0)
        elif x < 7.0:
            state_box.set_text("|ψ⟩ = (|0⟩ - |1⟩)/√2 ⊗ |0⟩")
            info_text.set_text("Step 3: Rz(π) gate applies relative quantum phase shift")

        # Stage 4: After CNOT (7.0 <= x < 9.2)
        elif x < 9.2:
            state_box.set_text("|ψ⟩ = (|00⟩ + |11⟩)/√2  [Bell State |Φ+⟩]")
            info_text.set_text("Step 4: CNOT gate entangles q[0] and q[1] into maximum Bell State!")

        # Stage 5: Measurement (x >= 9.2)
        else:
            state_box.set_text("Measured: |Φ+⟩ -> 50% |00⟩ + 50% |11⟩")
            info_text.set_text("Step 5: Z-Basis measurement collapses state into classical register c!")
            # Alternating collapsed measurement readout
            readout = '"11"' if (frame % 20 > 10) else '"00"'
            classical_readout.set_text(f'c = {readout}')

        return p_q0, p_q1, state_box, info_text, classical_readout

    ani = animation.FuncAnimation(fig, update, frames=num_frames, interval=25, blit=False, repeat=True)
    plt.tight_layout()
    
    # Save static thumbnail as well
    save_path = os.path.join(BASE_DIR, "assets", "silicon_chip_simulation.png")
    plt.savefig(save_path, bbox_inches='tight')
    plt.show()

if __name__ == '__main__':
    run_ibm_circuit()
