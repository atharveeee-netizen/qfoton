# -*- coding: utf-8 -*-
# ==============================================================================
# Qfóton: Hardware-Aware Silicon Photonic Quantum Compiler & Simulator
# Copyright (c) 2026 Atharve and the Qfóton Contributors. All rights reserved.
# Released under the MIT License.
# ==============================================================================
"""
Created on Sun Mar 16 13:39:05 2025

@author: Hüttenbrenner
"""

from .Gates import *
from .Circuit import *
import numpy as np

#%% specify the angles

# #x=-1 case
phi_1 = 0
phi_2 = 0
phi_3 = 0
phi_4 = 180

theta_1 = 22.5
theta_2 = 65.5302
theta_3 = -22.5



# #x= exp(iπ/2) case
# phi_1 = 88.24
# phi_2 = -66.52
# phi_3 = -11.25
# phi_4 = 102.24

# theta_1 = 36.53
# theta_2 = 62.25
# theta_3 = -36.53


#make the individual gates
num_modes_ns = 3

P_phi_4 = Gate(P(phi_4, 0), np.array([0,1]), num_modes_ns)
BS_11   = Gate(BS_NS(theta_1, phi_1), np.array([1,2]), num_modes_ns)
BS_22   = Gate(BS_NS(theta_2, phi_2), np.array([0,1]), num_modes_ns)
BS_33   = Gate(BS_NS(theta_3, phi_3), np.array([1,2]), num_modes_ns)

NS_LO_circuit = Circuit([P_phi_4, BS_11, BS_22, BS_33], 3)
NS   = NS_LO_circuit.unitary 


#%% compare amplitudes - > do the alpha vs beta comparison in the NS