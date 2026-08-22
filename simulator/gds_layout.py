"""
Silicon Photonic Integrated Circuit (PIC) Layout Geometry Exporter.
"""
import json
from typing import List, Dict

class PhotonicLayoutExporter:
    def __init__(self, waveguide_width_nm: float = 450.0, bend_radius_um: float = 10.0):
        self.width = waveguide_width_nm
        self.radius = bend_radius_um

    def export_clements_layout(self, mzi_list: List) -> Dict:
        layout = {
            'chip_technology': 'Silicon-on-Insulator (SOI) 220nm',
            'waveguide_width_nm': self.width,
            'bend_radius_um': self.radius,
            'total_mzi_count': len(mzi_list),
            'components': [{'mzi_id': i, 'modes': (m[0], m[1]), 'theta_rad': m[2], 'phi_rad': m[3]} for i, m in enumerate(mzi_list)]
        }
        return layout
