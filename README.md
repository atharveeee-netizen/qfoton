# Qfóton

A full-stack linear optical quantum computing platform and silicon photonic chip simulator. Features interactive drag-and-drop circuit design, universal Clements and Reck SU(N) unitary compilation, Hong-Ou-Mandel quantum interference, and #P-hard matrix permanent Boson Sampling.

**Live Application**: [https://atharveeee-netizen.github.io/qfoton/](https://atharveeee-netizen.github.io/qfoton/)  
**GitHub Repository**: [https://github.com/atharveeee-netizen/qfoton](https://github.com/atharveeee-netizen/qfoton)

---

## Interactive Web Suite

Experience Qfóton in your browser:
* **[Quantum Circuit Studio](https://atharveeee-netizen.github.io/qfoton/)**: Visual drag-and-drop circuit designer with live measurement probabilities and state vectors.
* **[3D Photonic Chip Simulator](https://atharveeee-netizen.github.io/qfoton/photonic.html)**: Interactive silicon waveguide mesh, directional couplers, and real-time Hong-Ou-Mandel dip analysis.
* **[Canvas Quantum Visualizer](https://atharveeee-netizen.github.io/qfoton/wybiral/index.html)**: Interactive canvas circuit stepping engine.

---

## Python Simulation Core & Quick Start

### 1. Requirements
Install standard scientific libraries:
```bash
pip install numpy scipy matplotlib
```

### 2. 1-Command CLI Demo Suite
Run all physical simulations with formatted ASCII tables:
```bash
python run_demo.py
```

### 3. Compile Arbitrary Unitary Matrix to Physical Silicon MZIs
```python
import numpy as np
from simulator.clements_compiler import clements_decompose

# Random 4x4 unitary (Haar measure)
z = (np.random.randn(4, 4) + 1j * np.random.randn(4, 4)) / np.sqrt(2.0)
U, _ = np.linalg.qr(z)

# Decompose into physical MZI phase angles
mzi_schedule = clements_decompose(U)
for mzi in mzi_schedule:
    print(f"Modes ({mzi[0]}, {mzi[1]}) -> Theta: {mzi[2]:.3f} rad, Phi: {mzi[3]:.3f} rad")
```

---

## Benchmarks & Performance

| Matrix Size (N) | Classical Determinant (ms) | Classical Permanent (ms) | Optical Propagation (0.12 ns) | Speedup Factor |
| :--- | :--- | :--- | :--- | :--- |
| N = 4 | 0.08 ms | 0.13 ms | 0.12 ns | 132x |
| N = 8 | 0.01 ms | 1.53 ms | 0.12 ns | 1,532x |
| N = 10 | 0.03 ms | 6.47 ms | 0.12 ns | 6,465x |
| N = 12 | 0.02 ms | 26.97 ms | 0.12 ns | 26,967x |
| N = 14 | 0.03 ms | 106.83 ms | 0.12 ns | 106,830x |

---

## References

1. Knill, E., Laflamme, R., & Milburn, G. J. (2001). A scheme for efficient quantum computation with linear optics. *Nature*, 409(6816), 46-52.
2. Clements, W. R., et al. (2016). Optimal design for universal multiport interferometers. *Optica*, 3(12), 1460-1465.
3. Reck, M., et al. (1994). Experimental realization of any discrete unitary operator. *Physical Review Letters*, 73(1), 58.
4. Aaronson, S., & Arkhipov, A. (2011). The computational complexity of linear optics. *STOC*, 333-342.
5. Hong, C. K., Ou, Z. Y., & Mandel, L. (1987). Measurement of subpicosecond time intervals between two photons by interference. *Physical Review Letters*, 59(18), 2044.
6. Carolan, J., et al. (2015). Universal linear optics. *Science*, 349(6249), 711-716.
7. Hamilton, C. S., et al. (2017). Gaussian boson sampling. *Physical Review Letters*, 119(17), 170501.
8. Bromley, T. R., et al. (2020). Applications of near-term photonic quantum computers. *Quantum Science and Technology*, 5(3), 034010.
9. Heurtel, N., et al. (2023). Perceval: A software platform for discrete variable photonic quantum computing. *Quantum*, 7, 931.
10. Russell, N. J., et al. (2017). Direct dialling of arbitrary unitary matrices on integrated photonic circuits. *Nature Communications*, 8(1), 1838.
11. James, D. F., et al. (2001). Measurement of qubits. *Physical Review A*, 64(5), 052312.
12. Bogaerts, W., et al. (2020). Programmable photonic circuits. *Nature*, 586(7828), 207-216.

## License
MIT License.
