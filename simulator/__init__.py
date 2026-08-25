# -*- coding: utf-8 -*-
# ==============================================================================
# Qfóton: Hardware-Aware Silicon Photonic Quantum Compiler & Simulator
# Copyright (c) 2026 Atharve and the Qfóton Contributors. All rights reserved.
# Released under the MIT License.
# ==============================================================================
"""

"""

import os
import glob
import importlib

# Get the current directory (i.e., folder/)
module_dir = os.path.dirname(__file__)
module_files = glob.glob(os.path.join(module_dir, "*.py"))

# Dynamically import all modules except __init__.py and private files
for path in module_files:
    module_name = os.path.basename(path)[:-3]  # remove ".py"
    if module_name.startswith("_") or module_name == "__init__":
        continue
    module = importlib.import_module(f".{module_name}", package=__name__)
    # Import everything (*) from each module
    for attr in dir(module):
        if not attr.startswith("_"):  # skip private/internal symbols
            globals()[attr] = getattr(module, attr)

