# Mitsuba Knob Renderer

Modern, Python-based knob rendering for VST plugin graphics using [Mitsuba 3](https://mitsuba.readthedocs.io/).

This replaces the legacy POV-Ray workflow with a faster, more flexible solution.

## Why Mitsuba?

| Feature | POV-Ray | Mitsuba 3 |
|---------|---------|-----------|
| Speed | Slow (pure CPU) | Fast (JIT via LLVM/CUDA) |
| Python API | None (shell commands) | Native Python |
| Materials | Fixed set | Physically-based, extensible |
| GPU Support | No | Yes (CUDA/OptiX) |
| Differentiable | No | Yes |

## Installation

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install mitsuba numpy pillow
```

## Quick Start

### Simple Version (recommended for getting started)

```bash
# Basic usage - renders 20 frames at 48x48
python render_simple.py

# Custom settings
python render_simple.py --frames 64 --output-size 128 --tile v
```

### Full Version (more styles and options)

```bash
# Classic pointer knob
python render_knob.py --style classic --frames 20 --output 64

# Sequential Circuits style (chrome ring, grooves)
python render_knob.py --style sci --frames 128 --output 48

# Modern minimalist (brushed metal)
python render_knob.py --style modern --frames 64 --output 96
```

## Output

The renderer creates a vertical (or horizontal) sprite strip PNG:

```
┌────────┐
│ frame0 │  <- angle: -135°
├────────┤
│ frame1 │  <- angle: -120°
├────────┤
│  ...   │
├────────┤
│ frameN │  <- angle: +135°
└────────┘
```

This format is directly usable by VST GUI frameworks (VSTGUI, IPlug2, JUCE, etc.)

## Command Line Options

### render_simple.py
| Option | Default | Description |
|--------|---------|-------------|
| `-f, --frames` | 20 | Number of rotation frames |
| `-r, --render-size` | 256 | Internal render resolution |
| `-o, --output-size` | 48 | Final frame size in pixels |
| `-t, --tile` | v | Tile direction: v=vertical, h=horizontal |
| `-n, --name` | knob | Output filename prefix |

### render_knob.py
| Option | Default | Description |
|--------|---------|-------------|
| `-f, --frames` | 20 | Number of rotation frames |
| `-s, --style` | classic | Knob style (classic, sci, modern) |
| `-r, --render` | 256 | Internal render resolution |
| `-o, --output` | 48 | Final frame size in pixels |
| `-t, --tile` | v | Tile direction |
| `--name` | auto | Output filename |
| `--no-resize` | - | Skip resizing step |

## Customizing Knobs

Edit `knob_config.py` to create custom styles:

```python
from knob_config import KnobConfig

my_knob = KnobConfig(
    start_angle=-150,
    end_angle=150,
    body_color=(0.2, 0.2, 0.8),  # Blue
    pointer_color=(1.0, 1.0, 1.0),
    body_material='metal',
    metal_type='Al',  # Aluminum
    roughness=0.1,
    pointer_style='dot',
    chrome_ring=True,
)
```

### Available Materials
- `plastic` - Diffuse plastic with subtle shine
- `metal` - Physically-based metal (Al, Ag, Au, Cu, Cr)
- `matte` - Pure diffuse (no reflections)

### Available Metal Types
| Code | Material |
|------|----------|
| Al | Aluminum |
| Ag | Silver |
| Au | Gold |
| Cu | Copper |
| Cr | Chromium |

## Performance Tips

1. **Use LLVM variant** for CPU rendering (default):
   ```python
   mi.set_variant('llvm_ad_rgb')
   ```

2. **Use CUDA variant** if you have an NVIDIA GPU:
   ```python
   mi.set_variant('cuda_ad_rgb')
   ```

3. **Lower samples** for previews:
   ```python
   'sample_count': 16  # preview
   'sample_count': 128  # final
   ```

4. **Batch render** at high resolution, resize once at the end

## Comparison with POV-Ray

### Old workflow (POV-Ray)
```bash
# Slow, 3-pass alpha compositing
python render.py -f 20 -s sci-knob -r 300 -o 48
# Time: ~60 seconds for 20 frames
```

### New workflow (Mitsuba)
```bash
# Fast, single pass with native alpha
python render_simple.py -f 20 -r 256 -o 48
# Time: ~5-10 seconds for 20 frames
```

## License

MIT - Use freely in your audio plugins.

## Links

- [Mitsuba 3 Documentation](https://mitsuba.readthedocs.io/)
- [Mitsuba 3 GitHub](https://github.com/mitsuba-renderer/mitsuba3)
- [BSDF Reference](https://mitsuba.readthedocs.io/en/latest/src/generated/plugins_bsdfs.html)
