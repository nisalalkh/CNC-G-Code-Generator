import cv2
import numpy as np
import config

def generate_milling_gcode(file_path):
    """
    Generate G-code for milling operations on a PCB design.
    Adjust coordinates based on copper board dimensions.
    """
    # Read the image in grayscale
    original_image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)

    # Upscale the image for better detection
    image = cv2.resize(original_image, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

    # Adaptive thresholding for better binarization
    binary_image = cv2.adaptiveThreshold(
        image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )

    # Apply morphological operations to close gaps and clean noise
    kernel = np.ones((3, 3), np.uint8)
    binary_image = cv2.dilate(binary_image, kernel, iterations=1)
    binary_image = cv2.erode(binary_image, kernel, iterations=1)

    # Edge detection using Canny
    edges = cv2.Canny(binary_image, 30, 100)

    # Find contours with hierarchical retrieval
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Filter and approximate contours
    filtered_contours = []
    for contour in contours:
        if cv2.contourArea(contour) > 10:  # Filter small contours
            epsilon = 0.002 * cv2.arcLength(contour, True)  # Higher precision for contour approximation
            approx = cv2.approxPolyDP(contour, epsilon, True)
            filtered_contours.append(approx)

    # Debug: Save contours for visualization
    debug_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(debug_image, filtered_contours, -1, (0, 255, 0), 1)
    #debug_image_path = file_path.replace(".png", "_debug.jpg")
    #cv2.imwrite(debug_image_path, debug_image)

    # Scale factors to map image pixels to copper board dimensions
    img_height, img_width = binary_image.shape
    x_scale = config.BOARD_WIDTH / img_width
    y_scale = config.BOARD_HEIGHT / img_height

    # Initialize G-code
    gcode = []
    gcode.append("G21 ; Set units to mm" if config.UNITS == "mm" else "G20 ; Set units to inches")
    gcode.append("G90 ; Absolute positioning")
    gcode.append(f"G0 Z{config.SAFE_HEIGHT} ; Move to safe height")
    gcode.append(f"M3 S{config.SPINDEL_SPEED} ; Start spindle")

    # Generate G-code for each contour
    for contour in filtered_contours:
        # Start a new milling path
        first_point = contour[0][0]
        x_start = first_point[0] * x_scale
        y_start = first_point[1] * y_scale
        gcode.append(f"G0 X{x_start:.3f} Y{y_start:.3f} ; Rapid move to start")
        gcode.append(f"G1 Z{-config.MILLING_DEPTH:.3f} F{config.FEED_RATE} ; Lower tool to cutting depth")

        for point in contour:
            x, y = point[0]
            x_real = x * x_scale
            y_real = y * y_scale
            gcode.append(f"G1 X{x_real:.3f} Y{y_real:.3f} F{config.FEED_RATE} ; Milling move")

        # Return to safe height after finishing the contour
        gcode.append(f"G0 Z{config.SAFE_HEIGHT} ; Move to safe height")

    # Lift the tool after completing the contour
    gcode.append(f"G0 Z{config.SAFE_HEIGHT} ; Lift tool to safe height")

    # End program
    gcode.append("M5 ; Stop spindle")
    gcode.append("M30 ; End program")

    return "\n".join(gcode)

