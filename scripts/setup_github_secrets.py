import os
import json
import base64
from nacl import encoding, public
import requests
from dotenv import load_dotenv

def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Encrypt a secret using the repository's public key"""
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def setup_github_secrets():
    # Load environment variables
    load_dotenv()
    
    # GitHub configuration
    GITHUB_TOKEN = input("Enter your GitHub Personal Access Token: ")
    REPO_OWNER = "om-369"
    REPO_NAME = "doc_ai"
    
    # Headers for GitHub API
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_TOKEN}",
    }
    
    # Get repository's public key
    key_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets/public-key"
    key_response = requests.get(key_url, headers=headers)
    
    if key_response.status_code != 200:
        print(f"Error getting public key: {key_response.json()}")
        return
    
    key_data = key_response.json()
    public_key = key_data["key"]
    key_id = key_data["key_id"]
    
    # Secrets to set
    secrets = {
        "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
        "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "AWS_S3_BUCKET": os.getenv("AWS_S3_BUCKET"),
        "COSMOS_ENDPOINT": os.getenv("COSMOS_ENDPOINT"),
        "COSMOS_KEY": os.getenv("COSMOS_KEY"),
        "COSMOS_DATABASE": os.getenv("COSMOS_DATABASE"),
        "COSMOS_CONTAINER": os.getenv("COSMOS_CONTAINER"),
        "AZURE_SQL_CONN_STR": os.getenv("AZURE_SQL_CONN_STR"),
        "SNS_TOPIC_ARN": os.getenv("SNS_TOPIC_ARN"),
        "APP_URL": os.getenv("APP_URL", "http://localhost:5000")
    }
    
    print("\nSetting up GitHub Secrets...")
    for secret_name, secret_value in secrets.items():
        if not secret_value:
            print(f"⚠️ Warning: {secret_name} is empty")
            continue
            
        encrypted_value = encrypt_secret(public_key, secret_value)
        
        secret_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets/{secret_name}"
        secret_data = {
            "encrypted_value": encrypted_value,
            "key_id": key_id
        }
        
        response = requests.put(secret_url, headers=headers, json=secret_data)
        
        if response.status_code == 201 or response.status_code == 204:
            print(f"✓ Successfully set {secret_name}")
        else:
            print(f"✗ Failed to set {secret_name}: {response.json()}")
    
    print("\nSetting up environments...")
    environments = ["staging", "production"]
    
    for env in environments:
        env_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/environments/{env}"
        
        env_config = {
            "wait_timer": 0,
            "reviewers": [],
            "deployment_branch_policy": None
        }
        
        if env == "production":
            env_config["wait_timer"] = 600  # 10 minutes
            # Add reviewers if needed
            # env_config["reviewers"] = [{"type": "User", "id": YOUR_GITHUB_USER_ID}]
        
        response = requests.put(env_url, headers=headers, json=env_config)
        
        if response.status_code in [200, 201]:
            print(f"✓ Successfully configured {env} environment")
        else:
            print(f"✗ Failed to configure {env} environment: {response.json()}")

if __name__ == "__main__":
    setup_github_secrets()
