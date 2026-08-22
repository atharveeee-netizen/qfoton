"""
Realistic Photonic Hardware Noise and Loss Engine (Quandela and Bristol Model).
"""
import numpy as np

class PhotonicHardwareNoiseModel:
    def __init__(self, propagation_loss_db_per_cm: float = 0.15, chip_length_cm: float = 2.0,
                 indistinguishability_v: float = 0.992, g2_zero: float = 0.005,
                 snspd_dark_count_hz: float = 10.0, snspd_dead_time_ns: float = 20.0):
        self.loss_db = propagation_loss_db_per_cm * chip_length_cm
        self.transmittance = 10.0 ** (-self.loss_db / 10.0)
        self.visibility = indistinguishability_v
        self.g2_0 = g2_zero
        self.dcr = snspd_dark_count_hz
        self.dead_time = snspd_dead_time_ns

    def apply_loss_to_state(self, photon_number: int) -> int:
        transmitted = 0
        for _ in range(photon_number):
            if np.random.rand() < self.transmittance:
                transmitted += 1
        return transmitted

    def get_hom_visibility(self) -> float:
        return self.visibility * (1.0 - self.g2_0)
