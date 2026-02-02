#!/usr/bin/env python3
import boto3
from botocore.exceptions import ClientError
import logging

# ================= CONFIG =================
REGION = "us-east-1"       # Change your region
BUCKET_NAME = "my-unique-bucket-2026"  # Bucket names must be globally unique
ENABLE_VERSIONING = True    # Enable versioning (optional)
ENABLE_PUBLIC_ACCESS_BLOCK = True  # Block public access

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ================= AWS CLIENT =================
s3_client = boto3.client("s3", region_name=REGION)

# ================= FUNCTIONS =================
def create_bucket(bucket_name, region):
    """Create an S3 bucket in the specified region"""
    try:
        logging.info(f"Creating bucket: {bucket_name} in {region}...")
        if region == "us-east-1":
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        logging.info(f"Bucket {bucket_name} created successfully.")
        return True
    except ClientError as e:
        logging.error(f"Error creating bucket: {e}")
        return False

def enable_versioning(bucket_name):
    """Enable versioning on the bucket"""
    try:
        s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        logging.info(f"Versioning enabled on bucket {bucket_name}.")
    except ClientError as e:
        logging.error(f"Failed to enable versioning: {e}")

def block_public_access(bucket_name):
    """Block public access to the bucket"""
    try:
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        logging.info(f"Public access blocked for bucket {bucket_name}.")
    except ClientError as e:
        logging.error(f"Failed to block public access: {e}")

# ================= MAIN =================
def main():
    if create_bucket(BUCKET_NAME, REGION):
        if ENABLE_VERSIONING:
            enable_versioning(BUCKET_NAME)
        if ENABLE_PUBLIC_ACCESS_BLOCK:
            block_public_access(BUCKET_NAME)
        logging.info(f"S3 bucket {BUCKET_NAME} is ready.")

if __name__ == "__main__":
    main()
