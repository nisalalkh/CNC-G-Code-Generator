import cv2
import numpy as np
import config

def generate_drilling_gcode(file_path):
    """
    Generate G-code for drilling holes in the PCB design.
    """
    # Load the image in grayscale
    image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    
    # Preprocess the image: Adaptive thresholding to detect white shapes
    binary_image = cv2.adaptiveThreshold(
        image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # Morphological operations to clean up noise
    kernel = np.ones((3, 3), np.uint8)
    binary_image = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel)

    # Find contours
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Debug: Visualize contours
    #debug_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    #cv2.drawContours(debug_image, contours, -1, (0, 255, 0), 2)
    #cv2.imwrite("debug_drilling_contours.jpg", debug_image)
    
    # Filter contours and extract drilling positions
    drill_positions = []
    for contour in contours:
        # Calculate area to filter small artifacts
        area = cv2.contourArea(contour)
        if area >=  config.MIN_HOLE_AREA:
            # Calculate circularity to ensure the shape is circular
            perimeter = cv2.arcLength(contour, True)
            if perimeter > 0:
                circularity = 4 * np.pi * (area / (perimeter ** 2))
                if config.CIRCULARITY_THRESHOLD[0] <= circularity <= config.CIRCULARITY_THRESHOLD[1]:
                    moments = cv2.moments(contour)
                    if moments["m00"] != 0:
                        cx = int(moments["m10"] / moments["m00"])
                        cy = int(moments["m01"] / moments["m00"])
                        drill_positions.append((cx, cy))

    # Get image dimensions and calculate scaling factors
    IMAGE_HEIGHT, IMAGE_WIDTH = image.shape[:2]
    SCALE_X = config.BOARD_WIDTH / IMAGE_WIDTH
    SCALE_Y = config.BOARD_HEIGHT / IMAGE_HEIGHT

    # Convert pixel coordinates to real-world CNC coordinates
    drill_positions = [(x * SCALE_X, y * SCALE_Y) for x, y in drill_positions]

    # Generate G-code
    gcode = []

    # Set units and spindle speed
    gcode.append("G21 ; Set units to mm" if config.UNITS == "mm" else "G20 ; Set units to inches")
    gcode.append("G90 ; Use absolute coordinates")
    gcode.append(f"G0 Z{config.SAFE_HEIGHT} ; Lift tool to safe height")
    gcode.append(f"M3 S{config.SPINDEL_SPEED} ; Start spindle at {config.SPINDEL_SPEED} RPM")

    # Drill holes
    for x, y in drill_positions:
        gcode.append(f"G0 X{x:.2f} Y{y:.2f} ; Move to drill position")
        gcode.append(f"G1 Z{config.DRILL_DEPTH} F{config.FEED_RATE} ; Drill down")
        gcode.append(f"G0 Z{config.SAFE_HEIGHT} ; Lift tool to safe height")

    # End program
    gcode.append("M5 ; Stop spindle")
    gcode.append("M30 ; End of program")

    return "\n".join(gcode)
