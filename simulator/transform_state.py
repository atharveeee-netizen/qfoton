# -*- coding: utf-8 -*-
# ==============================================================================
# Qfóton: Full-Stack Silicon Photonic Quantum Computing & Compiler Suite
# Copyright (c) 2026 Atharve and the Qfóton Contributors. All rights reserved.
# Released under the MIT License.
# ==============================================================================
"""
Created on Tue Jul 15 11:03:45 2025

@author: Hüttenbrenner

In this file, the ability to transform a general quantum state via the circuit is implemented. It can be any superposition of basis states, formulated in idx notation
"""
from .Circuit import *
from .Phi_func import *
from .Mask import *
from .Basis import *
from typing import Dict, Tuple, List, Any, Optional
import numpy as np
from copy import deepcopy
from collections import Counter


IdxState = Dict[Tuple[int, ...], complex]
#%%helper functions

def make_empty_state(keys_array: np.ndarray) -> IdxState:
    """
    Given a 2D int array of shape (n_keys, n_modes), build
    a dict mapping each index‐tuple → 0+0j.
    """
    state: IdxState = {}
    for row in keys_array:
        # ensure pure Python ints
        key = tuple(int(x) for x in row)
        state[key] = 0+0j
    return state


def renormalize(state: IdxState) -> None:
    """
    Renormalize state in place:
      • Compute the ℓ2‑norm = sqrt(sum |amplitude|^2)
      • Divide each amplitude by that norm.

    Raises:
        ValueError: if the state has zero norm.
    """
    # 1) Compute norm
    norm_sq = sum(abs(amp)**2 for amp in state.values())
    norm = norm_sq**0.5

    if norm == 0:
        raise ValueError("Cannot renormalize: the state has zero norm")

    # 2) Divide each amplitude by the norm
    for basis in state:
        state[basis] /= norm


def prune_small_amplitudes(state: dict[tuple[int, ...], complex],
                           tol: float = 1e-10) -> None:
    """
    Remove any basis entries whose |amplitude| < tol, modifying state in place.
    """
    for basis in list(state):
        if abs(state[basis]) < tol:
            del state[basis]
            
            
def remove_bunching(
    state: IdxState,
    forbidden_modes: list[int]
) -> IdxState:
    """
    Remove any components of the Idx superposition that have more than one
    photon in any of the specified forbidden modes, then renormalize.

    Args:
        state: dict mapping basis‐tuples (e.g. (n0, n1, …)) → complex amplitudes.
        forbidden_modes: list of mode‐indices where multi‐photon terms
                         are not allowed (e.g. [0, 2]).

    Returns:
        A new, renormalized IdxState dict with all “bunched” components removed.
    """
    # 1) Filter out any basis with >1 photon in a forbidden mode
    filtered: IdxState = {
        idx_state: amp
        for idx_state, amp in state.items()
        # idx_state is a tuple of mode‐indices (one per photon),
        # so .count(m) tells you how many photons are in mode m
        if all(idx_state.count(m) <= 1 for m in forbidden_modes)
    }

    # 2) Compute the norm of the filtered state
    norm = sum(abs(amp)**2 for amp in filtered.values()) ** 0.5
    if norm == 0:
        raise ValueError("All amplitudes were removed; cannot renormalize zero‐state")

    # 3) Renormalize in place
    for basis in filtered:
        filtered[basis] /= norm

    return filtered


#%% transfromation
# def transform_state(state: dict[tuple[int, ...], complex], circuit, clicks: list[int] = [], no_clicks: list[int] = [], renorm : bool = True) -> dict[tuple[int, ...], complex]:
#     '''
    

#     Parameters
#     ----------
#     state : dict[tuple[int, ...], complex]
#         Specifies the superposition of basis states in idx formulation that will be transformed
#         the tuple is the idx basis state, and complex is the amplitude of said basis state
    
#     circuit : TYPE Circuit class
#         The circuit 

#     clicks : list[int]
#         Specifies in which modes there must be at least one photon in the end -> this reduces the set of possible outputs
        
#     no_clicks : list[int]
#         Specifies in which modes there must be no photon in the end -> this reduces the set of possible outputs

#     renorm: bool
#         if true, state is renormalized
#     Returns
#     -------
#     transformed_state : dict[tuple[int, ...], complex]
#         The output state you get from sending your state through the circuit

#     '''
    
    
#     #get necessaray info about circuit and state
#     modes = circuit.mode_number
#     U = circuit.get_unitary()
#     first_key = next(iter(state))
#     num_photons = len(first_key)
    
#     #make possible output basis states from the click pattern
#     basis = Basis(num_photons, modes)
#     click_helper = np.zeros((len(clicks)))
#     no_click_helper = np.zeros((len(no_clicks)))
#     ok_outputs = basis.fock
#     ok_outputs = apply_mask(ok_outputs, clicks, click_helper, exclude = 3) if clicks else ok_outputs  #this excludes all states from basis where a mode which must yield a klick has no photon in it
#     ok_outputs = apply_mask(ok_outputs, no_clicks, no_click_helper, exclude = 0) if no_clicks else ok_outputs #excludes all states where a photon is in a mode where we expect no click
#     if(ok_outputs.size==0):
#         raise ValueError("Your restrictions excluded every possible state") 
#     ok_outputs = fock_list_to_idx_list(ok_outputs)
    
#     # go through input state and transfrom the basis states it is made up from, by using them as input to phi. keep track of coefficients though
#     # 1) extract & convert
#     keys_as_lists = [list(k) for k in state.keys()]

#     # 2) build a 2D array of shape (n_keys, n_modes)
#     inputs = np.array(keys_as_lists)
    
#     # 3) transfrom
#     Amplitudes = Phi(inputs, ok_outputs, U).get_amplitudes()

#     #rebuild transformed state
     
#     #make a new state that includes all possible output basis states as keys
#     transformed_state = make_empty_state(ok_outputs)

#     #use Amplitudes and the original state dict to find the new coeffients
#     for i, row in enumerate(ok_outputs):
#         key_out = tuple(int(x) for x in row)
#         for j, amp in enumerate(Amplitudes[:,i]):
#             key_in = tuple(int(x) for x in inputs[j])
#             transformed_state[key_out] += amp*state[key_in]
    
#     #renormalize final state
    
#     if(renorm):
#         renormalize(transformed_state)
    
#     #go through final state and remove elements that are too small
    
#     prune_small_amplitudes(transformed_state)
    
#     return transformed_state

#%% transform state function  that removes bunching before calculation

#make this the regular transform  state function

def transform_state(state: dict[tuple[int, ...], complex], circuit, clicks: list[int] = [], no_clicks: list[int] = [], remove_bunching: List[int] = [], renorm : bool = True) -> dict[tuple[int, ...], complex]:
    '''
    

    Parameters
    ----------
    state : dict[tuple[int, ...], complex]
        Specifies the superposition of basis states in idx formulation that will be transformed
        the tuple is the idx basis state, and complex is the amplitude of said basis state
    
    circuit : TYPE Circuit class
        The circuit 

    clicks : list[int]
        Specifies in which modes there must be at least one photon in the end -> this reduces the set of possible outputs
        
    no_clicks : list[int]
        Specifies in which modes there must be no photon in the end -> this reduces the set of possible outputs
    
    remove_bunching: 
        Exclude states that have multiple photons in these modes
        
    renorm: bool
        if true, state is renormalized
    Returns
    -------
    transformed_state : dict[tuple[int, ...], complex]
        The output state you get from sending your state through the circuit

    '''
    
    
    #get necessaray info about circuit and state
    modes = circuit.mode_number
    U = circuit.get_unitary()
    first_key = next(iter(state))
    num_photons = len(first_key)
    
    #make possible output basis states from the click pattern
    ok_outputs = generate_idx_basis_adv(
        num_photons,
        modes,
        clicks,
        no_clicks,
        remove_bunching,
    )
    
    if(ok_outputs.size==0):
        raise ValueError("Your restrictions excluded every possible state") 

    #print('past possible output generation')
    # go through input state and transfrom the basis states it is made up from, by using them as input to phi. keep track of coefficients though
    # 1) extract & convert
    keys_as_lists = [list(k) for k in state.keys()]

    # 2) build a 2D array of shape (n_keys, n_modes)
    inputs = np.array(keys_as_lists)
    
    # 3) transfrom
    Amplitudes = Phi(inputs, ok_outputs, U).get_amplitudes()

    #rebuild transformed state
     
    #make a new state that includes all possible output basis states as keys
    transformed_state = make_empty_state(ok_outputs)

    #use Amplitudes and the original state dict to find the new coeffients
    for i, row in enumerate(ok_outputs):
        key_out = tuple(int(x) for x in row)
        for j, amp in enumerate(Amplitudes[:,i]):
            key_in = tuple(int(x) for x in inputs[j])
            transformed_state[key_out] += amp*state[key_in]
    
    #renormalize final state
    
    if(renorm):
        renormalize(transformed_state)
    
    #go through final state and remove elements that are too small
    
    prune_small_amplitudes(transformed_state)
    
    return transformed_state



#%%
# --- small helpers on your state representation: dict[FockTuple] -> complex ---

Fock = Tuple[int, ...]
StateDict = Dict[Fock, complex]

def state_norm2(state: StateDict) -> float:
    return float(sum(abs(a)**2 for a in state.values()))

def normalize_state_inplace(state: StateDict) -> None:
    n2 = state_norm2(state)
    if n2 > 0.0:
        s = 1.0 / np.sqrt(n2)
        for k in list(state.keys()):
            state[k] *= s

def canonical_key(state: StateDict):
    # Used to merge identical outputs after normalization
    # complex is hashable, so (key, amp) tuples are fine
    return tuple(sorted(state.items()))

#%% ---first try main: mixture as a LIST of (state_dict, prob) ---



# def transform_mixture_list(
#     mixture: List[Tuple[StateDict, float]],
#     circuit,
#     clicks: Optional[List[int]] = None,
#     no_clicks: Optional[List[int]] = None,
#     *,
#     return_componentwise: bool = False
# ):
#     """
#     mixture: list of (state_dict, p_k), with sum p_k = 1
#     Returns (default):
#         out_mixture_list: list of (normalized_state_dict, updated_prob)
#         success_prob: total heralding success probability = sum_k p_k * s_k
#     If return_componentwise=True, returns a 3rd value:
#         per_component: list aligned with `mixture`, where each entry is
#             (normalized_state_dict_or_None, updated_prob_or_NaN, info_dict)
#         info_dict has keys: {"ok": bool, "error": str|None, "s_k": float}
#     """
#     if clicks is None: clicks = []
#     if no_clicks is None: no_clicks = []

#     # Accumulate surviving components for merging
#     weighted = []  # (canonical_key, p_k * s_k, normalized_state_dict)
#     total_success = 0.0

#     # Per-component log (same length/order as mixture)
#     per_component = []

#     for idx, (state_in, p_k) in enumerate(mixture):
#         # Try to transform WITHOUT renorm to keep heralding weight
#         try:
#             out_unnorm = transform_state(
#                 deepcopy(state_in), circuit,
#                 clicks=clicks, no_clicks=no_clicks, renorm=False
#             )
#         except Exception as e:
#             # Incompatible with heralding (or other error):
#             # contribute zero weight; mark component as NaN in the log.
#             per_component.append((None, np.nan, {"ok": False, "error": str(e), "s_k": 0.0}))
#             continue

#         # Component success probability s_k = ||out||^2
#         s_k = state_norm2(out_unnorm)
#         if s_k == 0.0:
#             # Survives with zero probability → NaN in per-component prob (undefined)
#             per_component.append((None, np.nan, {"ok": False, "error": None, "s_k": 0.0}))
#             continue

#         # Normalized branch for the surviving component
#         out_norm = deepcopy(out_unnorm)
#         normalize_state_inplace(out_norm)

#         # Track it for merging
#         weighted.append((canonical_key(out_norm), p_k * s_k, out_norm))
#         total_success += p_k * s_k

#         # Temporarily store q_k as None; we’ll fill after we know total_success
#         per_component.append((out_norm, None, {"ok": True, "error": None, "s_k": float(s_k)}))

#     # If no component survives, return empty mixture + 0 success
#     if total_success == 0.0:
#         if return_componentwise:
#             # Fill q_k=NaN for all entries (already NaN for failures; set for successes too)
#             per_component = [
#                 (st if info["ok"] else None, np.nan, info)
#                 for (st, _q_unused, info) in per_component
#             ]
#             return [], 0.0, per_component
#         return [], 0.0

#     # Merge identical normalized outputs, summing weights
#     merged_weights: Dict[Tuple[Fock, ...], float] = {}
#     reps: Dict[Tuple[Fock, ...], StateDict] = {}
#     for key, w, st in weighted:
#         merged_weights[key] = merged_weights.get(key, 0.0) + w
#         if key not in reps:
#             reps[key] = st

#     # Convert weights -> probabilities by dividing by total_success
#     out_list = []
#     for key, w in merged_weights.items():
#         q = w / total_success
#         out_list.append((reps[key], q))

#     # Fill per-component q_k now (NaN for failures)
#     if return_componentwise:
#         new_per_component = []
#         for (st, _q_placeholder, info), (state_in, p_k) in zip(per_component, mixture):
#             if not info["ok"]:
#                 new_per_component.append((None, np.nan, info))
#             else:
#                 q_k = (p_k * info["s_k"]) / total_success
#                 new_per_component.append((st, float(q_k), info))
#         per_component = new_per_component
#         return out_list, float(total_success), per_component

#     return out_list, float(total_success)

#%% strip bunching function for old version
def _strip_bunching(state: StateDict, remove_bunching: List[int]) -> StateDict:
    """
    Return a copy of `state` with any idx-basis elements removed that have
    >= 2 photons in any mode listed in `remove_bunching`.
    (idx convention: tuple entries are mode indices of individual photons)
    """
    if not remove_bunching:
        return state
    rb = set(int(m) for m in remove_bunching)
    out: StateDict = {}
    for idx, amp in state.items():
        counts = Counter(idx)            # e.g. (0,0,2) -> {0:2, 2:1}
        if any(counts.get(m, 0) >= 2 for m in rb):
            continue                     # drop bunched outputs in those modes
        out[idx] = amp
    return out
#%% this worked, but it removed bunching afterwards which was slow
# def transform_mixture_list(
#     mixture: List[Tuple[StateDict, float]],
#     circuit,
#     clicks: Optional[List[int]] = None,
#     no_clicks: Optional[List[int]] = None,
#     *,
#     remove_bunching: Optional[List[int]] = None,
#     return_componentwise: bool = False
# ):
#     """
#     mixture: list of (state_dict, p_k), with sum p_k = 1

#     remove_bunching: list[int] | None
#         If provided, drop ANY output basis ket that has >=2 photons in any
#         of these modes (idx convention) BEFORE computing s_k and normalization.

#     Returns (default):
#         out_mixture_list: list of (normalized_state_dict, updated_prob)
#         success_prob: total heralding success probability = sum_k p_k * s_k

#     If return_componentwise=True, also returns:
#         per_component: list aligned with `mixture`, each entry:
#             (normalized_state_dict_or_None, updated_prob_or_NaN, info_dict)
#         where info_dict = {"ok": bool, "error": str|None, "s_k": float}
#     """
#     if clicks is None: clicks = []
#     if no_clicks is None: no_clicks = []
#     if remove_bunching is None: remove_bunching = []

#     weighted = []   # (canonical_key, p_k * s_k, normalized_state_dict)
#     total_success = 0.0
#     per_component = []

#     for idx_comp, (state_in, p_k) in enumerate(mixture):
#         # 1) Transform WITHOUT renorm to keep heralding weight
#         try:
#             out_unnorm = transform_state(
#                 deepcopy(state_in), circuit,
#                 clicks=clicks, no_clicks=no_clicks, renorm=False
#             )
#         except Exception as e:
#             # Incompatible component: contributes zero, report NaN
#             per_component.append((None, np.nan, {"ok": False, "error": str(e), "s_k": 0.0}))
#             continue

#         # 1.5) Enforce de-bunching *before* computing s_k
#         if remove_bunching:
#             out_unnorm = _strip_bunching(out_unnorm, remove_bunching)

#         # 2) Component success probability AFTER filtering
#         s_k = state_norm2(out_unnorm)
#         if s_k == 0.0:
#             per_component.append((None, np.nan, {"ok": False, "error": None, "s_k": 0.0}))
#             continue

#         # 3) Normalize this surviving branch
#         out_norm = deepcopy(out_unnorm)
#         normalize_state_inplace(out_norm)

#         # 4) Accumulate for merging
#         weighted.append((canonical_key(out_norm), p_k * s_k, out_norm))
#         total_success += p_k * s_k
#         per_component.append((out_norm, None, {"ok": True, "error": None, "s_k": float(s_k)}))

#     # If nothing survives
#     if total_success == 0.0:
#         if return_componentwise:
#             per_component = [
#                 (st if info["ok"] else None, np.nan, info)
#                 for (st, _q_unused, info) in per_component
#             ]
#             return [], 0.0, per_component
#         return [], 0.0

#     # 5) Merge identical normalized outputs, sum weights
#     merged_weights: Dict[Tuple[Fock, ...], float] = {}
#     reps: Dict[Tuple[Fock, ...], StateDict] = {}
#     for key, w, st in weighted:
#         merged_weights[key] = merged_weights.get(key, 0.0) + w
#         if key not in reps:
#             reps[key] = st

#     # 6) Convert weights -> probabilities
#     out_list = [(reps[key], w / total_success) for key, w in merged_weights.items()]

#     if return_componentwise:
#         filled = []
#         for (st, _q_placeholder, info), (_state_in, p_k) in zip(per_component, mixture):
#             if not info["ok"]:
#                 filled.append((None, np.nan, info))
#             else:
#                 q_k = (p_k * info["s_k"]) / total_success
#                 filled.append((st, float(q_k), info))
#         return out_list, float(total_success), filled

#     return out_list, float(total_success)
#%%
def transform_mixture_list(
    mixture: List[Tuple[StateDict, float]],
    circuit,
    clicks: Optional[List[int]] = None,
    no_clicks: Optional[List[int]] = None,
    *,
    remove_bunching: Optional[List[int]] = None,
    return_componentwise: bool = False
):
    """
    mixture: list of (state_dict, p_k), with sum p_k = 1

    remove_bunching: list[int] | None
        If provided, drop ANY output basis ket that has >=2 photons in any
        of these modes (idx convention) BEFORE computing s_k and normalization.

    Returns (default):
        out_mixture_list: list of (normalized_state_dict, updated_prob)
        success_prob: total heralding success probability = sum_k p_k * s_k

    If return_componentwise=True, also returns:
        per_component: list aligned with `mixture`, each entry:
            (normalized_state_dict_or_None, updated_prob_or_NaN, info_dict)
        where info_dict = {"ok": bool, "error": str|None, "s_k": float}
    """
    if clicks is None: clicks = []
    if no_clicks is None: no_clicks = []
    if remove_bunching is None: remove_bunching = []

    weighted = []   # (canonical_key, p_k * s_k, normalized_state_dict)
    total_success = 0.0
    per_component = []

    for idx_comp, (state_in, p_k) in enumerate(mixture):
        # 1) Transform WITHOUT renorm to keep heralding weight
        try:
            out_unnorm = transform_state( #fails for one of the lossy states but works for the other -> look at that more
                deepcopy(state_in), circuit,
                clicks=clicks, no_clicks=no_clicks, remove_bunching = remove_bunching, renorm=False
            )
        except Exception as e:
            # Incompatible component: contributes zero, report NaN
            per_component.append((None, np.nan, {"ok": False, "error": str(e), "s_k": 0.0}))
            continue


        # 2) Component success probability AFTER filtering
        s_k = state_norm2(out_unnorm)
        if s_k == 0.0:
            per_component.append((None, np.nan, {"ok": False, "error": None, "s_k": 0.0}))
            print('WARNING: You might have lost a state')
            continue

        # 3) Normalize this surviving branch
        out_norm = deepcopy(out_unnorm)
        normalize_state_inplace(out_norm)

        # 4) Accumulate for merging
        weighted.append((canonical_key(out_norm), p_k * s_k, out_norm))
        total_success += p_k * s_k
        per_component.append((out_norm, None, {"ok": True, "error": None, "s_k": float(s_k)}))

    # If nothing survives
    if total_success == 0.0:
        if return_componentwise:
            per_component = [
                (st if info["ok"] else None, np.nan, info)
                for (st, _q_unused, info) in per_component
            ]
            return [], 0.0, per_component
        return [], 0.0

    # 5) Merge identical normalized outputs, sum weights
    merged_weights: Dict[Tuple[Fock, ...], float] = {}
    reps: Dict[Tuple[Fock, ...], StateDict] = {}
    for key, w, st in weighted:
        merged_weights[key] = merged_weights.get(key, 0.0) + w
        if key not in reps:
            reps[key] = st

    # 6) Convert weights -> probabilities
    out_list = [(reps[key], w / total_success) for key, w in merged_weights.items()]

    if return_componentwise:
        filled = []
        for (st, _q_placeholder, info), (_state_in, p_k) in zip(per_component, mixture):
            if not info["ok"]:
                filled.append((None, np.nan, info))
            else:
                q_k = (p_k * info["s_k"]) / total_success
                filled.append((st, float(q_k), info))
        return out_list, float(total_success), filled

    return out_list, float(total_success)


#generate the basis once for each photon number, and immediately cut it down with respect to: bunching, clicks, no clicks
#only use the truncated basis to calculate outputs


#%% I dont want to think about the tensorproduct state my self
from collections import defaultdict


def tensorproduct(state1, state2, *, mode_offset=0, canonicalize=sorted, tol=0.0):
    """
    Tensor product of two photonic states stored as dicts:
      state = { (m1,m2,...,mk): amplitude, ... }

    Parameters
    ----------
    mode_offset : int
        Added to every mode index in state2 before combining.
        Use this if state2 lives in a disjoint set of modes.
        Example: mode_offset = max_mode_in_state1
    canonicalize : callable
        Function that turns the combined key into a canonical tuple.
        Default: sorted -> tuples represent multisets of occupied modes.
        If photons are distinguishable (order matters), use canonicalize=lambda x: x
    tol : float
        Drop terms with |amp| <= tol after summing.

    Returns
    -------
    dict
    """
    out = defaultdict(complex)

    for k1, a1 in state1.items():
        k1 = tuple(k1)
        for k2, a2 in state2.items():
            k2 = tuple(m + mode_offset for m in k2)

            combined = k1 + k2
            combined = tuple(canonicalize(combined))

            out[combined] += a1 * a2

    if tol > 0:
        out = {k: v for k, v in out.items() if abs(v) > tol}
    else:
        out = dict(out)
    renormalize(out)

    return out


def max_mode(state):
    """Helper: maximum mode index appearing in a state (0 if empty)."""
    return max((max(k) for k in state.keys()), default=0)


# #test
# psi = {(1,5,6): np.sqrt(1/3), (2,5,6): -np.sqrt(2/3)}
# phi = {(1,): 1/np.sqrt(2), (3,): 1/np.sqrt(2)}

# # Same mode-label space (photons just add into the same set of modes)
# tp = tensorproduct(psi, phi)
