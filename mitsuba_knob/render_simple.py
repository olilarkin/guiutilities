#!/usr/bin/env python3
"""
Simple Knob Renderer - Minimal Mitsuba 3 Example
=================================================
A streamlined example showing how to render knob graphics.
This version is easier to understand and modify.

Usage:
    python render_simple.py
    python render_simple.py --frames 64 --size 128

Requirements:
    pip install mitsuba numpy pillow
"""

import argparse
import math
from pathlib import Path

try:
    import mitsuba as mi
    mi.set_variant('scalar_rgb')  # Simple CPU rendering
except ImportError:
    print("Install Mitsuba 3: pip install mitsuba")
    exit(1)

import numpy as np

try:
    from PIL import Image
except ImportError:
    Image = None
    print("Note: Install Pillow for resizing: pip install pillow")


def create_knob_scene(angle_deg: float, size: int = 256) -> dict:
    """
    Create a simple knob scene.

    Args:
        angle_deg: Rotation angle of the pointer in degrees
        size: Render resolution
    """
    angle_rad = math.radians(angle_deg)

    # Pointer endpoint
    pointer_len = 0.6
    px = pointer_len * math.sin(angle_rad)
    py = pointer_len * math.cos(angle_rad)

    scene = {
        'type': 'scene',

        # Path tracing integrator
        'integrator': {
            'type': 'path',
            'max_depth': 4
        },

        # Orthographic camera looking down at knob
        'sensor': {
            'type': 'orthographic',
            'to_world': mi.ScalarTransform4f.look_at(
                origin=[0, 0, 3],
                target=[0, 0, 0],
                up=[0, 1, 0]
            ),
            'film': {
                'type': 'hdrfilm',
                'width': size,
                'height': size,
                'pixel_format': 'rgba',
                'component_format': 'float32',
                'rfilter': {'type': 'tent'}
            },
            'sampler': {
                'type': 'independent',
                'sample_count': 32
            }
        },

        # Simple area light
        'light': {
            'type': 'rectangle',
            'to_world': mi.ScalarTransform4f.translate([1, 1, 4]) @
                       mi.ScalarTransform4f.scale([3, 3, 1]),
            'emitter': {
                'type': 'area',
                'radiance': {'type': 'rgb', 'value': [12, 12, 12]}
            }
        },

        # Ambient/fill light
        'ambient': {
            'type': 'constant',
            'radiance': {'type': 'rgb', 'value': [0.3, 0.3, 0.3]}
        },

        # Background plane
        'background': {
            'type': 'rectangle',
            'to_world': mi.ScalarTransform4f.translate([0, 0, -0.1]) @
                       mi.ScalarTransform4f.scale([2, 2, 1]),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {'type': 'rgb', 'value': [0.95, 0.95, 0.95]}
            }
        },

        # Knob body (dark cylinder)
        'knob_body': {
            'type': 'cylinder',
            'p0': [0, 0, 0],
            'p1': [0, 0, 0.25],
            'radius': 0.8,
            'bsdf': {
                'type': 'plastic',
                'diffuse_reflectance': {'type': 'rgb', 'value': [0.12, 0.12, 0.12]},
                'int_ior': 1.5
            }
        },

        # Knob top surface
        'knob_top': {
            'type': 'disk',
            'to_world': mi.ScalarTransform4f.translate([0, 0, 0.25]) @
                       mi.ScalarTransform4f.scale([0.8, 0.8, 1]),
            'bsdf': {
                'type': 'plastic',
                'diffuse_reflectance': {'type': 'rgb', 'value': [0.15, 0.15, 0.15]},
                'int_ior': 1.5
            }
        },

        # Pointer line
        'pointer': {
            'type': 'cylinder',
            'p0': [0, 0, 0.26],
            'p1': [px, py, 0.26],
            'radius': 0.04,
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {'type': 'rgb', 'value': [0.9, 0.9, 0.9]}
            }
        },

        # Pointer center dot
        'center': {
            'type': 'disk',
            'to_world': mi.ScalarTransform4f.translate([0, 0, 0.27]) @
                       mi.ScalarTransform4f.scale([0.06, 0.06, 1]),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {'type': 'rgb', 'value': [0.9, 0.9, 0.9]}
            }
        },
    }

    # Add tick marks
    num_ticks = 11
    start_angle = -135
    end_angle = 135
    for i in range(num_ticks):
        t = i / (num_ticks - 1)
        tick_angle = math.radians(start_angle + t * (end_angle - start_angle))
        inner_r = 0.85
        outer_r = 0.95
        x1 = inner_r * math.sin(tick_angle)
        y1 = inner_r * math.cos(tick_angle)
        x2 = outer_r * math.sin(tick_angle)
        y2 = outer_r * math.cos(tick_angle)

        scene[f'tick_{i}'] = {
            'type': 'cylinder',
            'p0': [x1, y1, 0.01],
            'p1': [x2, y2, 0.01],
            'radius': 0.015,
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {'type': 'rgb', 'value': [0.85, 0.85, 0.85]}
            }
        }

    return scene


def render_frames(num_frames: int, render_size: int, output_size: int,
                 start_angle: float = -135, end_angle: float = 135) -> list:
    """Render all frames of the knob animation."""
    frames = []

    for i in range(num_frames):
        # Calculate angle for this frame
        t = i / max(num_frames - 1, 1)
        angle = start_angle + t * (end_angle - start_angle)

        print(f"  Rendering frame {i+1}/{num_frames} (angle: {angle:.1f}°)", end='\r')

        # Create and render scene
        scene_dict = create_knob_scene(angle, render_size)
        scene = mi.load_dict(scene_dict)
        image = mi.render(scene)

        # Convert to numpy uint8 [0-255]
        bitmap = mi.Bitmap(image)
        frame = np.array(bitmap)
        # Convert from float32 [0,1] to uint8 [0,255]
        frame = np.clip(frame * 255, 0, 255).astype(np.uint8)
        frames.append(frame)

    print(f"  Rendered {num_frames} frames" + " " * 30)
    return frames


def create_sprite_strip(frames: list, vertical: bool = True) -> np.ndarray:
    """Stack frames into a sprite strip."""
    if vertical:
        return np.vstack(frames)
    return np.hstack(frames)


def resize_strip(strip: np.ndarray, output_size: int, num_frames: int,
                vertical: bool = True) -> np.ndarray:
    """Resize the sprite strip to target dimensions."""
    if Image is None:
        print("Warning: Pillow not installed, skipping resize")
        return strip

    img = Image.fromarray(strip)

    if vertical:
        new_size = (output_size, output_size * num_frames)
    else:
        new_size = (output_size * num_frames, output_size)

    resized = img.resize(new_size, Image.Resampling.LANCZOS)
    return np.array(resized)


def save_image(array: np.ndarray, path: str):
    """Save numpy array as PNG."""
    if Image is not None:
        img = Image.fromarray(array)
        img.save(path)
    else:
        # Fallback to Mitsuba
        bitmap = mi.Bitmap(array)
        bitmap.write(path)


def main():
    parser = argparse.ArgumentParser(description='Simple knob renderer')
    parser.add_argument('-f', '--frames', type=int, default=20,
                       help='Number of frames (default: 20)')
    parser.add_argument('-r', '--render-size', type=int, default=256,
                       help='Render resolution (default: 256)')
    parser.add_argument('-o', '--output-size', type=int, default=48,
                       help='Output frame size (default: 48)')
    parser.add_argument('-t', '--tile', choices=['v', 'h'], default='v',
                       help='Tile direction (default: v)')
    parser.add_argument('-n', '--name', default='knob',
                       help='Output filename prefix (default: knob)')

    args = parser.parse_args()
    vertical = args.tile == 'v'

    print("Simple Mitsuba Knob Renderer")
    print("=" * 40)
    print(f"Frames:      {args.frames}")
    print(f"Render size: {args.render_size}x{args.render_size}")
    print(f"Output size: {args.output_size}x{args.output_size}")
    print()

    # Render all frames
    print("Rendering...")
    frames = render_frames(args.frames, args.render_size, args.output_size)

    # Create sprite strip
    print("Creating sprite strip...")
    strip = create_sprite_strip(frames, vertical)

    # Save full resolution
    full_path = f'{args.name}-{args.render_size}px.png'
    save_image(strip, full_path)
    print(f"Saved: {full_path}")

    # Resize and save
    if args.output_size != args.render_size:
        print("Resizing...")
        resized = resize_strip(strip, args.output_size, args.frames, vertical)
        resized_path = f'{args.name}-{args.output_size}px.png'
        save_image(resized, resized_path)
        print(f"Saved: {resized_path}")

    print("\nDone!")


if __name__ == '__main__':
    main()
