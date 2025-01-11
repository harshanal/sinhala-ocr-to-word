import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from docx import Document
import os

# Paths
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPLER_PATH = r'C:\poppler\Library\bin'
PDF_PATH = r'c:\book\wadena.pdf'  # Replace with your PDF file path
OUTPUT_DOC_PATH = r'c:\book\output_word_document.docx'  # Replace with your desired output Word file path

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Function to convert PDF to images
def pdf_to_images(pdf_path, poppler_path):
    try:
        images = convert_from_path(pdf_path, poppler_path=poppler_path)
        print(f"Converted PDF to {len(images)} images.")
        return images
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return []

# Function to apply OCR on images
def images_to_text(images):
    text = []
    total_images = len(images)
    for index, image in enumerate(images):
        try:
            extracted_text = pytesseract.image_to_string(image, lang='sin')  # Specify the language
            text.append(extracted_text)
            print(f"Processed {index + 1}/{total_images} pages.")
        except Exception as e:
            print(f"Failed to perform OCR on page {index + 1}: {e}")
    return text

# Function to save text to a Word document
def save_text_to_word(texts, output_path):
    doc = Document()
    for page_text in texts:
        doc.add_paragraph(page_text)
        doc.add_page_break()
    doc.save(output_path)
    print(f"Saved text to Word document at {output_path}")

# Main function to convert PDF to Word
def convert_pdf_to_word(pdf_path, output_doc_path, poppler_path):
    images = pdf_to_images(pdf_path, poppler_path)
    if not images:
        print("No images to process for OCR.")
        return
    texts = images_to_text(images)
    if not texts:
        print("No text extracted.")
        return
    save_text_to_word(texts, output_doc_path)
    print("Conversion completed successfully!")

# Example usage
if __name__ == "__main__":
    convert_pdf_to_word(PDF_PATH, OUTPUT_DOC_PATH, POPLER_PATH)
