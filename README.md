# Serverless File Processor

Automated serverless pipeline built on AWS Lambda and S3.
Upload a file to S3 and Lambda processes it automatically.
Zero servers. Zero manual work. Fully event-driven.

## How It Works

1. Upload any txt file to S3 uploads/ folder
2. S3 automatically triggers Lambda function
3. Lambda reads and analyses the file
4. Lambda saves JSON report to S3 results/ folder
5. Done - zero human intervention

## What Lambda Extracts

- Total lines, words and characters
- Non-empty line count
- Longest line in the document
- First line preview
- Processing timestamp
- File status

## Technologies

- Python 3.12
- AWS Lambda
- AWS S3 and boto3
- IAM roles and permissions
- Event-driven architecture
- S3 trigger notifications

## How to Run

1. Clone this repo
2. Configure AWS credentials: aws configure
3. Run: python3 deploy.py
4. Upload any txt file to S3 uploads/ folder
5. Check results/ folder for JSON output

## Author

Sadhvi Sharma

Nokia 5G Cloud Engineer transitioning to AWS Cloud and AI Engineering

Calgary, Canada

GitHub: github.com/sadvi11

LinkedIn: linkedin.com/in/sadhvi-sharma-5789a6249
