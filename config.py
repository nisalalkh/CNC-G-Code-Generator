# config.py
BOARD_WIDTH = 100  # Width of the board in mm
BOARD_HEIGHT = 100  # Height of the board in mm
UNITS = "mm"  # Units for the G-code (mm or inches)
FEED_RATE = 100  # Feed rate in mm/min
SPINDEL_SPEED = 1000
SPINDLE_SPEED = 1000  # Spindle speed in RPM
CUTTING_DEPTH = -0.5  # Depth for cutting (in mm)
MILLING_DEPTH = -0.05  # Depth for milling (in mm)
DRILLING_DEPTH = -1.0  # Depth for drilling (in mm)
SAFE_HEIGHT = 5.0  # Safe height for non-cutting movements
TOOL_CHANGE_COMMAND = "M6"  # Command for tool change
