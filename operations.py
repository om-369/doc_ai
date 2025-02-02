import os
from pdf2image import convert_from_path
from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from google.cloud import vision
from PIL import Image
import datetime

# Google Document AI configuration
PROJECT_ID = "pro-ai-jects"
LOCATION = "us"
PROCESSOR_ID = "pro-ai-jects-processor"
MIME_TYPE = "image/png"


# Set Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"E:\google keys\gcp credentials\luminous-pier-447309-d2-c68ee3c993f4.json"

# Folders for uploads and image storage
UPLOAD_FOLDER = 'uploads/'
IMAGE_FOLDER = 'images/'
OUTPUT_TEXT_FOLDER = 'output__text/'

# def convert_pdf_to_images(pdf_path, session_id, username):
#     """
#     Converts a PDF file to images for each page.

#     Args:
#         pdf_path (str): Path to the PDF file.
#         session_id (str): Unique session identifier.
#         username (str): Name of the user.

#     Returns:
#         list: List of file paths for the generated images.
#     """
#     user_image_folder = os.path.join(IMAGE_FOLDER, username)
#     os.makedirs(user_image_folder, exist_ok=True)  # Ensure user's image folder exists

#     # Convert PDF to images
#     images = convert_from_path(pdf_path)
#     image_paths = []

#     for i, image in enumerate(images):
#         image_filename = f"{session_id}_page_{i + 1}.png"
#         image_path = os.path.join(user_image_folder, image_filename)
#         image.save(image_path, "PNG")
#         image_paths.append(image_path)

#     return image_paths


# def extract_text_from_images(image_paths):
#     """
#     Extracts text from a list of images using Google Vision API.

#     Args:
#         image_paths (list): List of image file paths.

#     Returns:
#         str: Concatenated text extracted from all images.
#     """
#     client = vision.ImageAnnotatorClient()
#     full_text = ""

#     for image_path in image_paths:
#         # Open the image file
#         with open(image_path, "rb") as image_file:
#             content = image_file.read()

#         # Create Google Vision API request
#         image = vision.Image(content=content)
#         response = client.text_detection(image=image)

#         # Extract text from the response
#         if response.text_annotations:
#             full_text += response.text_annotations[0].description + "\n"
    
#     with open("output_text/output.txt", "w",encoding="utf-8") as text_file:
#         text_file.write(full_text)
#     print("full text",full_text)
#     return full_text


# def process_pdf_to_text(pdf_path, session_id, username):
#     """
#     Handles the entire workflow of converting a PDF to images and extracting text.

#     Args:
#         pdf_path (str): Path to the PDF file.
#         session_id (str): Unique session identifier.
#         username (str): Name of the user.

#     Returns:
#         tuple: Paths to the processed images and the extracted text file.
#     """
#     # Convert PDF to images
#     image_paths = convert_pdf_to_images(pdf_path, session_id, username)

#     # Extract text from the images
#     extracted_text = extract_text_from_images(image_paths)

#     # Save the extracted text to a file
#     ocr_text_path = os.path.join(OUTPUT_TEXT_FOLDER, f"{session_id}_ocr.txt")


#     return image_paths, ocr_text_path

import os
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

OUTPUT_TEXT_FOLDER = "output_text"  # Ensure this matches your project folder structure
os.makedirs(OUTPUT_TEXT_FOLDER, exist_ok=True)

def convert_pdf_to_images(pdf_path, session_id, username):
    """
    Converts a PDF file to images for each page.

    Args:
        pdf_path (str): Path to the PDF file.
        session_id (str): Unique session identifier.
        username (str): Name of the user.

    Returns:
        list: List of paths to the generated images.
    """
    user_image_folder = os.path.join("images", username)
    os.makedirs(user_image_folder, exist_ok=True)  # Ensure the user's image folder exists

    images = convert_from_path(pdf_path)
    image_paths = []

    for i, image in enumerate(images):
        image_filename = f"{session_id}_page_{i + 1}.png"
        image_path = os.path.join(user_image_folder, image_filename)
        image.save(image_path, "PNG")
        image_paths.append(image_path)

    return image_paths


def extract_text_from_images(image_paths):
    """
    Extracts text from a list of image paths using Tesseract OCR.

    Args:
        image_paths (list): List of paths to image files.

    Returns:
        str: Combined text extracted from all images.
    """
    extracted_text = ""
    for image_path in image_paths:
        # Use Tesseract to extract text from the image
        text = pytesseract.image_to_string(Image.open(image_path), lang="eng")
        extracted_text += f"\n--- Text from {os.path.basename(image_path)} ---\n{text}\n"
    return extracted_text


def process_pdf_to_text(pdf_path, session_id, username):
    """
    Handles the entire workflow of converting a PDF to images and extracting text.

    Args:
        pdf_path (str): Path to the PDF file.
        session_id (str): Unique session identifier.
        username (str): Name of the user.

    Returns:
        tuple: Paths to the processed images and the extracted text file.
    """
    # Convert PDF to images
    image_paths = convert_pdf_to_images(pdf_path, session_id, username)

    # Extract text from the images
    extracted_text = extract_text_from_images(image_paths)

    # Save the extracted text to a file
    ocr_text_path = os.path.join(OUTPUT_TEXT_FOLDER, f"{session_id}_ocr.txt")
    with open(ocr_text_path, "w", encoding="utf-8") as text_file:
        text_file.write(extracted_text)

    return image_paths, ocr_text_path
