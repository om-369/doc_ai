import sys
import os
from flask import Flask
import boto3
from azure.cosmos import CosmosClient
import pyodbc
import fitz  # PyMuPDF
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

def test_dependencies():
    results = {}
    
    # Test Flask
    try:
        app = Flask(__name__)
        results['Flask'] = "OK"
    except Exception as e:
        results['Flask'] = f"Error: {str(e)}"
    
    # Test PyMuPDF
    try:
        version = fitz.__version__
        results['PyMuPDF'] = f"OK (version {version})"
    except Exception as e:
        results['PyMuPDF'] = f"Error: {str(e)}"
    
    # Test Pillow
    try:
        version = Image.__version__
        results['Pillow'] = f"OK (version {version})"
    except Exception as e:
        results['Pillow'] = f"Error: {str(e)}"
    
    print("\nDependency Test Results:")
    print("------------------------")
    for package, status in results.items():
        print(f"{package}: {status}")

if __name__ == "__main__":
    test_dependencies()
