import json
import boto3
from lambda_function import process_content

BUCKET = "sadhvi-cloud-projects"

def test_process():
    sample = "AWS Cost Report. EC2 running 24/7. S3 has 500GB unused. Need to reduce costs."
    result = process_content(sample, "test.txt")
    print(json.dumps(result, indent=4))

test_process()
