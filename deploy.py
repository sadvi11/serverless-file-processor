import boto3
import json
import zipfile
import time
from botocore.exceptions import ClientError

FUNCTION_NAME = "sadhvi-file-processor"
REGION = "us-east-2"
BUCKET = "sadhvi-cloud-projects"
ZIP_FILE = "lambda_package.zip"

lambda_client = boto3.client("lambda", region_name=REGION)
iam_client = boto3.client("iam", region_name=REGION)
s3_client = boto3.client("s3", region_name="us-east-2")

def create_role():
    role_name = "sadhvi-file-processor-role"
    trust_policy = {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}
    try:
        role = iam_client.create_role(RoleName=role_name, AssumeRolePolicyDocument=json.dumps(trust_policy), Description="Role for file processor")
        iam_client.attach_role_policy(RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole")
        iam_client.attach_role_policy(RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/AmazonS3FullAccess")
        role_arn = role["Role"]["Arn"]
        print("IAM Role created: " + role_arn)
        print("Waiting 10 seconds...")
        time.sleep(10)
        return role_arn
    except ClientError as e:
        if "EntityAlreadyExists" in str(e):
            role = iam_client.get_role(RoleName=role_name)
            role_arn = role["Role"]["Arn"]
            print("Role exists: " + role_arn)
            return role_arn
        print("Role error: " + str(e))
        return None

def zip_code():
    with zipfile.ZipFile(ZIP_FILE, "w") as zf:
        zf.write("lambda_function.py")
    with open(ZIP_FILE, "rb") as f:
        return f.read()

def deploy_lambda(role_arn, zip_bytes):
    try:
        response = lambda_client.create_function(FunctionName=FUNCTION_NAME, Runtime="python3.12", Role=role_arn, Handler="lambda_function.lambda_handler", Code={"ZipFile": zip_bytes}, Description="Sadhvi serverless file processor", Timeout=30, MemorySize=128)
        print("Lambda deployed: " + response["FunctionArn"])
        return True
    except ClientError as e:
        if "ResourceConflictException" in str(e):
            lambda_client.update_function_code(FunctionName=FUNCTION_NAME, ZipFile=zip_bytes)
            return True
        print("Deploy error: " + str(e))
        return False

def add_s3_trigger():
    try:
        account_id = boto3.client("sts", region_name=REGION).get_caller_identity()["Account"]
        try:
            lambda_client.add_permission(FunctionName=FUNCTION_NAME, StatementId="s3-trigger", Action="lambda:InvokeFunction", Principal="s3.amazonaws.com", SourceArn="arn:aws:s3:::" + BUCKET)
        except ClientError as e:
            if "ResourceConflictException" not in str(e):
                raise e
        s3_client.put_bucket_notification_configuration(Bucket=BUCKET, NotificationConfiguration={"LambdaFunctionConfigurations": [{"LambdaFunctionArn": "arn:aws:lambda:" + REGION + ":" + account_id + ":function:" + FUNCTION_NAME, "Events": ["s3:ObjectCreated:*"], "Filter": {"Key": {"FilterRules": [{"Name": "prefix", "Value": "uploads/"}]}}}]})
        return True
    except ClientError as e:
        print("Trigger error: " + str(e))
        return False

print("===== Serverless File Processor Deployer =====")
print("Step 1: Creating IAM role...")
role_arn = create_role()
print("Step 2: Zipping code...")
zip_bytes = zip_code()
print("Step 3: Deploying Lambda...")
deployed = deploy_lambda(role_arn, zip_bytes)
if deployed:
    print("Step 4: Adding S3 trigger...")
    add_s3_trigger()
    print("===== Deployment Complete! =====")
    print("Upload txt files to uploads/ folder")
