# Sinhala OCR to Word Conversion

This project provides a Python script to convert a **Sinhala-language PDF** into a Microsoft Word document by using [Tesseract OCR](https://github.com/UB-Mannheim/tesseract) and [Poppler](http://blog.alivate.com.au/poppler-windows/) for PDF-to-image conversion.

## Background

Converting PDF documents containing Sinhala text to editable formats using online converters often results in garbled text. This issue generally arises due to the complex character sets and encoding used in Sinhala scripts, which many conventional PDF to text tools do not handle correctly. This project addresses this problem by using Optical Character Recognition (OCR) to read Sinhala text from PDFs converted to images. While this method improves text recognition accuracy, the final converted output may still require manual editing to correct any OCR inaccuracies, especially with handwritten or poorly scanned documents.

## Table of Contents

1. [Features](#features)  
2. [Prerequisites](#prerequisites)  
3. [Installation](#installation)  
4. [Configuration](#configuration)  
5. [Usage](#usage)  
6. [How It Works](#how-it-works)  
7. [Troubleshooting](#troubleshooting)  
8. [License](#license)

---

## Features

- **Automatic PDF-to-Image Conversion**: Uses `pdf2image` with Poppler to convert PDF pages into images.  
- **OCR Extraction**: Uses `pytesseract` to extract Sinhala text from the images.  
- **Word Document Generation**: Outputs extracted text as a `.docx` file using `python-docx`.

---

## Prerequisites

1. **Python 3.7+**  
2. **Tesseract OCR** (Windows)  
   - [Tesseract OCR Windows installer](https://github.com/UB-Mannheim/tesseract/wiki)  
   - Make sure you have the Sinhala language pack (often included, or install `tesseract-ocr-sin`).  
   - Example path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
3. **Poppler** (Windows)  
   - Download and install Poppler for Windows (e.g., from [here](http://blog.alivate.com.au/poppler-windows/)).  
   - Example path: `C:\poppler\Library\bin`
4. **Git** (optional, if you want to clone the repository)  

---

## Installation

1. **Clone or Download the Repository** (GitLab):
   ```bash
   git clone https://gitlab.com/your-username/your-repo.git
   cd your-repo
   ```
   
2. **Create and Activate a Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
   *(On Windows Command Prompt, use `venv\Scripts\activate` instead of `source`.)*

3. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   Ensure your `requirements.txt` includes:
   ```
   pytesseract
   pdf2image
   pillow
   python-docx
   ```

---

## Configuration

In the script, you’ll find the following variables at the beginning:

```python
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPLER_PATH = r'C:\poppler\Library\bin'
PDF_PATH = r'c:\book\book.pdf'
OUTPUT_DOC_PATH = r'c:\book\output_word_document.docx'
```

- **TESSERACT_PATH**: Path to your `tesseract.exe`.  
- **POPLER_PATH**: Path to Poppler’s `bin` folder.  
- **PDF_PATH**: Full path to your input PDF file.  
- **OUTPUT_DOC_PATH**: Full path where you want the resulting Word document to be saved.

Update these paths as per your local configuration before running the script.

---

## Usage

1. **Update Paths**: Edit the file (e.g., `sinocr.py`) to ensure `TESSERACT_PATH`, `POPLER_PATH`, `PDF_PATH`, and `OUTPUT_DOC_PATH` match your local system.
2. **Run the Script**:
   ```bash
   python sinocr.py
   ```
3. **Output**:  
   - The script will convert the PDF pages to images (using Poppler).  
   - Tesseract OCR will extract Sinhala text from each page.  
   - A `.docx` file will be created at the location specified in `OUTPUT_DOC_PATH`.

---

## How It Works

1. **PDF to Images**: The [pdf2image](https://pypi.org/project/pdf2image/) library calls `pdftoppm` from Poppler to convert each page in the PDF to an image.
2. **OCR Extraction**: [pytesseract](https://pypi.org/project/pytesseract/) invokes Tesseract OCR on each image to read and extract Sinhala text.
3. **Word Document Creation**: [python-docx](https://pypi.org/project/python-docx/) constructs a `.docx` file, appending each page’s extracted text as a new paragraph, separated by page breaks.

---

## Troubleshooting

- **Poppler Not Found**: If you get `poppler not found` errors, ensure `POPLER_PATH` is correct or add it to your system `PATH` environment variable.
- **Tesseract Not Found**: Confirm `TESSERACT_PATH` is correct and that Tesseract is installed with the Sinhala language pack.
- **Language Issues**: For better accuracy, verify the `lang='sin'` parameter in `pytesseract.image_to_string(...)` is correct.  
- **High Memory Usage or Slow Performance**: For very large PDFs, consider processing pages in smaller batches or using higher CPU/memory resources.

---

## License

This project is open-source. Please refer to the [LICENSE](LICENSE) file in the repository for details on usage and distribution.