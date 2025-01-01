import cv2
import numpy as np
from pdf2image import convert_from_path
from flask import Flask, render_template, request, jsonify
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

def process_file(file_path):
    """
    Processes an uploaded file (image or PDF) and extracts contours.
    Args:
        file_path (str): Path to the uploaded file.
    Returns:
        list: Contours extracted from the processed image.
    """
    ext = file_path.split('.')[-1].lower()

    # Convert PDF to image if needed
    if ext == "pdf":
        images = convert_from_path(file_path)
        if not images:
            raise ValueError("Error: Could not process the PDF!")
        pdf_image_path = file_path.replace(".pdf", "_temp.jpg")
        images[0].save(pdf_image_path, "JPEG")
        file_path = pdf_image_path

    # Load image in grayscale
    image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Error: Could not load the image!")

    # Noise reduction with Gaussian Blur
    blurred_image = cv2.GaussianBlur(image, (5, 5), 0)

    # Adaptive thresholding
    binary_image = cv2.adaptiveThreshold(
        blurred_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )

    # Morphological operations to close small gaps and clean noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    cleaned_image = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Edge detection
    edges = cv2.Canny(cleaned_image, 30, 100)

    # Find contours using tree method to capture all paths
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Filter small contours based on area
    min_contour_area = 10
    filtered_contours = [c for c in contours if cv2.contourArea(c) > min_contour_area]

    return filtered_contours




def generate_gcode(contours, feed_rate=1000, scale=0.1):
    """
    Generates G-code from contours.
    Args:
        contours (list): List of contours.
        feed_rate (int): Feed rate for the CNC machine.
        scale (float): Scale factor to convert pixels to real-world units.
    Returns:
        list: Generated G-code lines.
    """
    gcode = [
        "G21 ; Set units to millimeters",
        "G90 ; Absolute positioning",
        f"G0 F{feed_rate} ; Set feed rate"
    ]

    for contour in contours:
        if len(contour) == 0:
            continue
        gcode.append("G0 Z5 ; Raise tool to safe height")
        for i, point in enumerate(contour):
            x, y = point[0]
            x, y = round(x * scale, 2), round(y * scale, 2)
            if i == 0:
                gcode.append(f"G0 X{x} Y{y} ; Move to start of contour")
                gcode.append("G0 Z0 ; Lower tool for cutting")
            else:
                gcode.append(f"G1 X{x} Y{y} ; Cut to ({x}, {y})")
        gcode.append("G0 Z5 ; Raise tool after contour")

    gcode.append("M30 ; End of program")
    return gcode

def plot_contours(contours, output_path, scale=0.1):
    """
    Plots contours for visualization.
    Args:
        contours (list): List of contours.
        output_path (str): Path to save the plot.
        scale (float): Scale factor for real-world units.
    """
    plt.figure(figsize=(10, 10))
    for contour in contours:
        points = np.squeeze(contour, axis=1) * scale
        plt.plot(points[:, 0], points[:, 1], linewidth=1)
    plt.gca().invert_yaxis()
    plt.title("Tool Path Visualization")
    plt.xlabel("X-axis (mm)")
    plt.ylabel("Y-axis (mm)")
    plt.grid(True)
    plt.savefig(output_path)
    plt.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if not file:
        return jsonify({"error": "No file uploaded!"}), 400

    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    try:
        contours = process_file(file_path)
        gcode = generate_gcode(contours)

        # Save and plot the visualization
        output_path = os.path.join('static', 'toolpath.png')
        plot_contours(contours, output_path)

        return jsonify({
            "gcode": gcode,
            "visualization_url": "/static/toolpath.png"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    app.run(debug=True)
