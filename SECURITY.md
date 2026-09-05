# Security Policy

## Supported Versions

Security updates are applied to the following versions of Qfóton:

| Version | Supported          |
| ------- | ------------------ |
| 2.x     | :white_check_mark: |
| 1.x     | :x:                |

## Reporting a Vulnerability

We take the security and integrity of Qfóton seriously. If you discover a security vulnerability in the codebase, simulation algorithms, or dependency chain, please report it responsibly.

### How to Report

1. **Do not create a public issue.**
2. Send an email directly to the project maintainers via GitHub private vulnerability reporting or open a confidential draft security advisory on GitHub.
3. Include the following details in your report:
   - Type of issue (e.g. buffer overflow in C extensions, dependency vulnerability, arbitrary code execution via untrusted QASM circuit parsing)
   - Step-by-step instructions to reproduce the issue
   - Proof of concept script or minimal reproducible example
   - Expected impact on simulation runtimes or host systems

### Response Timeline

- **Initial Response**: Within 48 hours of receiving the vulnerability report.
- **Triage and Confirmation**: Within 5 business days.
- **Patch Release**: High and critical vulnerabilities will receive expedited patches pushed to the main branch and distributed via PyPI.

### Scope

In scope:
- Remote code execution through malformed OpenQASM inputs
- Path traversal vulnerabilities in GDSII layout file generation
- Malicious dependency injection or unsafe deserialization

Out of scope:
- Bugs that only produce unphysical quantum simulation results without compromising host system integrity (please report these as standard GitHub issues)
- Theoretical limitations of classical simulation algorithms
