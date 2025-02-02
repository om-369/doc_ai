# Post3 Project

## Description
A document AI processing pipeline for automated content analysis and information extraction.

## Features
- PDF document processing
- NLP-based content analysis
- Entity recognition
- Automated categorization

## Installation
```bash
git clone https://github.com/yourusername/post3.git
cd post3
pip install -r requirements.txt
```

## Usage
```python
python app.py --input documents/ --output results/
```

## Deployment
### AWS S3 Setup
1. Install AWS CLI:
```bash
pip install awscli
```
2. Configure credentials:
```bash
aws configure
```
3. Create S3 bucket:
```bash
aws s3 mb s3://your-bucket-name --region your-region
```
4. Deploy static assets:
```bash
aws s3 sync ./static s3://your-bucket-name/static --acl public-read
```

## Security Configuration

### IAM Role Setup
1. Create IAM policy with S3 access:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::your-bucket-name",
                "arn:aws:s3:::your-bucket-name/*"
            ]
        }
    ]
}
```
2. Create IAM role and attach policy
3. Configure EC2 instance/ECS task to use role

# README updates
## Monitoring Setup

### AWS CloudWatch Alarms:
```bash
# CPU Utilization Alert
aws cloudwatch put-metric-alarm \
    --alarm-name "HighCPUUtilization" \
    --metric-name "CPUUtilization" \
    --namespace "AWS/EC2" \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --alarm-actions "arn:aws:sns:your-region:account-id:your-notification-topic"
## License
MIT License
