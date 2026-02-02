# What this script does

# Creates IAM Role for Lambda with basic execution policy.

# Zips Python code for deployment.

# Creates Lambda function.

# Updates Lambda code if needed.

# Deletes Lambda function.

import boto3
import logging              
import zipfile
import os
from botocore.exceptions import ClientError

# ================= CONFIG =================
REGION = "us-east-1"
LAMBDA_FUNCTION_NAME = "MyLambdaFunction"
LAMBDA_RUNTIME = "python3.8"
LAMBDA_HANDLER = "lambda_function.lambda_handler"
ROLE_NAME = "MyLambdaExecutionRole"