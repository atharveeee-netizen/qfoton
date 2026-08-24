from setuptools import setup, find_packages

setup(
    name="qfoton",
    version="2.0.0",
    author="Atharve and the Qfóton Contributors",
    author_email="atharveeee@gmail.com",
    description="Full-Stack Silicon Photonic Quantum Computing Compiler, Multiphysics Simulator & GDSII Foundry CAD Engine",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/atharveeee-netizen/qfoton",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
    ],
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.22.0",
        "scipy>=1.8.0",
        "matplotlib>=3.5.0",
    ],
)
