# What this script does

# Creates IAM Role for Lambda with basic execution policy.

# Zips Python code for deployment.

# Creates Lambda function.

# Updates Lambda code if needed.

# Deletes Lambda function.

#!/usr/bin/env python3
import boto3
from botocore.exceptions import ClientError
import logging
import zipfile
import os

# ================= CONFIG =================
REGION = "us-east-1"
LOG_FILE = "/tmp/lambda_manager.log"

# Lambda config
FUNCTION_NAME = "MyLambdaFunction"
RUNTIME = "python3.11"
HANDLER = "lambda_function.lambda_handler"
ROLE_NAME = "LambdaExecutionRole"
ZIP_FILE = "/tmp/lambda_function.zip"  # The zipped Python code

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)

# ================= AWS CLIENT =================
iam_client = boto3.client("iam", region_name=REGION)
lambda_client = boto3.client("lambda", region_name=REGION)

# ================= FUNCTIONS =================

def create_lambda_role(role_name):
    """Create an IAM role for Lambda execution"""
    assume_role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {"Effect": "Allow",
             "Principal": {"Service": "lambda.amazonaws.com"},
             "Action": "sts:AssumeRole"}
        ]
    }
    try:
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=str(assume_role_policy).replace("'", '"'),
            Description="Role for Lambda execution"
        )
        logging.info(f"IAM Role created: {role_name}")
        role_arn = response['Role']['Arn']

        # Attach AWSLambdaBasicExecutionRole policy
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
        )
        logging.info(f"Attached AWSLambdaBasicExecutionRole to {role_name}")
        return role_arn
    except ClientError as e:
        if "EntityAlreadyExists" in str(e):
            logging.info(f"Role {role_name} already exists, fetching ARN...")
            response = iam_client.get_role(RoleName=role_name)
            return response['Role']['Arn']
        logging.error(f"Error creating role: {e}")
        return None

def zip_lambda_code(source_file, zip_file):
    """Zip the Python code for Lambda"""
    with zipfile.ZipFile(zip_file, 'w') as z:
        z.write(source_file, arcname=os.path.basename(source_file))
    logging.info(f"Created ZIP file: {zip_file}")

def create_lambda_function(function_name, role_arn, zip_file, runtime=RUNTIME, handler=HANDLER):
    """Create a Lambda function"""
    try:
        with open(zip_file, 'rb') as f:
            code_bytes = f.read()

        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime=runtime,
            Role=role_arn,
            Handler=handler,
            Code={'ZipFile': code_bytes},
            Timeout=15,
            MemorySize=128,
            Publish=True
        )
        logging.info(f"Lambda function created: {function_name}")
        return response['FunctionArn']
    except ClientError as e:
        logging.error(f"Error creating Lambda function: {e}")
        return None

def update_lambda_function_code(function_name, zip_file):
    """Update Lambda code"""
    try:
        with open(zip_file, 'rb') as f:
            code_bytes = f.read()

        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=code_bytes,
            Publish=True
        )
        logging.info(f"Lambda function code updated: {function_name}")
        return response['FunctionArn']
    except ClientError as e:
        logging.error(f"Error updating Lambda function code: {e}")
        return None

def delete_lambda_function(function_name):
    """Delete Lambda function"""
    try:
        lambda_client.delete_function(FunctionName=function_name)
        logging.info(f"Lambda function deleted: {function_name}")
    except ClientError as e:
        logging.error(f"Error deleting Lambda function: {e}")

# ================= MAIN =================
def main():
    # Create IAM role
    role_arn = create_lambda_role(ROLE_NAME)
    if not role_arn:
        logging.error("Cannot proceed without Lambda execution role")
        return

    # Prepare sample Lambda code
    sample_code = """
def lambda_handler(event, context):
    return {'statusCode': 200, 'body': 'Hello from Lambda!'}
"""
    source_file = "/tmp/lambda_function.py"
    with open(source_file, 'w') as f:
        f.write(sample_code)

    # Zip code
    zip_lambda_code(source_file, ZIP_FILE)

    # Create Lambda function
    create_lambda_function(FUNCTION_NAME, role_arn, ZIP_FILE)

    # Example: Update function code
    # update_lambda_function_code(FUNCTION_NAME, ZIP_FILE)

    # Example: Delete function
    # delete_lambda_function(FUNCTION_NAME)

if __name__ == "__main__":
    main()
