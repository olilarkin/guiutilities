"""
Knob Configuration Examples
============================
Define custom knob styles by creating configuration dictionaries.
These can be loaded and used with the renderer.
"""

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class KnobConfig:
    """Configuration for a knob rendering."""

    # Rotation range
    start_angle: float = -135.0  # degrees
    end_angle: float = 135.0     # degrees

    # Dimensions
    outer_radius: float = 0.9
    inner_radius: float = 0.7
    height: float = 0.3
    view_size: float = 2.6

    # Appearance
    body_color: Tuple[float, float, float] = (0.1, 0.1, 0.1)
    pointer_color: Tuple[float, float, float] = (0.9, 0.9, 0.9)
    background_color: Tuple[float, float, float] = (0.95, 0.95, 0.95)

    # Material properties
    body_material: str = 'plastic'  # 'plastic', 'metal', 'matte'
    pointer_material: str = 'metal'  # 'plastic', 'metal', 'matte'
    metal_type: str = 'Al'  # 'Al', 'Ag', 'Au', 'Cu', 'Cr'
    roughness: float = 0.15

    # Tick marks
    num_ticks: int = 11
    tick_radius: float = 0.02
    show_ticks: bool = True

    # Grooves
    num_grooves: int = 0  # 0 = no grooves
    groove_radius: float = 0.05

    # Pointer style
    pointer_style: str = 'line'  # 'line', 'dot', 'wedge'
    pointer_length: float = 0.6
    pointer_width: float = 0.05

    # Chrome ring
    chrome_ring: bool = False
    chrome_ring_width: float = 0.08

    # Rendering
    samples_per_pixel: int = 64
    max_bounces: int = 6


# Preset configurations
PRESETS = {
    'classic': KnobConfig(
        start_angle=-135,
        end_angle=135,
        body_color=(0.15, 0.15, 0.15),
        pointer_color=(0.8, 0.1, 0.1),
        body_material='plastic',
        pointer_material='matte',
        num_ticks=20,
        pointer_style='line',
    ),

    'sci': KnobConfig(
        start_angle=-150,
        end_angle=150,
        body_color=(0.03, 0.03, 0.03),
        pointer_color=(0.9, 0.9, 0.9),
        body_material='plastic',
        pointer_material='metal',
        metal_type='Ag',
        num_ticks=11,
        num_grooves=30,
        chrome_ring=True,
        pointer_style='line',
        samples_per_pixel=128,
    ),

    'modern': KnobConfig(
        start_angle=-145,
        end_angle=145,
        view_size=2.4,
        body_color=(0.7, 0.7, 0.7),
        pointer_color=(0.95, 0.3, 0.1),
        background_color=(0.12, 0.12, 0.12),
        body_material='metal',
        metal_type='Al',
        roughness=0.1,
        pointer_material='matte',
        num_ticks=0,
        pointer_style='dot',
        pointer_length=0.6,
        pointer_width=0.08,
        samples_per_pixel=128,
        max_bounces=8,
    ),

    'vintage': KnobConfig(
        start_angle=-135,
        end_angle=135,
        body_color=(0.6, 0.55, 0.45),  # Cream/ivory
        pointer_color=(0.1, 0.1, 0.1),
        body_material='plastic',
        pointer_material='matte',
        num_ticks=11,
        pointer_style='wedge',
        pointer_width=0.08,
    ),

    'mini': KnobConfig(
        start_angle=-150,
        end_angle=150,
        outer_radius=0.7,
        view_size=2.0,
        body_color=(0.2, 0.2, 0.2),
        pointer_color=(1.0, 1.0, 1.0),
        body_material='plastic',
        pointer_material='matte',
        num_ticks=0,
        pointer_style='line',
        pointer_length=0.5,
        pointer_width=0.03,
        samples_per_pixel=32,
    ),

    'gold': KnobConfig(
        start_angle=-135,
        end_angle=135,
        body_color=(0.83, 0.69, 0.22),
        pointer_color=(0.05, 0.05, 0.05),
        body_material='metal',
        metal_type='Au',
        roughness=0.08,
        pointer_material='matte',
        num_ticks=12,
        pointer_style='dot',
        chrome_ring=True,
        samples_per_pixel=128,
        max_bounces=8,
    ),
}


def get_preset(name: str) -> KnobConfig:
    """Get a preset configuration by name."""
    if name not in PRESETS:
        available = ', '.join(PRESETS.keys())
        raise ValueError(f"Unknown preset '{name}'. Available: {available}")
    return PRESETS[name]


def list_presets() -> List[str]:
    """List all available preset names."""
    return list(PRESETS.keys())
