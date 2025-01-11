from flask import Flask, render_template, request, jsonify
import os
from milling import generate_milling_gcode
from drilling import generate_drilling_gcode
from cutting import generate_cutting_gcode
import config

app = Flask(__name__)

# Ensure the upload folder exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

# Validate G-code
def validate_cutting_gcode(gcode):
    for line in gcode.splitlines():
        if line.startswith("G1") or line.startswith("G0"):
            parts = line.split()
            for part in parts:
                if part.startswith("X"):
                    x_value = float(part[1:])
                    if x_value < 0 or x_value > config.BOARD_WIDTH:
                        return f"Error: X-coordinate {x_value} out of bounds."
                if part.startswith("Y"):
                    y_value = float(part[1:])
                    if y_value < 0 or y_value > config.BOARD_HEIGHT:
                        return f"Error: Y-coordinate {y_value} out of bounds."
                if part.startswith("Z"):
                    z_value = float(part[1:])
                    if z_value not in [config.SAFE_HEIGHT, config.CUTTING_DEPTH]:
                        return f"Error: Z-coordinate {z_value} invalid."

    return "Valid"
# Generate G-code with spindle control
def generate_gcode_with_spindle(x, y, z, cutting_depth, spindle_speed):
    gcode = []
    gcode.append(f"M3 S{spindle_speed}")  # Start spindle at specified speed
    gcode.append(f"G1 X{x} Y{y} Z{z}")   # Move tool to specified coordinates
    if z < cutting_depth:
        gcode.append(f"G1 Z{cutting_depth}")  # Cut to desired depth
    gcode.append("M5")  # Stop the spindle
    return "\n".join(gcode)

@app.route('/generate_gcode', methods=['POST'])
def generate_gcode():
    try:
        operation = request.form.get('operation')
        file = request.files.get('file')

        if not file or not operation:
            return jsonify({"error": "Invalid input parameters."}), 400

        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        if operation == 'cutting':
            gcode = generate_cutting_gcode(file_path)
        elif operation == 'milling':
            gcode = generate_milling_gcode(file_path)
        elif operation == 'drilling':
            gcode = generate_drilling_gcode(file_path)
        else:
            return jsonify({"error": "Unknown operation type."}), 400

        if "Error" in gcode:
            return jsonify({"error": gcode}), 400

        # Return the G-code directly
        return gcode, 200, {'Content-Type': 'text/plain'}

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
