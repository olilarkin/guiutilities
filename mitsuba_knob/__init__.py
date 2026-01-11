"""
Mitsuba Knob Renderer
=====================
Modern, Python-based knob rendering for VST plugin graphics.
"""

from .knob_config import KnobConfig, PRESETS, get_preset, list_presets

__version__ = '1.0.0'
__all__ = ['KnobConfig', 'PRESETS', 'get_preset', 'list_presets']
