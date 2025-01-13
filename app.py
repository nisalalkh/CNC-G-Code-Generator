from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from milling import generate_milling_gcode
from drilling import generate_drilling_gcode
from cutting import generate_cutting_gcode
import config

app = Flask(__name__)

# Directory to store the G-code files
GCODE_DIRECTORY = 'uploads'

# Make sure the directory exists
if not os.path.exists(GCODE_DIRECTORY):
    os.makedirs(GCODE_DIRECTORY)

# Ensure the upload folder exists
UPLOAD_FOLDER = 'uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')


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
