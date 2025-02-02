from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from azure.cosmos import CosmosClient
from pdf2image import convert_from_path
import fitz  # PyMuPDF for text extraction
import os
import pytesseract
from PIL import Image
import datetime
import pyodbc
import binascii
import base64
from operations import process_pdf_to_text
# from PyPDF2 import PdfReader

# Add to imports
import boto3
from botocore.exceptions import ClientError

# Flask application setup
app = Flask(__name__)
app.secret_key = 'Riya@112020'

# Configure upload folders
UPLOAD_FOLDER = 'uploads/'
IMAGE_FOLDER = 'images/'
OUTPUT_TEXT_FOLDER = 'output__text/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
# Mock database for user credentials and activities
users = {
    "user1": generate_password_hash("password1"),
    "user2": generate_password_hash("password2"),
    "user3": generate_password_hash("password3"),
    "user4": generate_password_hash("password4"),
    "user5": generate_password_hash("password5"),
}
user_activities = {}

# Azure Cosmos DB configuration
COSMOS_ENDPOINT = os.environ.get('COSMOS_ENDPOINT')
COSMOS_KEY = os.environ.get('COSMOS_KEY')
COSMOS_DB_NAME = os.environ.get('COSMOS_DB_NAME')
COSMOS_CONTAINER_NAME = os.environ.get('COSMOS_CONTAINER_NAME')

# Azure SQL connection
AZURE_SQL_CONN_STR = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=tcp:pro-ai-jects.database.windows.net,1433;"
    "Database=pro-ai-jects;"
    "UID=pro-ai-jects;"
    "PWD=Siya@112020;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Timeout=60;"
)

# AWS S3 Configuration
AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# Initialize Cosmos DB
def initialize_cosmos_container():
    client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
    database = client.create_database_if_not_exists(COSMOS_DB_NAME)
    container = database.create_container_if_not_exists(
        id=COSMOS_CONTAINER_NAME,
        partition_key={"paths": ["/partitionKey"], "kind": "Hash"},
    )
    return container

cosmos_container = initialize_cosmos_container()


# Helper function: Get Azure SQL connection
def get_db_connection():
    try:
        return pyodbc.connect(AZURE_SQL_CONN_STR)
    except pyodbc.Error as e:
        print(f"Azure SQL connection error: {e}")
        raise e


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Users WHERE Username = ?", (username,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return "User already exists!", 400

        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO Users (Username, PasswordHash) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))

    return render_template('register.html')


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute("SELECT UserID, PasswordHash FROM Users WHERE Username = ?", (username,))
#         user = cursor.fetchone()
#         conn.close()

#         if user and check_password_hash(user[1], password):
#             session['user'] = username
#             session['user_id'] = user[0]
#             session['session_id'] = f"{username}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
#             return redirect(url_for('dashboard'))
#         # return "Invalid username or password!", 401

#         # Set session and log activity
#         session['user'] = username
#         session['session_id'] = f"session_{username}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
#         user_activities[username].append(f"Logged in at {datetime.datetime.now()}")
#         return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT UserID, PasswordHash FROM Users WHERE Username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session['user'] = username
            session['user_id'] = user[0]
            session['session_id'] = f"{username}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            return redirect(url_for('dashboard'))  # Make sure this line is correct
        
        return "Invalid username or password!", 401

    return render_template('login.html')

# @app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    username = session['user']
    session_id = session['session_id']

    if username not in user_activities:
        user_activities[username] = []

    if request.method == 'POST':
        try:
            file = request.files['file']
            if file and file.filename.endswith('.pdf'):
                filename = secure_filename(f"{session_id}_{file.filename}")
                pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(pdf_path)

                # Process the PDF: Convert to images and extract text
                image_paths, ocr_text_path = process_pdf_to_text(pdf_path, session_id, username)

                # Log activity
                user_activities[username].append(f"Uploaded and processed file '{filename}' at {datetime.datetime.now()}")

                # Save results to Cosmos DB
                with open(ocr_text_path, "r", encoding="utf-8") as text_file:
                    extracted_text = text_file.read()
                cosmos_container.upsert_item({
                    "id": f"{session_id}_{os.path.basename(ocr_text_path)}",
                    "partitionKey": username,
                    "text": extracted_text,
                })

                return jsonify({
                    "message": "File processed successfully!",
                    "pdf_path": pdf_path,
                    "image_paths": image_paths,
                    "ocr_path": ocr_text_path,
                }), 200
            else:
                return jsonify({"error": "Invalid file format. Please upload a PDF."}), 400
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return jsonify({"error": "An error occurred while processing the file."}), 500

    activities = user_activities.get(username, [])
    return render_template('dashboard.html', username=username, activities=activities)
@app.route('/logout')
def logout():
    if 'user' in session:
        username = session['user']
        user_activities[username].append(f"Logged out at {datetime.datetime.now()}")
        session.pop('user')

    return redirect(url_for('index'))
# Add to app.py
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "azure_cosmos": check_cosmos_connection(),
            "aws_s3": check_s3_connection()
        }
    })

def check_cosmos_connection():
    try:
        cosmos_container.read_item('health-check', 'health-check')
        return "connected"
    except:
        return "disconnected"

def check_s3_connection():
    try:
        s3_client.head_bucket(Bucket=os.environ.get('AWS_S3_BUCKET'))
        return "connected"
    except ClientError:
        return "disconnected"

if __name__ == '__main__':
    app.run(debug=True)