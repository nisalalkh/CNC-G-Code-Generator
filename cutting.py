import cv2
import numpy as np
import config

def generate_cutting_gcode(file_path):
    """
    Generate G-code for cutting the border of the PCB design.
    Ensures the G-code complies with config.py parameters and includes spindle control.
    """
    # Example coordinates for cutting the border
    border_coords = [
        (0, 0),
        (0, config.BOARD_HEIGHT),
        (config.BOARD_WIDTH, config.BOARD_HEIGHT),
        (config.BOARD_WIDTH, 0),
        (0, 0)
    ]

    gcode = []

    # Set units
    if config.UNITS == "mm":
        gcode.append("G21 ; Set units to mm")
    else:
        gcode.append("G20 ; Set units to inches")

    # Use absolute positioning
    gcode.append("G90 ; Use absolute coordinates")

    # Lift to safe height
    gcode.append(f"G0 Z{config.SAFE_HEIGHT} ; Lift tool to safe height")

    # Start spindle (M3 for clockwise rotation)
    gcode.append(f"M3 S{config.SPINDEL_SPEED} ; Start spindle at {config.SPINDEL_SPEED} RPM")

    # Start cutting
    for i, (x, y) in enumerate(border_coords):
        if i == 0:
            # Move to the first point without cutting
            gcode.append(f"G0 X{x:.2f} Y{y:.2f}")
            gcode.append(f"G1 Z{config.CUTTING_DEPTH} F{config.FEED_RATE}")
        else:
            # Cutting to subsequent points
            gcode.append(f"G1 X{x:.2f} Y{y:.2f} F{config.FEED_RATE}")

    # Lift to safe height at the end
    gcode.append(f"G0 Z{config.SAFE_HEIGHT} ; Lift tool to safe height")

    # Stop spindle after cutting
    gcode.append("M5 ; Stop spindle")

    # End program
    gcode.append("M30 ; End of program")

    # Join the G-code lines into a single string
    return "\n".join(gcode)
