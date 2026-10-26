"""
Spinner Library - Create animated loading spinners

Multiple styles of spinners you can use in your projects.
"""

import sys
import time
from dataclasses import dataclass


@dataclass
class Spinner:
    """Simple spinner class."""

    frames: list[str]
    delay: float = 0.1
    text: str = "Loading..."

    def __call__(self, duration: float = 3.0) -> None:
        """Animate spinner for specified duration."""
        start_time = time.time()
        frame_idx = 0

        while time.time() - start_time < duration:
            frame = self.frames[frame_idx % len(self.frames)]
            sys.stdout.write(f"\r{frame} {self.text}")
            sys.stdout.flush()
            time.sleep(self.delay)
            frame_idx += 1

        sys.stdout.write("\r✓ Done!\n")
        sys.stdout.flush()

    def animate(self, duration: float = 3.0, callback=None) -> None:
        """Animate with optional callback."""
        start_time = time.time()
        frame_idx = 0

        while time.time() - start_time < duration:
            frame = self.frames[frame_idx % len(self.frames)]
            if callback:
                callback(frame, self.text)
            time.sleep(self.delay)
            frame_idx += 1


# SPINNER PRESETS

# 1. Classic pulsing circle (blue inner to outer circle)
PULSE_CIRCLE = Spinner(
    frames=["◔", "◑", "◕", "●", "◕", "◑"], delay=0.1, text="Processing..."
)

# 2. Rotating circle with quarter fills
ROTATING_CIRCLE = Spinner(frames=["◐", "◓", "◑", "◒"], delay=0.1, text="Loading...")

# 3. Braille dots (smooth animated dots)
BRAILLE_DOTS = Spinner(
    frames=["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
    delay=0.08,
    text="Loading...",
)

# 4. Bar spinner
BAR_SPINNER = Spinner(
    frames=["▏", "▎", "▍", "▌", "▋", "▊", "▉", "▊", "▋", "▌", "▍", "▎"],
    delay=0.1,
    text="Running...",
)

# 5. Growing circle
GROWING_CIRCLE = Spinner(
    frames=["◯", "◐", "◓", "◑", "◒", "●", "◒", "◑", "◓", "◐"],
    delay=0.15,
    text="Processing...",
)

# 6. Arrow spinner
ARROW_SPINNER = Spinner(
    frames=["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"], delay=0.1, text="Working..."
)

# 7. Dots growing and shrinking
EXPANDING_DOTS = Spinner(
    frames=[".", "..", "...", "....", ".....", "....", "...", "..", "."],
    delay=0.1,
    text="Thinking...",
)

# 8. Triangle spinner
TRIANGLE_SPINNER = Spinner(frames=["◢", "◣", "◤", "◥"], delay=0.1, text="Processing...")

# 9. Multiple dots at angles
DOTS_ANGLES = Spinner(frames=["⠁", "⠂", "⠄", "⠂"], delay=0.15, text="Loading...")

# 10. Block spinner
BLOCK_SPINNER = Spinner(frames=["▌", "█", "▄", "▀"], delay=0.1, text="Loading...")


class ColorSpinner(Spinner):
    """Spinner with color support."""

    def __init__(
        self,
        frames: list[str],
        delay: float = 0.1,
        text: str = "Loading...",
        color: str = "34",
    ):
        """
        Create a colored spinner.

        Args:
            frames: List of animation frames
            delay: Delay between frames in seconds
            text: Status text
            color: ANSI color code (34=blue, 31=red, 32=green, 33=yellow, etc.)
        """
        super().__init__(frames, delay, text)
        self.color = color

    def __call__(self, duration: float = 3.0) -> None:
        """Animate spinner with color for specified duration."""
        start_time = time.time()
        frame_idx = 0
        color_code = f"\033[{self.color}m"
        reset_code = "\033[0m"

        while time.time() - start_time < duration:
            frame = self.frames[frame_idx % len(self.frames)]
            sys.stdout.write(f"\r{color_code}{frame}{reset_code} {self.text}")
            sys.stdout.flush()
            time.sleep(self.delay)
            frame_idx += 1

        sys.stdout.write(f"\r{color_code}✓{reset_code} Done!\n")
        sys.stdout.flush()


# Colored variants
BLUE_PULSE = ColorSpinner(
    frames=["◔", "◑", "◕", "●", "◕", "◑"],
    delay=0.1,
    text="Processing...",
    color="34",  # Blue
)

RED_PULSE = ColorSpinner(
    frames=["◔", "◑", "◕", "●", "◕", "◑"],
    delay=0.1,
    text="Error processing...",
    color="31",  # Red
)

GREEN_PULSE = ColorSpinner(
    frames=["◔", "◑", "◕", "●", "◕", "◑"],
    delay=0.1,
    text="Success...",
    color="32",  # Green
)

YELLOW_PULSE = ColorSpinner(
    frames=["◔", "◑", "◕", "●", "◕", "◑"],
    delay=0.1,
    text="Warning...",
    color="33",  # Yellow
)


if __name__ == "__main__":
    import sys

    spinners = [
        ("Pulse Circle", PULSE_CIRCLE),
        ("Rotating Circle", ROTATING_CIRCLE),
        ("Braille Dots", BRAILLE_DOTS),
        ("Bar", BAR_SPINNER),
        ("Growing Circle", GROWING_CIRCLE),
        ("Arrow", ARROW_SPINNER),
        ("Expanding Dots", EXPANDING_DOTS),
        ("Triangle", TRIANGLE_SPINNER),
        ("Block", BLOCK_SPINNER),
        ("Blue Pulse", BLUE_PULSE),
        ("Red Pulse", RED_PULSE),
        ("Green Pulse", GREEN_PULSE),
    ]

    print("\n" + "=" * 60)
    print("SPINNER EXAMPLES")
    print("=" * 60 + "\n")

    for name, spinner in spinners:
        print(f"{name}:")
        spinner(duration=2.0)
        print()

    print("=" * 60 + "\n")
