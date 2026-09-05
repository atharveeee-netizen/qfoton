# Contributing to Qfóton

Thank you for your interest in contributing to **Qfóton**! We welcome contributions from quantum physicists, optical engineers, semiconductor designers, and software developers worldwide.

---

## Code of Conduct

All contributors and maintainers must abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it to understand our community standards and expectations.

---

## How Can I Contribute?

You can contribute to Qfóton in multiple ways:

1. **Physical Simulation Engines**: Adding new photonic models (e.g. microring weight banks, squeezed-light states, phase-change materials).
2. **Compiler & Decomposition Algorithms**: Optimizing unitary matrix decompositions, Clements/Reck routing, or open-source QASM transpilers.
3. **Noise & Foundry Calibration**: Grounding noise parameters against peer-reviewed experimental literature or foundry PDK specs (IMEC, AIM Photonics, AMF, LioniX).
4. **Benchmarking**: Adding reproducible physics benchmarks comparing physical simulations against classical or optical experiments.
5. **Documentation & Examples**: Expanding tutorial notebooks, cleanroom guides, and API documentation.

---

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/atharveeee-netizen/qfoton.git
cd qfoton
```

### 2. Create a Virtual Environment

```bash
# On Linux / macOS
python3 -m venv venv
source venv/bin/activate

# On Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies in Editable Mode

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

---

## Testing & Physical Verification

Every pull request must pass the automated test suite and maintain physical consistency.

### Run Automated Unit Tests
```bash
pytest tests/test_quantum_suite.py -v
```

### Run the 16-Stage Master Physical Simulation Suite
```bash
python run_demo.py
```

### Run the SOTA Scientific Benchmark Suite
```bash
python benchmarks/run_sota_benchmarks.py
```

### Run Carolan et al. Science (2015) Reproduction
```bash
python simulate_science_2015_chip.py
```

---

## Coding Standards

1. **Python Style**: Follow PEP 8 guidelines. Keep line lengths reasonable (under 100 characters where possible).
2. **Type Hints**: Include type annotations for all new public functions and class constructors.
3. **Physical Units & Documentation**: 
   - State units explicitly in variable names or docstrings (e.g. `loss_db_per_cm`, `transit_time_ns`, `heater_resistance_ohms`).
   - Ground novel noise parameters with academic citations (Author, Journal, Year, DOI).
4. **Zero AI Slop**: Write clear, mathematically precise docstrings. Avoid generic placeholder text or empty comments.
5. **Purity of Dependencies**: Prefer NumPy and SciPy for numerical and matrix computations. Avoid adding heavyweight frameworks unless strictly necessary.

---

## Submitting a Pull Request

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Commit your changes with descriptive commit messages:
   ```bash
   git commit -m "feat(simulator): add spontaneous four-wave mixing CAR model"
   ```
3. Ensure all tests pass locally:
   ```bash
   pytest tests/test_quantum_suite.py
   python run_demo.py
   ```
4. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a Pull Request on GitHub against `main`. Fill out the Pull Request template completely, detailing your methodology, mathematical formulations, and validation results.

---

## Attribution & License

By contributing to Qfóton, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
