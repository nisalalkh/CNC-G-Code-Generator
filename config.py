# config.py
BOARD_WIDTH = 100  # Width of the board in mm
BOARD_HEIGHT = 100  # Height of the board in mm
UNITS = "mm"  # Units for the G-code (mm or inches)
FEED_RATE = 60  # Feed rate in mm/min
SPINDEL_SPEED = 1000  # Spindle speed in RPM
CUTTING_DEPTH = -0.5  # Depth for cutting (in mm)
MILLING_DEPTH = -0.05  # Depth for milling (in mm)
DRILL_DEPTH = -0.5  # Depth for drilling (in mm)
SAFE_HEIGHT = 5.0  # Safe height for non-cutting movements
TOOL_CHANGE_COMMAND = "M6"  # Command for tool change
MIN_HOLE_AREA = 10  # Example threshold for minimum hole area
CIRCULARITY_THRESHOLD = (0.2, 1.2)  # Accept nearly circular contours
TOOL_DIAMETER = 0.01