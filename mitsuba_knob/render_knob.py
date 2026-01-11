#!/usr/bin/env python3
"""
Modern Knob Renderer using Mitsuba 3
=====================================
A fast, physically-based renderer for VST plugin knob graphics.

Replaces the legacy POV-Ray workflow with Mitsuba 3's Python API,
offering significant speed improvements via JIT compilation (LLVM/CUDA).

Usage:
    python render_knob.py --frames 20 --style sci --output 64 --tile v
    python render_knob.py -f 128 -s classic -o 48 -t h

Author: Generated for guiutilities modernization
"""

import argparse
import math
import numpy as np
from pathlib import Path

try:
    import mitsuba as mi
except ImportError:
    print("Error: Mitsuba 3 not installed. Install with: pip install mitsuba")
    print("Documentation: https://mitsuba.readthedocs.io/")
    exit(1)

try:
    from PIL import Image
except ImportError:
    Image = None
    print("Note: Install Pillow for resizing: pip install pillow")

# Try to use LLVM backend for CPU JIT compilation (fastest)
# Falls back to scalar if LLVM not available
try:
    mi.set_variant('llvm_ad_rgb')
except Exception:
    try:
        mi.set_variant('scalar_rgb')
    except Exception:
        print("Error: No suitable Mitsuba variant available")
        exit(1)


class KnobStyle:
    """Base class for knob style definitions."""

    def __init__(self):
        self.start_angle = -135  # degrees
        self.end_angle = 135    # degrees
        self.view_size = 2.6    # orthographic view size

    def get_angle_for_frame(self, frame: int, total_frames: int) -> float:
        """Calculate rotation angle for a given frame."""
        t = frame / max(total_frames - 1, 1)
        return self.start_angle + t * (self.end_angle - self.start_angle)

    def build_scene_dict(self, angle: float, render_size: int) -> dict:
        """Build Mitsuba scene dictionary. Override in subclasses."""
        raise NotImplementedError


class ClassicKnob(KnobStyle):
    """Classic pointer-style knob with tick marks."""

    def __init__(self):
        super().__init__()
        self.num_ticks = 20
        self.knob_radius = 0.9
        self.pointer_color = [0.8, 0.1, 0.1]  # Red pointer

    def build_scene_dict(self, angle: float, render_size: int) -> dict:
        scene = {
            'type': 'scene',
            'integrator': {
                'type': 'path',
                'max_depth': 6
            },
            'sensor': self._build_camera(render_size),
            'light': self._build_lighting(),
            'background': self._build_background(),
        }

        # Add tick marks
        for i in range(self.num_ticks):
            tick_angle = self.start_angle + i * (self.end_angle - self.start_angle) / (self.num_ticks - 1)
            scene[f'tick_{i}'] = self._build_tick(tick_angle)

        # Add knob body
        scene['outer_knob'] = self._build_outer_knob()
        scene['inner_knob'] = self._build_inner_knob()

        # Add rotating pointer
        scene['pointer'] = self._build_pointer(angle)
        scene['pointer_center'] = self._build_pointer_center()

        return scene

    def _build_camera(self, render_size: int) -> dict:
        return {
            'type': 'orthographic',
            'to_world': mi.ScalarTransform4f.look_at(
                origin=[0, 0, 2],
                target=[0, 0, 0],
                up=[0, 1, 0]
            ),
            'film': {
                'type': 'hdrfilm',
                'width': render_size,
                'height': render_size,
                'pixel_format': 'rgba',
                'component_format': 'float32',
                'rfilter': {'type': 'gaussian'}
            },
            'sampler': {
                'type': 'multijitter',
                'sample_count': 64
            }
        }

    def _build_lighting(self) -> dict:
        """Rectangle area light for studio-style lighting."""
        return {
            'type': 'rectangle',
            'to_world': mi.ScalarTransform4f.translate([2, 2, 5]) @
                       mi.ScalarTransform4f.scale([3, 3, 1]),
            'emitter': {
                'type': 'area',
                'radiance': {'type': 'rgb', 'value': [15, 15, 15]}
            }
        }

    def _build_area_light(self) -> dict:
        """Alternative: rectangle area light for studio-style lighting."""
        return {
            'type': 'rectangle',
            'to_world': mi.ScalarTransform4f.translate([2, 2, 5]) @
                       mi.ScalarTransform4f.scale([3, 3, 1]),
            'emitter': {
                'type': 'area',
                'radiance': {'type': 'rgb', 'value': [15, 15, 15]}
            }
        }

    def _build_background(self) -> dict:
        return {
            'type': 'rectangle',
            'to_world': mi.ScalarTransform4f.translate([0, 0, -0.1]) @
                       mi.ScalarTransform4f.scale([self.view_size, self.view_size, 1]),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {'type': 'rgb', 'value': [0.95, 0.95, 0.95]}
            }
        }

    def _build_tick(self, tick_angle: float) -> dict:
        rad = math.radians(tick_angle)
        inner_r = 1.0
        outer_r = 1.15
        x1 = inner_r * math.sin(rad)
        y1 = inner_r * math.cos(rad)
        x2 = outer_r * math.sin(rad)
        y2 = outer_r * math.cos(rad)

        return {
            'type': 'cylinder',
            'p0': [x1, y1, 0],
            'p1': [x2, y2, 0],
            'radius': 0.02,
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {'type': 'rgb', 'value': [0.9, 0.9, 0.9]}
            }
        }

    def _build_outer_knob(self) -> dict:
        return {
            'type': 'cylinder',
            'p0': [0, 0, 0],
            'p1': [0, 0, 0.3],
            'radius': self.knob_radius,
            'bsdf': {
                'type': 'plastic',
                'diffuse_reflectance': {'type': 'rgb', 'value': [0.15, 0.15, 0.15]},
                'int_ior': 1.5,
                'nonlinear': True
            }
        }

    def _build_inner_knob(self) -> dict:
        return {
            'type': 'disk',
            'to_world': mi.ScalarTransform4f.translate([0, 0, 0.31]) @
                       mi.ScalarTransform4f.scale([self.knob_radius * 0.95, self.knob_radius * 0.95, 1]),
            'bsdf': {
                'type': 'roughconductor',
                'distribution': 'ggx',
                'alpha': 0.15,
                'material': 'none',
                'eta': {'type': 'rgb', 'value': [0.2, 0.2, 0.2]},
                'k': {'type': 'rgb', 'value': [3.0, 3.0, 3.0]}
            }
        }

    def _build_pointer(self, angle: float) -> dict:
        rad = math.radians(angle)
        length = 0.7
        x = length * math.sin(rad)
        y = length * math.cos(rad)

        return {
            'type': 'cylinder',
            'p0': [0, 0, 0.32],
            'p1': [x, y, 0.32],
            'radius': 0.04,
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {'type': 'rgb', 'value': self.pointer_color}
            }
        }

    def _build_pointer_center(self) -> dict:
        return {
            'type': 'disk',
            'to_world': mi.ScalarTransform4f.translate([0, 0, 0.33]) @
                       mi.ScalarTransform4f.scale([0.08, 0.08, 1]),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {'type': 'rgb', 'value': [0.05, 0.05, 0.05]}
            }
        }


class SciKnob(KnobStyle):
    """Sequential Circuits style knob with chrome ring and grooves."""

    def __init__(self):
        super().__init__()
        self.start_angle = -150
        self.end_angle = 150
        self.view_size = 3.0
        self.num_grooves = 30
        self.num_steps = 11

    def build_scene_dict(self, angle: float, render_size: int) -> dict:
        scene = {
            'type': 'scene',
            'integrator': {
                'type': 'path',
                'max_depth': 8
            },
            'sensor': self._build_camera(render_size),
            'area_light': self._build_area_light(),
            'fill_light': self._build_fill_light(),
            'background': self._build_background(),
        }

        # Add tick marks
        for i in range(self.num_steps):
            tick_angle = self.start_angle + i * (self.end_angle - self.start_angle) / (self.num_steps - 1)
            scene[f'tick_{i}'] = self._build_tick(tick_angle)

        # Add grooves around outer edge
        for i in range(self.num_grooves):
            groove_angle = i * 360 / self.num_grooves
            scene[f'groove_{i}'] = self._build_groove(groove_angle)

        # Add knob components
        scene['outer_knob'] = self._build_outer_knob()
        scene['chrome_ring'] = self._build_chrome_ring()
        scene['inner_knob'] = self._build_inner_knob()

        # Add rotating pointer
        scene['pointer'] = self._build_pointer(angle)
        scene['pointer_center'] = self._build_pointer_center()

        return scene

    def _build_camera(self, render_size: int) -> dict:
        return {
            'type': 'orthographic',
            'to_world': mi.ScalarTransform4f.look_at(
                origin=[0, 0, 2],
                target=[0, 0, 0],
                up=[0, 1, 0]
            ),
            'film': {
                'type': 'hdrfilm',
                'width': render_size,
                'height': render_size,
                'pixel_format': 'rgba',
                'component_format': 'float32',
                'rfilter': {'type': 'gaussian'}
            },
            'sampler': {
                'type': 'multijitter',
                'sample_count': 128
            }
        }

    def _build_area_light(self) -> dict:
        return {
            'type': 'rectangle',
            'to_world': mi.ScalarTransform4f.translate([-3, 3, 8]) @
                       mi.ScalarTransform4f.rotate([1, 0, 0], 30) @
                       mi.ScalarTransform4f.scale([4, 4, 1]),
            'emitter': {
                'type': 'area',
                'radiance': {'type': 'rgb', 'value': [20, 20, 20]}
            }
        }

    def _build_fill_light(self) -> dict:
        return {
            'type': 'rectangle',
            'to_world': mi.ScalarTransform4f.translate([2, 2, 5]) @
                       mi.ScalarTransform4f.scale([2, 2, 1]),
            'emitter': {
                'type': 'area',
                'radiance': {'type': 'rgb', 'value': [8, 8, 8]}
            }
        }

    def _build_background(self) -> dict:
        return {
            'type': 'rectangle',
            'to_world': mi.ScalarTransform4f.translate([0, 0, -0.05]) @
                       mi.ScalarTransform4f.scale([self.view_size, self.view_size, 1]),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {'type': 'rgb', 'value': [0.98, 0.98, 0.98]}
            }
        }

    def _build_tick(self, tick_angle: float) -> dict:
        rad = math.radians(tick_angle)
        inner_r = 1.0
        outer_r = 1.16
        x1 = inner_r * math.sin(rad)
        y1 = inner_r * math.cos(rad)
        x2 = outer_r * math.sin(rad)
        y2 = outer_r * math.cos(rad)

        return {
            'type': 'cylinder',
            'p0': [x1, y1, 0],
            'p1': [x2, y2, 0],
            'radius': 0.015,
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {'type': 'rgb', 'value': [0.95, 0.95, 0.95]}
            }
        }

    def _build_groove(self, groove_angle: float) -> dict:
        rad = math.radians(groove_angle)
        r = 0.87
        x = r * math.sin(rad)
        y = r * math.cos(rad)

        return {
            'type': 'cylinder',
            'p0': [x, y, 0.01],
            'p1': [x, y, 0.35],
            'radius': 0.055,
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {'type': 'rgb', 'value': [0.02, 0.02, 0.02]}
            }
        }

    def _build_outer_knob(self) -> dict:
        return {
            'type': 'cylinder',
            'p0': [0, 0, 0],
            'p1': [0, 0, 0.35],
            'radius': 0.9,
            'bsdf': {
                'type': 'plastic',
                'diffuse_reflectance': {'type': 'rgb', 'value': [0.03, 0.03, 0.03]},
                'int_ior': 1.5,
                'nonlinear': True
            }
        }

    def _build_chrome_ring(self) -> dict:
        return {
            'type': 'cylinder',
            'p0': [0, 0, 0.35],
            'p1': [0, 0, 0.45],
            'radius': 0.81,
            'bsdf': {
                'type': 'conductor',
                'material': 'Cr'  # Chromium
            }
        }

    def _build_inner_knob(self) -> dict:
        return {
            'type': 'cylinder',
            'p0': [0, 0, 0.35],
            'p1': [0, 0, 0.5],
            'radius': 0.73,
            'bsdf': {
                'type': 'plastic',
                'diffuse_reflectance': {'type': 'rgb', 'value': [0.25, 0.25, 0.25]},
                'int_ior': 1.4
            }
        }

    def _build_pointer(self, angle: float) -> dict:
        rad = math.radians(angle)
        length = 0.65
        x = length * math.sin(rad)
        y = length * math.cos(rad)

        return {
            'type': 'cylinder',
            'p0': [0, 0, 0.51],
            'p1': [x, y, 0.51],
            'radius': 0.05,
            'bsdf': {
                'type': 'conductor',
                'material': 'Ag'  # Silver
            }
        }

    def _build_pointer_center(self) -> dict:
        return {
            'type': 'disk',
            'to_world': mi.ScalarTransform4f.translate([0, 0, 0.52]) @
                       mi.ScalarTransform4f.scale([0.06, 0.06, 1]),
            'bsdf': {
                'type': 'conductor',
                'material': 'Ag'
            }
        }


class ModernKnob(KnobStyle):
    """Modern minimalist knob with brushed metal finish."""

    def __init__(self):
        super().__init__()
        self.start_angle = -145
        self.end_angle = 145
        self.view_size = 2.4
        self.knob_radius = 0.85

    def build_scene_dict(self, angle: float, render_size: int) -> dict:
        scene = {
            'type': 'scene',
            'integrator': {
                'type': 'path',
                'max_depth': 8
            },
            'sensor': self._build_camera(render_size),
            'envmap': self._build_environment(),
            'background': self._build_background(),
            'knob_body': self._build_knob_body(),
            'knob_top': self._build_knob_top(),
            'indicator': self._build_indicator(angle),
        }
        return scene

    def _build_camera(self, render_size: int) -> dict:
        return {
            'type': 'orthographic',
            'to_world': mi.ScalarTransform4f.look_at(
                origin=[0, 0, 2],
                target=[0, 0, 0],
                up=[0, 1, 0]
            ),
            'film': {
                'type': 'hdrfilm',
                'width': render_size,
                'height': render_size,
                'pixel_format': 'rgba',
                'component_format': 'float32',
                'rfilter': {'type': 'gaussian'}
            },
            'sampler': {
                'type': 'multijitter',
                'sample_count': 128
            }
        }

    def _build_environment(self) -> dict:
        return {
            'type': 'constant',
            'radiance': {'type': 'rgb', 'value': [0.8, 0.8, 0.8]}
        }

    def _build_background(self) -> dict:
        return {
            'type': 'rectangle',
            'to_world': mi.ScalarTransform4f.translate([0, 0, -0.05]) @
                       mi.ScalarTransform4f.scale([self.view_size, self.view_size, 1]),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {'type': 'rgb', 'value': [0.12, 0.12, 0.12]}
            }
        }

    def _build_knob_body(self) -> dict:
        return {
            'type': 'cylinder',
            'p0': [0, 0, 0],
            'p1': [0, 0, 0.3],
            'radius': self.knob_radius,
            'bsdf': {
                'type': 'roughconductor',
                'distribution': 'ggx',
                'alpha_u': 0.05,
                'alpha_v': 0.3,  # Anisotropic for brushed effect
                'material': 'Al'  # Aluminum
            }
        }

    def _build_knob_top(self) -> dict:
        return {
            'type': 'disk',
            'to_world': mi.ScalarTransform4f.translate([0, 0, 0.3]) @
                       mi.ScalarTransform4f.scale([self.knob_radius, self.knob_radius, 1]),
            'bsdf': {
                'type': 'roughconductor',
                'distribution': 'ggx',
                'alpha': 0.08,
                'material': 'Al'
            }
        }

    def _build_indicator(self, angle: float) -> dict:
        rad = math.radians(angle)
        # Small dot indicator
        r = 0.6
        x = r * math.sin(rad)
        y = r * math.cos(rad)

        return {
            'type': 'disk',
            'to_world': mi.ScalarTransform4f.translate([x, y, 0.31]) @
                       mi.ScalarTransform4f.scale([0.08, 0.08, 1]),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {'type': 'rgb', 'value': [0.95, 0.3, 0.1]}  # Orange indicator
            }
        }


def get_style(name: str) -> KnobStyle:
    """Get a knob style by name."""
    styles = {
        'classic': ClassicKnob,
        'sci': SciKnob,
        'modern': ModernKnob,
    }
    if name not in styles:
        raise ValueError(f"Unknown style '{name}'. Available: {list(styles.keys())}")
    return styles[name]()


def render_frame(style: KnobStyle, frame: int, total_frames: int, render_size: int) -> np.ndarray:
    """Render a single frame of the knob."""
    angle = style.get_angle_for_frame(frame, total_frames)
    scene_dict = style.build_scene_dict(angle, render_size)

    scene = mi.load_dict(scene_dict)
    image = mi.render(scene)

    # Convert to numpy array (0-255 range)
    bitmap = mi.Bitmap(image)
    frame = np.array(bitmap)
    # Convert from float32 [0,1] to uint8 [0,255]
    return np.clip(frame * 255, 0, 255).astype(np.uint8)


def create_sprite_strip(frames: list, tile_direction: str) -> np.ndarray:
    """Combine frames into a sprite strip."""
    if tile_direction == 'v':
        return np.vstack(frames)
    else:
        return np.hstack(frames)


def save_image(image: np.ndarray, path: Path):
    """Save image to file."""
    bitmap = mi.Bitmap(image)
    bitmap.write(str(path))


def main():
    parser = argparse.ArgumentParser(
        description='Render knob graphics for VST plugins using Mitsuba 3',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --frames 20 --style sci --output 64
  %(prog)s -f 128 -s modern -o 48 -t h
  %(prog)s --style classic --frames 64 --render 512 --output 128

Available styles:
  classic  - Traditional pointer knob with tick marks
  sci      - Sequential Circuits style with chrome ring
  modern   - Minimalist brushed metal with dot indicator
        """
    )

    parser.add_argument('-f', '--frames', type=int, default=20,
                       help='Number of rotation frames (default: 20)')
    parser.add_argument('-s', '--style', default='classic',
                       choices=['classic', 'sci', 'modern'],
                       help='Knob style (default: classic)')
    parser.add_argument('-r', '--render', type=int, default=256,
                       help='Render resolution in pixels (default: 256)')
    parser.add_argument('-o', '--output', type=int, default=48,
                       help='Output frame size in pixels (default: 48)')
    parser.add_argument('-t', '--tile', default='v', choices=['v', 'h'],
                       help='Tile direction: v=vertical, h=horizontal (default: v)')
    parser.add_argument('--name', default=None,
                       help='Output filename (default: knob-{style})')
    parser.add_argument('--no-resize', action='store_true',
                       help='Skip resizing, output at render resolution')

    args = parser.parse_args()

    # Setup
    output_name = args.name or f'knob-{args.style}'
    output_dir = Path('.')

    print(f"Mitsuba 3 Knob Renderer")
    print(f"=" * 40)
    print(f"Style:       {args.style}")
    print(f"Frames:      {args.frames}")
    print(f"Render size: {args.render}x{args.render}")
    print(f"Output size: {args.output}x{args.output}")
    print(f"Tile:        {'vertical' if args.tile == 'v' else 'horizontal'}")
    print(f"Variant:     {mi.variant()}")
    print()

    # Get knob style
    style = get_style(args.style)

    # Render all frames
    print(f"Rendering {args.frames} frames...")
    frames = []
    for i in range(args.frames):
        print(f"  Frame {i+1}/{args.frames}", end='\r')
        frame = render_frame(style, i, args.frames, args.render)
        frames.append(frame)
    print(f"  Completed {args.frames} frames    ")

    # Create sprite strip
    print("Creating sprite strip...")
    strip = create_sprite_strip(frames, args.tile)

    # Save full resolution
    full_path = output_dir / f'{output_name}-{args.render}x{args.render}.png'
    save_image(strip, full_path)
    print(f"Saved: {full_path}")

    # Resize if requested
    if not args.no_resize and args.output != args.render:
        print("Resizing...")
        if args.tile == 'v':
            new_height = args.output * args.frames
            new_width = args.output
        else:
            new_height = args.output
            new_width = args.output * args.frames

        resized_path = output_dir / f'{output_name}-{args.output}x{args.output}.png'

        if Image is not None:
            # Use Pillow for high-quality resizing
            img = Image.fromarray(strip)
            resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            resized.save(str(resized_path))
        else:
            print("Warning: Pillow not installed, skipping resize")

        print(f"Saved: {resized_path}")

    print("\nDone!")


if __name__ == '__main__':
    main()
