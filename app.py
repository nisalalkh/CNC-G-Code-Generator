from flask import Flask, request, render_template, send_file
import os
from image_processor import process_file, generate_gcode

app = Flask(__name__)

# Directories for file storage
UPLOAD_FOLDER = './uploads'
PROCESSED_FOLDER = './processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")  # Load the main web page

@app.route("/process-image", methods=["POST"])
def process_image():
    # Get file and user inputs from the form
    file = request.files.get("file")
    feed_rate = request.form.get("feed_rate", 1000, type=int)  # Default feed rate: 1000
    
    if not file:
        return "No file uploaded!", 400

    # Save the uploaded file
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        # Process the file (image or PDF) and extract contours
        contours = process_file(filepath)

        # Generate G-code from contours
        gcode = generate_gcode(contours, feed_rate)
        gcode_path = os.path.join(PROCESSED_FOLDER, "output.gcode")
        with open(gcode_path, 'w') as gcode_file:
            for line in gcode:
                gcode_file.write(line + '\n')

        # Return the G-code file for download
        return send_file(gcode_path, as_attachment=True, download_name="output.gcode")

    except ValueError as e:
        return str(e), 400

if __name__ == "__main__":
    app.run(debug=True)