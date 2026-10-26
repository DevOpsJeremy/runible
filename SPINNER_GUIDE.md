# Spinner Guide - Creating Animated Loading Spinners

## The Pulsing Circle Spinner (What You Saw)

The spinner with a blue circle that pulses (inner to outer circle) looks like this:

```
◔ → ◑ → ◕ → ● → ◕ → ◑ → ◔
```

This cycles through these Unicode characters that represent a circle filling and emptying.

## Quick Start

### Simple Usage

```python
from spinner import BLUE_PULSE

# Animate for 3 seconds
BLUE_PULSE(duration=3.0)
```

### Output
```
◔ Processing...
```

(animates to ◑, ◕, ●, etc.)

## All Available Spinners

### 1. Pulse Circle (Pulsing inner/outer)
```
Frames: ◔ → ◑ → ◕ → ● → ◕ → ◑
PULSE_CIRCLE = Spinner(
    frames=["◔", "◑", "◕", "●", "◕", "◑"],
    delay=0.1,
    text="Processing..."
)
```

### 2. Rotating Circle (Quarter fills)
```
Frames: ◐ → ◓ → ◑ → ◒
ROTATING_CIRCLE = Spinner(
    frames=["◐", "◓", "◑", "◒"],
    delay=0.1,
    text="Loading..."
)
```

### 3. Braille Dots (Smooth animated dots)
```
Frames: ⠋ → ⠙ → ⠹ → ⠸ → ⠼ → ⠴ → ⠦ → ⠧ → ⠇ → ⠏
BRAILLE_DOTS = Spinner(
    frames=["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
    delay=0.08
)
```

### 4. Bar Spinner (Growing/shrinking bar)
```
Frames: ▏ → ▎ → ▍ → ▌ → ▋ → ▊ → ▉
BAR_SPINNER = Spinner(
    frames=["▏", "▎", "▍", "▌", "▋", "▊", "▉", "▊", "▋", "▌", "▍", "▎"],
    delay=0.1
)
```

### 5. Growing Circle (Circle grows and shrinks)
```
Frames: ◯ → ◐ → ◓ → ◑ → ◒ → ●
GROWING_CIRCLE = Spinner(
    frames=["◯", "◐", "◓", "◑", "◒", "●", "◒", "◑", "◓", "◐"],
    delay=0.15
)
```

### 6. Arrow Spinner (Rotating arrows)
```
Frames: ← → ↖ → ↑ → ↗ → → → ↘ → ↓ → ↙
ARROW_SPINNER = Spinner(
    frames=["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"],
    delay=0.1
)
```

### 7. Triangle Spinner (Rotating triangles)
```
Frames: ◢ → ◣ → ◤ → ◥
TRIANGLE_SPINNER = Spinner(
    frames=["◢", "◣", "◤", "◥"],
    delay=0.1
)
```

### 8. Block Spinner (Block transformations)
```
Frames: ▌ → █ → ▄ → ▀
BLOCK_SPINNER = Spinner(
    frames=["▌", "█", "▄", "▀"],
    delay=0.1
)
```

## Colored Spinners

Use colored variants for status indication:

```python
from spinner import BLUE_PULSE, RED_PULSE, GREEN_PULSE, YELLOW_PULSE

BLUE_PULSE(duration=2.0)  # Blue circle
RED_PULSE(duration=2.0)  # Red circle (error)
GREEN_PULSE(duration=2.0)  # Green circle (success)
YELLOW_PULSE(duration=2.0)  # Yellow circle (warning)
```

## Create Custom Spinner

### Simple Spinner

```python
from spinner import Spinner

my_spinner = Spinner(frames=["▏", "▎", "▍", "▌"], delay=0.1, text="Custom loading...")

my_spinner(duration=3.0)
```

### With Color

```python
from spinner import ColorSpinner

my_colored_spinner = ColorSpinner(
    frames=["◔", "◑", "◕", "●"],
    delay=0.15,
    text="Processing...",
    color="35",  # Magenta
)

my_colored_spinner(duration=3.0)
```

## ANSI Color Codes

Use these numbers for the `color` parameter:

| Code | Color |
|------|-------|
| 30 | Black |
| 31 | Red |
| 32 | Green |
| 33 | Yellow |
| 34 | Blue |
| 35 | Magenta |
| 36 | Cyan |
| 37 | White |

## Animation Details

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `frames` | List[str] | Required | Animation frames |
| `delay` | float | 0.1 | Seconds between frames |
| `text` | str | "Loading..." | Status message |
| `color` | str | None | ANSI color code |
| `duration` | float | 3.0 | Total animation time |

### Methods

```python
spinner = Spinner(frames=["◔", "◑", "◕", "●"], delay=0.1)

# Simple animation
spinner(duration=2.0)


# With callback for custom handling
def my_callback(frame, text):
    print(f"[{frame}] {text}")


spinner.animate(duration=2.0, callback=my_callback)
```

## Unicode Characters for Spinners

### Circles and Fills
```
◔ ◑ ◕ ●     (Quarter fills - pulse effect)
◐ ◓ ◑ ◒     (Rotating quarters)
◯ ◎ ●       (Growing circles)
```

### Dots and Indicators
```
⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏  (Braille dots)
● ○ ◔ ◕     (Various sizes)
```

### Bars and Fills
```
▏ ▎ ▍ ▌ ▋ ▊ ▉  (Vertical bars)
▁ ▂ ▃ ▄ ▅ ▆ ▇ █  (Horizontal bars)
```

### Arrows
```
← ↖ ↑ ↗ → ↘ ↓ ↙  (Directional arrows)
```

### Blocks and Triangles
```
◢ ◣ ◤ ◥  (Triangles)
█ ▀ ▄    (Blocks)
```

## Practical Examples

### Loading Data
```python
from spinner import BLUE_PULSE
import time

print("Fetching data...")
BLUE_PULSE(duration=2.0)
print("Data loaded!")
```

### Long Running Task
```python
from spinner import BRAILLE_DOTS


def process_data():
    spinner = BRAILLE_DOTS
    for i in range(5):
        spinner.animate(duration=2.0)
        print(f"Processed batch {i + 1}")
```

### Status-Based Spinner
```python
from spinner import GREEN_PULSE, RED_PULSE, YELLOW_PULSE


def long_operation():
    try:
        print("Processing...")
        YELLOW_PULSE(duration=2.0)
        # Do work here
        GREEN_PULSE(duration=1.0)
        print("Success!")
    except Exception as e:
        RED_PULSE(duration=2.0)
        print(f"Error: {e}")
```

### With Context Manager
```python
from spinner import BLUE_PULSE
import time


class LoadingSpinner:
    def __enter__(self):
        self.spinner = BLUE_PULSE
        return self

    def __exit__(self, *args):
        pass


with LoadingSpinner():
    BLUE_PULSE(duration=3.0)
```

## Tips & Tricks

### Smooth Animation
- Use smaller `delay` values (0.05-0.08) for smoother animation
- Use larger `delay` values (0.15-0.2) for emphasized animation

### Responsive Spinners
```python
spinner = Spinner(frames=["◔", "◑", "◕", "●"], delay=0.1, text="Working...")
spinner(duration=3.0)  # 3 seconds
```

### Mix and Match
```python
from spinner import BLUE_PULSE, GREEN_PULSE, RED_PULSE

steps = [
    (BLUE_PULSE, 2, "Step 1..."),
    (GREEN_PULSE, 2, "Step 2..."),
    (RED_PULSE, 1, "Warning: Check step 2"),
]

for spinner, duration, message in steps:
    print(message)
    spinner(duration=duration)
```

## File: spinner.py

- **PULSE_CIRCLE** - Recommended! Pulsing inner-outer circle
- **BLUE_PULSE** - Same as above but blue (recommended!)
- **ROTATING_CIRCLE** - Rotating quarter-filled circles
- **BRAILLE_DOTS** - Smooth animated braille dots
- **BAR_SPINNER** - Growing/shrinking bar
- **GROWING_CIRCLE** - Circle expands and contracts
- **ARROW_SPINNER** - Rotating directional arrows
- **TRIANGLE_SPINNER** - Rotating triangles
- **BLOCK_SPINNER** - Block transformations
- **RED_PULSE**, **GREEN_PULSE**, **YELLOW_PULSE** - Colored variants

## Integration with DAG Visualization

You can use spinners while rendering DAGs:

```python
from spinner import BLUE_PULSE
from dag_viz_textualize import DAGApp, SimpleDAG, NodeStatus


def render_with_loading():
    print("Building pipeline...")
    BLUE_PULSE(duration=2.0)

    dag = SimpleDAG()
    # ... build your DAG ...

    app = DAGApp(dag, {})
    app.run()
```

---

**Status**: ✅ Ready to use!
**File**: `spinner.py`
**Presets**: 12 different spinners
**Colors**: Supports all ANSI colors
