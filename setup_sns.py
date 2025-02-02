import os
from dotenv import load_dotenv
import boto3
import json



def setup_sns():
    try:
        sns = boto3.client('sns')
        
        # Create the SNS topic
        print("Creating SNS topic...")
        topic_response = sns.create_topic(Name='doc-ai-notifications')
        topic_arn = topic_response['TopicArn']
        print(f"✓ Topic created: {topic_arn}")
        
        # Set topic attributes
        print("\nSetting topic attributes...")
        sns.set_topic_attributes(
            TopicArn=topic_arn,
            AttributeName='DisplayName',
            AttributeValue='Doc AI Notifications'
        )
        print("✓ Topic display name set")
        
        # Update environment variable
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        with open(env_path, 'r') as file:
            lines = file.readlines()
        
        with open(env_path, 'w') as file:
            for line in lines:
                if line.startswith('SNS_TOPIC_ARN='):
                    file.write(f'SNS_TOPIC_ARN="{topic_arn}"\n')
                else:
                    file.write(line)
        
        print(f"\n✓ Updated .env with new topic ARN")
        print("\nSNS Topic setup complete!")
        print("-" * 50)
        print("Next steps:")
        print("1. Add email subscribers using:")
        print(f"   aws sns subscribe --topic-arn {topic_arn} --protocol email --notification-endpoint your-email@example.com")
        print("\n2. Update your GitHub Actions secrets with the new SNS_TOPIC_ARN")
        
    except Exception as e:
        print(f"Error setting up SNS: {str(e)}")

if __name__ == "__main__":
    load_dotenv()
    setup_sns()
