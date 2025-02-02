#!/bin/bash
# Automated deployment script
set -e

echo "Starting deployment process..."

# Install dependencies
echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Configure AWS CLI
echo "Configuring AWS..."
aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
aws configure set default.region ap-south-1

# Ensure S3 bucket exists
echo "Checking S3 bucket..."
if ! aws s3api head-bucket --bucket $AWS_S3_BUCKET 2>/dev/null; then
    echo "Creating S3 bucket..."
    aws s3api create-bucket \
        --bucket $AWS_S3_BUCKET \
        --region ap-south-1 \
        --create-bucket-configuration LocationConstraint=ap-south-1
fi

# Sync static assets
echo "Syncing static assets..."
if [ -d "./static" ]; then
    aws s3 sync ./static s3://$AWS_S3_BUCKET/static --acl public-read
fi

# Set up environment variables
echo "Setting up environment..."
export FLASK_APP=app.py
export FLASK_ENV=production

# Start application with Gunicorn
echo "Starting application..."
gunicorn app:app \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance \
    --daemon

echo "Deployment completed successfully!"
