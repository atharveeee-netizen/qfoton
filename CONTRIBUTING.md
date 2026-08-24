# Contributing to Qfóton

We welcome contributions to Qfóton from quantum physicists, optical engineers, semiconductor designers, and software developers.

## Development Workflow
1. Fork the repository and create a branch for your feature (`git checkout -b feature/quantum-module`).
2. Implement your physical simulation or compilation engine in `simulator/`.
3. Add corresponding tests and verify with:
   ```bash
   python run_demo.py
   ```
4. Submit a Pull Request detailing the theoretical physics equations and benchmark validation results.

## Code Standards
- Adhere to PEP 8 formatting.
- Include LaTeX / Unicode physical documentation in all docstrings.
- Minimize external dependencies (prefer NumPy and SciPy).
