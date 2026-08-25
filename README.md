# Qfóton

**Open-source hardware-aware compiler and simulator for silicon photonic quantum processors.**

[![Build & CI](https://github.com/atharveeee-netizen/qfoton/actions/workflows/ci.yml/badge.svg)](https://github.com/atharveeee-netizen/qfoton/actions)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/atharveeee-netizen/qfoton/blob/main/notebooks/qfoton_quickstart.ipynb)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## What is Qfóton?

Most quantum software tools stop at the abstract circuit level. Real silicon photonic hardware does not.

Qfóton bridges this gap. It takes a standard OpenQASM circuit, compiles it into a physical Mach-Zehnder Interferometer (MZI) mesh, simulates realistic semiconductor noise (waveguide loss, thermal cross-talk, phase drift), and exports layout files for 220nm silicon foundries.

The goal is simple: let researchers and students test how their quantum algorithms behave on real photonic hardware, without needing expensive proprietary CAD tools.

---

## The Pipeline

```text
  OpenQASM 2.0 / 3.0 Circuit
           |
           v
  Clements SU(N) Decomposition --> Physical MZI Grid
           |
           v
  Hardware-Aware Noise Simulation
    - Waveguide loss (0.148 dB/cm, IMEC 220nm SOI)
    - Inter-heater thermal cross-talk (K^-1 inversion)
    - DAC phase jitter & thermo-optic drift
    - PID stabilization model
           |
           v
  Verification & Benchmarking
    - State tomography & fidelity
    - HOM visibility check
    - Comparison against Science (2015) lab data
           |
           v
  GDSII Layout Export
    - Waveguide, coupler, and heater polygons
    - Compatible with KLayout, Cadence, L-Edit
```

---

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Run the full simulation suite
python run_demo.py

# Simulate a specific circuit preset
python simulate_custom_chip.py --preset ghz3
python simulate_custom_chip.py --preset bell

# Use your own OpenQASM file
python simulate_custom_chip.py --qasm path/to/circuit.qasm

# Reproduce the Science (2015) 6-mode benchmark
python simulate_science_2015_chip.py
```

---

## What Does Qfóton Actually Do?

Below is an honest breakdown of each component, what it does, and where the ideas come from.

| Component | What Qfóton Does | Type | Based On |
| :--- | :--- | :--- | :--- |
| **Clements Compiler** | Decomposes arbitrary NxN unitaries into rectangular MZI grids | Implementation | Clements et al., Optica 2016 |
| **Reck Compiler** | Decomposes unitaries into triangular MZI grids (for comparison) | Implementation | Reck et al., PRL 1994 |
| **Thermal Cross-Talk Calibrator** | Inverts inter-heater coupling matrix (K^-1) to cancel heat bleed | Our model | Literature-informed |
| **PID Phase Stabilizer** | Simulates closed-loop thermo-optic drift correction | Simulation | Control theory standard |
| **Cleanroom Noise Engine** | Injects waveguide loss, phase jitter, detector noise from published specs | Simulation | Carolan et al., Science 2015 |
| **HOM Interference Simulator** | Models two-photon quantum interference dip | Simulation | Hong, Ou & Mandel, PRL 1987 |
| **SFWM Photon Source** | Models on-chip spontaneous four-wave mixing pair generation | Simulation | Optica 2021 parameters |
| **Boson Sampling Permanent** | Computes Glynn matrix permanents for sampling benchmarks | Implementation | Aaronson & Arkhipov 2011 |
| **SSH Topological Protection** | Simulates topological edge state robustness under disorder | Simulation | SSH model, literature |
| **MBQC Cluster Generator** | Builds 3D Raussendorf cluster state graphs | Simulation | Bartolucci et al., Nat. Comm. 2023 |
| **VQE Chemistry Solver** | Simulates photonic variational eigensolver for H2 | Simulation | Standard VQE literature |
| **ZNE Error Mitigation** | Richardson extrapolation for zero-noise limit | Implementation | Temme et al., PRL 2017 |
| **QRNG Simulation** | Models 50:50 beam-splitter Bernoulli sampling + NIST statistical tests | Simulation | PR Applied 2022 model |
| **Grating Coupler Optimizer** | Optimizes sub-wavelength fiber coupling geometry | Simulation | IEEE JLT 2023 parameters |
| **DAC Pre-Emphasis Shaper** | Computes overdrive voltage pulses for faster thermal switching | Our model | Nature Photonics parameters |
| **Pauli Frame Tracker** | Software-only Pauli frame updates from fusion measurements | Implementation | Nat. Comm. 2023 architecture |
| **Loss-Aware MZI Router** | Heuristic Dijkstra routing to minimize insertion loss | Our implementation | Standard graph optimization |
| **GDSII Layout Export** | Generates binary .gds mask files with waveguide and heater polygons | Implementation | GDSII stream format spec |
| **MATLAB Bridge** | Exports MZI phase vectors to .m files for external co-simulation | Utility | Standard data export |

> **Important clarification:** Qfóton is a *software simulator*. The QRNG module models a photonic beam-splitter measurement process using stochastic sampling - it is not connected to physical quantum hardware. The GDSII export generates layout geometry files that would require external DRC validation before any actual fabrication. All noise parameters are drawn from published experimental data, not from our own lab measurements.

---

## Benchmark: Science (2015) Reproduction

Qfóton's noise model is calibrated against published experimental data from Carolan et al., "Universal linear optics," Science 349.6249 (2015).

| Metric | Published Lab Value | Qfóton Simulation | Notes |
| :--- | :--- | :--- | :--- |
| Gate Process Fidelity | 99.40% +/- 0.30% | 99.98% +/- 0.07% | Simulated unitary metric |
| HOM Visibility | 97.50% +/- 1.20% | 97.46% | Within published error bar |
| Waveguide Loss | 0.148 dB/cm | 0.148 dB/cm | Input parameter from paper |
| Thermal Recovery (K^-1) | ~50% to 100% | 7.6% to 100% | Analytical matrix inversion |
| Heralded Purity g2(0) | 0.004 +/- 0.001 | 0.0045 | Within published error bar |

---

## Python API Example

```python
import numpy as np
from simulator.clements_compiler import ClementsCompiler
from simulator.hardware_noise import CleanroomNoiseModel
from simulator.thermal_crosstalk import ThermalCrossTalkOptimizer
from simulator.gds_layout import GDSIIPhotonicLayout

# 1. Compile a unitary into MZI mesh
compiler = ClementsCompiler(num_modes=4)
mesh = compiler.decompose(np.eye(4))  # or parse from OpenQASM

# 2. Simulate hardware noise
noise = CleanroomNoiseModel(loss_db_per_cm=0.148, phase_jitter_std=0.019)
noisy_U = noise.apply_noise(mesh['reconstructed_unitary'])

# 3. Calibrate thermal cross-talk
cal = ThermalCrossTalkOptimizer(num_mzis=len(mesh['mzi_list']))
calibrated = cal.invert_thermal_cross_talk(target_phases=mesh['phase_vector'])

# 4. Export GDSII layout
gds = GDSIIPhotonicLayout(num_modes=4)
gds.build_clements_mesh(mesh['mzi_list'])
gds.export_gdsii("my_chip.gds")
```

---

## Project Structure

```
qfoton/
  run_demo.py                  # Runs the full simulation suite
  simulate_chip.py             # Interactive circuit studio
  simulate_custom_chip.py      # CLI for custom circuits and presets
  simulate_science_2015_chip.py # Science (2015) benchmark reproduction
  simulator/
    clements_compiler.py       # Clements SU(N) decomposition
    reck_compiler.py           # Reck triangular decomposition
    hardware_noise.py          # 220nm SOI noise model
    thermal_crosstalk.py       # K^-1 thermal calibration
    pid_phase_stabilizer.py    # PID drift correction
    hom_interference.py        # Hong-Ou-Mandel simulator
    photonic_qrng.py           # QRNG beam-splitter simulation
    gds_layout.py              # Binary GDSII mask export
    ...                        # 30+ additional modules
  notebooks/
    qfoton_quickstart.ipynb    # Google Colab quickstart
  tests/
    test_quantum_suite.py      # Automated test suite
```

---

## Key References

* Carolan, J., et al. "Universal linear optics." Science 349.6249 (2015): 711-716.
* Clements, W. R., et al. "Optimal design for universal multiport interferometers." Optica 3.12 (2016): 1460-1465.
* Hong, C. K., Ou, Z. Y., & Mandel, L. "Measurement of subpicosecond time intervals between two photons by interference." PRL 59.18 (1987): 2044.
* Bartolucci, S., et al. "Fusion-based quantum computation." Nature Communications 14.1 (2023): 912.
* Madsen, L. S., et al. "Quantum computational advantage with a programmable photonic processor." Nature 606 (2022): 75-81.
* Temme, K., Bravyi, S., & Gambetta, J. M. "Error mitigation for short-depth quantum circuits." PRL 119.18 (2017): 180509.

---

## License

Released under the **MIT License**. Copyright (c) 2026 Atharve and the Qfóton Contributors.
