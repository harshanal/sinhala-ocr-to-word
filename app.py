"""
app.py
========

A Flask application that:
1. Displays a UI with Tailwind CSS for PDF upload.
2. Converts Sinhala PDFs to Word documents using OCR.
3. Shows conversion progress through periodic polling.

Setup:
------
- Install dependencies (requirements.txt):
    pdf2image
    pytesseract
    python-docx
    pillow
    Flask

- Install Tesseract and ensure TESSERACT_PATH is correct.
- Install Poppler and ensure POPPLER_PATH is correct.
"""

import os
import threading
import time
import uuid
from flask import Flask, render_template_string, request, jsonify, send_file
from pdf2image import convert_from_path
from PIL import Image
from docx import Document
import pytesseract

# ----------------------------
# Configuration
# ----------------------------
# Paths to Tesseract and Poppler on your DigitalOcean Droplet (adjust accordingly)
#TESSERACT_PATH = r'/usr/bin/tesseract'  # Example Linux path
#POPPLER_PATH = r'/usr/bin'             # Example Linux path
# For Windows, for example:
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = r'C:\poppler\Library\bin'

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Flask app config
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'        # Folder to store uploaded PDFs
app.config['CONVERT_FOLDER'] = 'converts'      # Folder to store conversion outputs
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERT_FOLDER'], exist_ok=True)

# Global variable to hold progress
# In production, consider a database or cache (like Redis)
# keyed by a unique session or job ID.
conversion_progress = {}

# ----------------------------
# HTML Template (index)
# ----------------------------
# For simplicity, we render HTML from a Python string here.
# In production, place this in /templates/index.html 
# and use Flask's render_template('index.html')
INDEX_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Sinhala PDF to Word Converter</title>
  <!-- Tailwind CSS (CDN) -->
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 flex flex-col items-center p-6">
  <div class="w-full max-w-xl mt-10">
    <div class="bg-white rounded-lg shadow-md p-6">
      <h1 class="text-2xl font-bold mb-4">Sinhala PDF to Word Converter</h1>
      <p class="text-gray-700 mb-4">
        Convert Sinhala PDFs to Word documents using OCR. This process may take a few moments,
        and you can watch the progress below.
      </p>

      <!-- Upload Form -->
      <form id="uploadForm" class="mb-4">
        <input 
          type="file" 
          name="pdf_file" 
          accept="application/pdf" 
          class="block mb-4 border border-gray-300 rounded p-2 w-full"
          required
        />
        <button 
          type="submit" 
          class="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700">
          Start Conversion
        </button>
      </form>

      <!-- Progress Bar -->
      <div id="progressContainer" class="w-full bg-gray-200 h-4 rounded overflow-hidden mb-2" style="display: none;">
        <div id="progressBar" class="bg-green-500 h-4" style="width: 0%;"></div>
      </div>
      <p id="progressText" class="text-gray-800 text-sm mb-4" style="display: none;"></p>

      <!-- Download Link -->
      <a 
        id="downloadLink" 
        href="#" 
        class="text-blue-700 font-semibold" 
        style="display: none;"
        download>
        Download Word Document
      </a>
    </div>
  </div>

  <script>
    const uploadForm = document.getElementById('uploadForm');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const downloadLink = document.getElementById('downloadLink');
    let jobId = null;
    let intervalId = null;

    // Handle form submission (upload PDF)
    uploadForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(uploadForm);
      progressContainer.style.display = 'block';
      progressText.style.display = 'block';
      downloadLink.style.display = 'none';
      progressBar.style.width = '0%';
      progressText.textContent = 'Uploading PDF...';

      try {
        const response = await fetch('/upload', {
          method: 'POST',
          body: formData
        });
        const data = await response.json();
        if (data.success) {
          jobId = data.job_id;
          // Start polling progress
          intervalId = setInterval(checkProgress, 2000);
        } else {
          alert(data.message);
        }
      } catch (err) {
        alert('Error uploading file.');
      }
    });

    // Poll server for progress
    async function checkProgress() {
      try {
        const res = await fetch(`/progress/${jobId}`);
        const data = await res.json();
        if (!data.success) {
          clearInterval(intervalId);
          alert(data.message);
          return;
        }

        progressBar.style.width = data.percentage + '%';
        progressText.textContent = data.status;

        // Completed
        if (data.completed) {
          clearInterval(intervalId);
          progressText.textContent = "Conversion completed!";
          downloadLink.href = `/download/${jobId}`;
          downloadLink.style.display = 'inline-block';
        }
      } catch (err) {
        clearInterval(intervalId);
        alert('Error retrieving progress.');
      }
    }
  </script>
</body>
</html>
"""

# ----------------------------
# Routes
# ----------------------------
@app.route("/")
def index():
    """Serve the main page with the upload form."""
    return render_template_string(INDEX_HTML)

@app.route("/upload", methods=["POST"])
def upload():
    """Handle file upload and start OCR conversion in a background thread."""
    if "pdf_file" not in request.files:
        return jsonify({"success": False, "message": "No PDF file provided."})

    pdf_file = request.files["pdf_file"]
    if pdf_file.filename == "":
        return jsonify({"success": False, "message": "No selected file."})

    # Validate that it is indeed a PDF
    if not pdf_file.filename.lower().endswith(".pdf"):
        return jsonify({"success": False, "message": "File is not a PDF."})

    # Save uploaded PDF
    job_id = str(uuid.uuid4())  # Unique job ID
    pdf_filename = f"{job_id}.pdf"
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
    pdf_file.save(pdf_path)

    # Initialize progress
    conversion_progress[job_id] = {
        "current": 0,
        "total": 0,
        "completed": False,
        "status": "Starting...",
        "output_path": ""
    }

    # Start background thread for conversion
    thread = threading.Thread(target=convert_pdf_to_word, args=(job_id, pdf_path))
    thread.start()

    return jsonify({"success": True, "message": "File uploaded successfully.", "job_id": job_id})

@app.route("/progress/<job_id>", methods=["GET"])
def progress(job_id):
    """Return conversion progress for a given job_id."""
    if job_id not in conversion_progress:
        return jsonify({"success": False, "message": "Invalid job ID."})

    data = conversion_progress[job_id]
    # Avoid division by zero
    percentage = 0
    if data["total"] > 0:
        percentage = int((data["current"] / data["total"]) * 100)

    return jsonify({
        "success": True,
        "current": data["current"],
        "total": data["total"],
        "percentage": percentage,
        "completed": data["completed"],
        "status": data["status"]
    })

@app.route("/download/<job_id>", methods=["GET"])
def download(job_id):
    """Return the Word document for a given job_id."""
    if job_id not in conversion_progress:
        return "Invalid job ID", 400

    output_path = conversion_progress[job_id]["output_path"]
    if not output_path or not os.path.exists(output_path):
        return "File not found", 404

    return send_file(output_path, as_attachment=True)

# ----------------------------
# OCR Conversion Logic
# ----------------------------
def convert_pdf_to_word(job_id, pdf_path):
    """
    Converts the PDF to Word using OCR (Tesseract).
    Updates global conversion_progress dict for the given job_id.
    """
    try:
        # Step 1: Convert PDF to images
        conversion_progress[job_id]["status"] = "Converting PDF to images..."
        images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
        total_pages = len(images)
        conversion_progress[job_id]["total"] = total_pages

        # Step 2: OCR each page and build doc
        conversion_progress[job_id]["status"] = "Performing OCR..."
        doc = Document()
        for index, img in enumerate(images, start=1):
            # Update progress
            conversion_progress[job_id]["current"] = index
            conversion_progress[job_id]["status"] = f"Processing page {index} of {total_pages}"
            
            text = pytesseract.image_to_string(img, lang='sin')  # Use Sinhala
            doc.add_paragraph(text)
            doc.add_page_break()

        # Step 3: Save output Word doc
        output_filename = f"{job_id}.docx"
        output_path = os.path.join(app.config['CONVERT_FOLDER'], output_filename)
        doc.save(output_path)
        conversion_progress[job_id]["output_path"] = output_path

        # Clean up
        conversion_progress[job_id]["status"] = "Conversion done."
        conversion_progress[job_id]["completed"] = True

    except Exception as e:
        conversion_progress[job_id]["status"] = f"Error: {str(e)}"
        conversion_progress[job_id]["completed"] = True

    finally:
        # Optionally remove the original PDF to save space
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

# ----------------------------
# Run the App
# ----------------------------
if __name__ == "__main__":
    # You may want to run with gunicorn in production
    app.run(host="0.0.0.0", port=5000, debug=True)
