import os
from dotenv import load_dotenv
import boto3
from azure.cosmos import CosmosClient
import pyodbc
import json

def test_aws_connection():
    try:
        # Test S3
        s3 = boto3.client('s3')
        response = s3.list_buckets()
        print("AWS S3 Connection: Success")
        print(f"Available buckets: {[bucket['Name'] for bucket in response['Buckets']]}")
        
        # Test SNS
        sns = boto3.client('sns')
        topics = sns.list_topics()
        print("\nAWS SNS Connection: Success")
        print(f"Available topics: {json.dumps(topics['Topics'], indent=2)}")
    except Exception as e:
        print(f"AWS Connection Error: {str(e)}")

def test_cosmos_connection():
    try:
        client = CosmosClient(
            os.getenv('COSMOS_ENDPOINT'),
            os.getenv('COSMOS_KEY')
        )
        db = client.get_database_client(os.getenv('COSMOS_DATABASE'))
        container = db.get_container_client(os.getenv('COSMOS_CONTAINER'))
        
        # Test with a simple query
        items = list(container.query_items(
            query='SELECT TOP 1 * FROM c',
            enable_cross_partition_query=True
        ))
        print("\nAzure Cosmos DB Connection: Success")
        print(f"Found {len(items)} items in test query")
    except Exception as e:
        print(f"Cosmos DB Connection Error: {str(e)}")

def test_azure_sql_connection():
    try:
        conn = pyodbc.connect(os.getenv('AZURE_SQL_CONN_STR'))
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()
        print("\nAzure SQL Connection: Success")
        print(f"SQL Server Version: {version[0][:50]}...")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Azure SQL Connection Error: {str(e)}")

if __name__ == "__main__":
    load_dotenv()
    print("Testing all connections...")
    print("-" * 50)
    
    test_aws_connection()
    test_cosmos_connection()
    test_azure_sql_connection()
