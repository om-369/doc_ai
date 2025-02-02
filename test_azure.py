import os
from dotenv import load_dotenv
from azure.cosmos import CosmosClient
import pyodbc
import time

def test_cosmos_db():
    print("\nTesting Azure Cosmos DB Connection:")
    print("-" * 40)
    try:
        # Get credentials from environment
        endpoint = os.getenv('COSMOS_ENDPOINT')
        key = os.getenv('COSMOS_KEY')
        database = os.getenv('COSMOS_DATABASE')
        container = os.getenv('COSMOS_CONTAINER')
        
        print(f"Endpoint: {endpoint}")
        print(f"Database: {database}")
        print(f"Container: {container}")
        
        # Create the client
        client = CosmosClient(endpoint, key)
        print("✓ Client created successfully")
        
        # Get database
        db = client.get_database_client(database)
        print("✓ Database client created")
        
        # Get container
        container_client = db.get_container_client(container)
        print("✓ Container client created")
        
        # Test query
        items = list(container_client.query_items(
            query='SELECT TOP 1 * FROM c',
            enable_cross_partition_query=True
        ))
        print(f"✓ Query successful - Found {len(items)} items")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")

def test_sql_connection():
    print("\nTesting Azure SQL Connection:")
    print("-" * 40)
    try:
        conn_str = os.getenv('AZURE_SQL_CONN_STR')
        print("Connection string components:")
        for part in conn_str.split(';'):
            if 'pwd' not in part.lower() and 'password' not in part.lower():
                print(f"  {part}")
        
        print("\nAttempting connection...")
        start_time = time.time()
        
        conn = pyodbc.connect(conn_str, timeout=10)
        print("✓ Connection established")
        
        cursor = conn.cursor()
        print("✓ Cursor created")
        
        # Test basic query
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()
        print("✓ Query executed successfully")
        print(f"SQL Server Version: {version[0][:100]}...")
        
        # Test database access
        cursor.execute("SELECT DB_NAME()")
        db_name = cursor.fetchone()
        print(f"✓ Connected to database: {db_name[0]}")
        
        # Close connections
        cursor.close()
        conn.close()
        print("✓ Connection closed properly")
        
        end_time = time.time()
        print(f"\nTotal connection time: {end_time - start_time:.2f} seconds")
        
    except pyodbc.Error as e:
        print(f"✗ SQL Error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check if the SQL Server is accessible")
        print("2. Verify your IP is allowed in Azure SQL firewall rules")
        print("3. Confirm the connection string format")
        print("4. Ensure the SQL Server is running")
    except Exception as e:
        print(f"✗ General Error: {str(e)}")

if __name__ == "__main__":
    load_dotenv()
    
    print("Azure Connection Tests")
    print("=" * 50)
    
    test_cosmos_db()
    test_sql_connection()
