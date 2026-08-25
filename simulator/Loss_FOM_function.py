# -*- coding: utf-8 -*-
# ==============================================================================
# Qfóton: Hardware-Aware Silicon Photonic Quantum Compiler & Simulator
# Copyright (c) 2026 Atharve and the Qfóton Contributors. All rights reserved.
# Released under the MIT License.
# ==============================================================================
"""
Created on Sun May  4 12:55:26 2025

@author: Hüttenbrenner
the Loss figure of Merit function is defined here
"""
from .Basis import *
from .Gates import * 
from .Circuit import * 
from .Phi_func import *
from .NS_Gate import *
from .Mask import *
import numpy as np
 
def Loss_FOM(circuit, P_Loss, num_modes, max_photons, input_idx, output_idx, heralding_pattern_idx): # expects a circuit class object, the probabilty to loose a photon, the number of modes, the maximal (the usefull) photon number (4 in our case), input state, desired output state and the heralding pattern
    
     #you calculate the General success probability for the one Input state we care about, it shoud not be renormalized. you multiply that by 	P_no_loss = 1-P_Loss
     #Then find the probabilty that for our input state we get a false herald but no loss, e.g. all the ways bunching can happen - remove bunching later?? - take more than one possible input state??
     # -also multiply by no loss prob
     # collect prob for all lossy cases of the one input state we have (i.e. each photon could get lost) to trigger a false herald and multiply with p loss **1 * p_no_loss**3
     # You divide the succ prob by all the fail probs, including the false herald with no loss.
	 # this is your figure of Merit - it implizitly depends on first bs angles through circuit and on p_loss
     Basis_complete = Basis(max_photons, num_modes)
     basis = Basis_complete.fock
     
     succ = np.abs(Phi(input_idx, output_idx, circuit.unitary).get_amplitudes()).item()**2*(1-P_Loss)**max_photons # all 4 photons dont get lost!
     
     heralding_click_mask = np.zeros(num_modes)
     heralding_click_mask[heralding_pattern_idx] = 1 #at the positions of the detectors, the click mask should be one
     no_loss_false_herald_outputs = apply_click_mask(basis, heralding_click_mask, np.zeros(num_modes)) #make an idx list of all no loss false herald outputs that can occur. if this list turns out empty you need to set the prob zero! or throw an exception
     no_loss_false_herlad_outputs = apply_mask(no_loss_false_herald_outputs, output_idx, np.ones((len(output_idx))), exclude = 2) #remove the correct output form the list
     no_loss_false_herald_outputs_idx = fock_list_to_idx_list(no_loss_false_herald_outputs)
    
     no_loss_false_herald_array = np.abs(Phi(input_idx, no_loss_false_herald_outputs_idx, circuit.unitary).get_amplitudes())**2
     #mulitiply later with P_no_loss **4 because all 4 photons dont get lost             // Dont renormalize that, right?
     
     # loss
     Basis_loss = Basis(max_photons-1, num_modes)
     basis_loss = Basis_loss.fock
     heralding_click_mask_loss = np.zeros(num_modes)
     heralding_click_mask_loss[heralding_pattern_idx] = 1
     loss_false_herald_outputs = apply_click_mask(basis_loss, heralding_click_mask_loss, np.zeros(num_modes)) #make an idx list of all no loss false herald outputs that can occur. if this list turns out empty you need to set the prob zero! or throw an exception
     loss_false_herald_outputs_idx = fock_list_to_idx_list(loss_false_herald_outputs) #in our case there will only be one output state that can reproduce the heralding pattern in a lossy case, but this code aims to be general
     
     lossy_inputs = []
     for i in range(len(input_idx)):
         lossy = np.delete(input_idx, i)  # removes the i-th element
         lossy_inputs.append(lossy)

     lossy_inputs_idx = np.array(lossy_inputs)
     
     loss_false_herald_array = np.abs(Phi(lossy_inputs_idx, loss_false_herald_outputs_idx, circuit.unitary).get_amplitudes())**2 #just gives empty array, why?

     
     return succ/(np.sum(loss_false_herald_array)* P_Loss * (1-P_Loss)**(max_photons - 1)) # np.sum(no_loss_false_herald_array) * (1-P_Loss)**max_photons +
 
    
 
    #%% test case
    
# #%%specify photon and mode number
num_modes = 10

#sweep these angles. keep t_81 = t_91 for now.
t_81 = 45 
p_81 = 0     #phase can stay 0
t_91 = 45 #the 9 and the 8 refere to the ancilla modes they go to
p_91 = 0
#build a function to always find the counter with these angles.
t_82 = 90 #set the angle of the additional beamsplitter connecting the helper modes to the main detector mode index 1
p_82 = 0     #phase can stay 0
t_92 = 90 #the 9 and the 8 refere to the ancilla modes they go to
p_92 = 0

#%%Generate the gates and circuit
# Gate_1  = Gate(H, [0,1], num_modes)# the array in the function's argument tells us which two modes are involved in the gate
# Gate_2  = Gate(H, [1,4], num_modes)
# Gate_3  = Gate(BS(t_81,p_81), [2,8], num_modes)
# Gate_4  = Gate(BS(t_91,p_91), [5,9], num_modes)
# Gate_5  = Gate(NS,[1,2,3], num_modes)
# Gate_6  = Gate(NS,[4,5,6], num_modes)
# Gate_7  = Gate(H, [1,4], num_modes)
# Gate_8  = Gate(H, [0,1], num_modes)
# Gate_9  = Gate(BS(t_82,p_82), [1,8], num_modes)
# Gate_10 = Gate(BS(t_92,p_92), [1,9], num_modes)

# Gates_in_order = [Gate_1, Gate_2, Gate_3, Gate_4, Gate_5, Gate_6, Gate_7, Gate_8, Gate_9, Gate_10] #leftmost gate in circuit is also on the left in this list


# num_photons = 4

# basis = Basis(num_photons, num_modes)

# Circuit = Circuit(Gates_in_order, num_modes)
 
# test_loss_fom = Loss_FOM(Circuit, 0.001, num_modes, num_photons, np.array([0,2,4,5]), np.array([1,2,4,5]), np.array([1,2,5])) 
     
     
     
     
  

