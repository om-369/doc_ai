import os
from dotenv import load_dotenv
import boto3
import json

def test_s3_permissions():
    try:
        s3 = boto3.client('s3')
        
        print("Testing S3 Permissions:")
        print("-" * 30)
        
        # Test ListAllMyBuckets
        print("\n1. Testing ListAllMyBuckets:")
        buckets = s3.list_buckets()
        print(f"✓ Success! Found {len(buckets['Buckets'])} buckets")
        for bucket in buckets['Buckets']:
            print(f"  - {bucket['Name']}")
        
        # Test specific bucket operations
        bucket_name = 'mydocai'
        print(f"\n2. Testing operations on bucket '{bucket_name}':")
        
        # Test ListBucket
        try:
            objects = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
            print(f"✓ ListBucket: Success!")
        except Exception as e:
            print(f"✗ ListBucket: Failed - {str(e)}")
        
        # Test PutObject
        try:
            s3.put_object(Bucket=bucket_name, Key='test.txt', Body='test content')
            print(f"✓ PutObject: Success!")
        except Exception as e:
            print(f"✗ PutObject: Failed - {str(e)}")
            
        # Test GetObject
        try:
            obj = s3.get_object(Bucket=bucket_name, Key='test.txt')
            print(f"✓ GetObject: Success!")
        except Exception as e:
            print(f"✗ GetObject: Failed - {str(e)}")
            
    except Exception as e:
        print(f"Error testing S3: {str(e)}")

def test_sns_permissions():
    try:
        sns = boto3.client('sns')
        
        print("\nTesting SNS Permissions:")
        print("-" * 30)
        
        # Test ListTopics
        print("\n1. Testing ListTopics:")
        topics = sns.list_topics()
        print(f"✓ Success! Found {len(topics['Topics'])} topics")
        
        # Create a test topic
        topic_name = 'doc-ai-notifications-test'
        print(f"\n2. Testing topic creation '{topic_name}':")
        try:
            response = sns.create_topic(Name=topic_name)
            topic_arn = response['TopicArn']
            print(f"✓ CreateTopic: Success! ARN: {topic_arn}")
            
            # Test topic attributes
            try:
                attrs = sns.get_topic_attributes(TopicArn=topic_arn)
                print(f"✓ GetTopicAttributes: Success!")
            except Exception as e:
                print(f"✗ GetTopicAttributes: Failed - {str(e)}")
            
            # Clean up - delete test topic
            sns.delete_topic(TopicArn=topic_arn)
            print(f"✓ Cleanup: Test topic deleted")
            
        except Exception as e:
            print(f"✗ Topic operations failed: {str(e)}")
            
    except Exception as e:
        print(f"Error testing SNS: {str(e)}")

if __name__ == "__main__":
    load_dotenv()
    
    print("AWS Permissions Test")
    print("=" * 50)
    
    test_s3_permissions()
    test_sns_permissions()
