"""
Quick Spinner Examples

Copy-paste these examples directly into your code!
"""

# ============================================================================
# EXAMPLE 1: Basic Blue Pulsing Circle (Recommended!)
# ============================================================================

from spinner import BLUE_PULSE

def example_basic():
    """The most popular spinner - blue circle that pulses."""
    print("Processing...")
    BLUE_PULSE(duration=3.0)
    print("Done!")


# ============================================================================
# EXAMPLE 2: Custom Spinner with Your Own Frames
# ============================================================================

from spinner import Spinner

def example_custom():
    """Create your own spinner."""
    my_spinner = Spinner(
        frames=["◐", "◓", "◑", "◒"],
        delay=0.1,
        text="Loading..."
    )
    my_spinner(duration=3.0)


# ============================================================================
# EXAMPLE 3: Colored Spinners for Status
# ============================================================================

from spinner import BLUE_PULSE, GREEN_PULSE, RED_PULSE, YELLOW_PULSE

def example_status():
    """Different colors for different statuses."""
    print("\n1. Processing (Blue):")
    BLUE_PULSE(duration=2.0)

    print("\n2. Success (Green):")
    GREEN_PULSE(duration=2.0)

    print("\n3. Warning (Yellow):")
    YELLOW_PULSE(duration=2.0)

    print("\n4. Error (Red):")
    RED_PULSE(duration=2.0)


# ============================================================================
# EXAMPLE 4: Use in a Loop
# ============================================================================

def example_loop():
    """Animate during a long operation."""
    from spinner import BRAILLE_DOTS
    
    for i in range(5):
        print(f"\nBatch {i+1}/5:")
        BRAILLE_DOTS(duration=2.0)


# ============================================================================
# EXAMPLE 5: Different Spinner Styles
# ============================================================================

def example_all_styles():
    """Try all the different spinners."""
    from spinner import (
        PULSE_CIRCLE,
        ROTATING_CIRCLE,
        BRAILLE_DOTS,
        BAR_SPINNER,
        GROWING_CIRCLE,
        ARROW_SPINNER,
        TRIANGLE_SPINNER,
        BLOCK_SPINNER,
    )

    spinners = [
        ("Pulse Circle", PULSE_CIRCLE),
        ("Rotating Circle", ROTATING_CIRCLE),
        ("Braille Dots", BRAILLE_DOTS),
        ("Bar", BAR_SPINNER),
        ("Growing Circle", GROWING_CIRCLE),
        ("Arrow", ARROW_SPINNER),
        ("Triangle", TRIANGLE_SPINNER),
        ("Block", BLOCK_SPINNER),
    ]

    for name, spinner in spinners:
        print(f"{name}:")
        spinner(duration=1.5)
        print()


# ============================================================================
# EXAMPLE 6: Custom Color (Magenta)
# ============================================================================

from spinner import ColorSpinner

def example_custom_color():
    """Create a spinner in any ANSI color."""
    magenta_spinner = ColorSpinner(
        frames=["◔", "◑", "◕", "●", "◕", "◑"],
        delay=0.1,
        text="Custom color...",
        color="35"  # Magenta
    )
    magenta_spinner(duration=3.0)


# ============================================================================
# EXAMPLE 7: With Callback (Advanced)
# ============================================================================

def example_callback():
    """Get callback for each animation frame."""
    from spinner import Spinner
    
    def on_frame(frame, text):
        # Do something on each frame
        print(f"Frame: {frame}")
    
    spinner = Spinner(
        frames=["◐", "◓", "◑", "◒"],
        delay=0.2,
        text="Custom callback..."
    )
    spinner.animate(duration=2.0, callback=on_frame)


# ============================================================================
# EXAMPLE 8: Text Changing Spinner
# ============================================================================

def example_changing_text():
    """Spinner that changes text during animation."""
    from spinner import BLUE_PULSE
    
    texts = ["Fetching...", "Processing...", "Saving...", "Done!"]
    
    for text in texts:
        BLUE_PULSE(duration=1.0)


# ============================================================================
# EXAMPLE 9: Task Completion Sequence
# ============================================================================

def example_sequence():
    """Show progress through multiple tasks."""
    from spinner import BLUE_PULSE, GREEN_PULSE, YELLOW_PULSE
    
    tasks = [
        ("Checking files", BLUE_PULSE),
        ("Validating", BLUE_PULSE),
        ("Compiling", BLUE_PULSE),
        ("Success!", GREEN_PULSE),
    ]
    
    for task_name, spinner in tasks:
        print(f"\n{task_name}...")
        spinner(duration=1.5)


# ============================================================================
# EXAMPLE 10: Spinner with Try/Except
# ============================================================================

def example_error_handling():
    """Show different spinners based on success/failure."""
    from spinner import GREEN_PULSE, RED_PULSE
    
    try:
        print("Processing...")
        # Simulate work
        import random
        if random.random() > 0.5:
            raise ValueError("Something went wrong!")
        GREEN_PULSE(duration=2.0)
        print("Success!")
    except Exception as e:
        RED_PULSE(duration=2.0)
        print(f"Error: {e}")


# ============================================================================
# EXAMPLE 11: Spinner as Progress Indicator
# ============================================================================

def example_progress():
    """Use spinner to show work is happening during a loop."""
    from spinner import BRAILLE_DOTS
    
    total_items = 5
    for i in range(total_items):
        print(f"\nProcessing item {i+1}/{total_items}...")
        BRAILLE_DOTS(duration=1.0)
    print("\nAll done!")


# ============================================================================
# EXAMPLE 12: Spinner with Print Statements
# ============================================================================

def example_with_logging():
    """Mix spinner with logging/print statements."""
    from spinner import BLUE_PULSE
    
    steps = [
        "Initializing...",
        "Loading configuration...",
        "Connecting to database...",
        "Fetching data...",
        "Processing...",
        "Saving results...",
    ]
    
    for step in steps:
        print(f"\n{step}")
        BLUE_PULSE(duration=1.0)
    
    print("\nComplete!")


# ============================================================================
# QUICK REFERENCE
# ============================================================================

"""
FASTEST START:

    from spinner import BLUE_PULSE
    BLUE_PULSE(duration=3.0)

COMMON SPINNERS:
    BLUE_PULSE          - Blue pulsing circle (recommended!)
    GREEN_PULSE         - Green pulsing circle (success)
    RED_PULSE           - Red pulsing circle (error)
    YELLOW_PULSE        - Yellow pulsing circle (warning)
    BRAILLE_DOTS        - Smooth animated dots
    ROTATING_CIRCLE     - Rotating quarters
    ARROW_SPINNER       - Rotating arrows

PARAMETERS:
    duration=2.0        - How long to animate (seconds)
    delay=0.1           - Delay between frames (seconds)
    text="Loading..."   - Status message to display
    color="35"          - ANSI color code (31=red, 32=green, etc.)

ANSI COLORS:
    "30" = Black        "31" = Red          "32" = Green
    "33" = Yellow       "34" = Blue         "35" = Magenta
    "36" = Cyan         "37" = White

EXAMPLES:
    BLUE_PULSE(duration=2.0)
    GREEN_PULSE(duration=1.0)
    ColorSpinner(frames=["A","B"], color="35")(duration=2.0)
"""

if __name__ == "__main__":
    print("\n" + "="*60)
    print("SPINNER EXAMPLES")
    print("="*60)
    
    examples = [
        ("Basic", example_basic),
        ("Custom", example_custom),
        ("Status Colors", example_status),
        ("All Styles", example_all_styles),
        ("Custom Color", example_custom_color),
    ]
    
    for name, func in examples[:2]:  # Run first 2 to keep it short
        print(f"\n\n📍 {name}")
        print("-"*60)
        func()
    
    print("\n" + "="*60)
    print("See spinner.py for all 12 spinners and SPINNER_GUIDE.md for details!")
    print("="*60)
