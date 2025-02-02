import os
from dotenv import load_dotenv

def fix_env_file():
    """
    Fix and verify the .env file format.
    This script helps ensure all required environment variables are present
    and properly formatted.
    """
    required_vars = [
        ('FLASK_APP', 'app.py'),
        ('FLASK_ENV', 'development'),
        ('SECRET_KEY', None),
        ('COSMOS_ENDPOINT', None),
        ('COSMOS_KEY', None),
        ('COSMOS_DATABASE', None),
        ('COSMOS_CONTAINER', None),
        ('AZURE_SQL_CONN_STR', None),
        ('AWS_ACCESS_KEY_ID', None),
        ('AWS_SECRET_ACCESS_KEY', None),
        ('AWS_REGION', 'ap-south-1'),
        ('AWS_S3_BUCKET', None),
        ('SNS_TOPIC_ARN', None),
        ('APP_URL', 'http://localhost:5000'),
        ('DEBUG', 'True')
    ]
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("Creating from .env.example...")
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as src, open('.env', 'w') as dst:
                dst.write(src.read())
            print("✓ Created .env from .env.example")
        else:
            print("❌ .env.example not found")
            return
    
    # Load current environment variables
    load_dotenv()
    
    # Verify environment variables
    print("\nVerifying environment variables:")
    missing_vars = []
    for var_name, default_value in required_vars:
        value = os.getenv(var_name)
        if value:
            print(f"✓ {var_name}: Present")
        else:
            print(f"❌ {var_name}: Missing")
            missing_vars.append((var_name, default_value))
    
    if missing_vars:
        print("\n⚠️ Some required variables are missing!")
        print("Please set the following variables in your .env file:")
        for var_name, default_value in missing_vars:
            if default_value:
                print(f"- {var_name} (default: {default_value})")
            else:
                print(f"- {var_name} (required)")
    else:
        print("\n✓ All required variables are present")

if __name__ == "__main__":
    fix_env_file()
