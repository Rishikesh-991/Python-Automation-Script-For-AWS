#!/usr/bin/env python3
import boto3
from botocore.exceptions import ClientError
import logging

# ================= CONFIG =================
REGION = "us-east-1"  # Region doesn't matter for IAM
LOG_FILE = "/tmp/iam_manager.log"

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# ================= AWS CLIENT =================
iam_client = boto3.client('iam', region_name=REGION)

# ================= FUNCTIONS =================

# ----- IAM USER -----
def create_user(username):
    try:
        iam_client.create_user(UserName=username)
        logging.info(f"IAM User created: {username}")
    except ClientError as e:
        logging.error(f"Error creating user {username}: {e}")

def delete_user(username):
    try:
        iam_client.delete_user(UserName=username)
        logging.info(f"IAM User deleted: {username}")
    except ClientError as e:
        logging.error(f"Error deleting user {username}: {e}")

def attach_user_policy(username, policy_arn):
    try:
        iam_client.attach_user_policy(UserName=username, PolicyArn=policy_arn)
        logging.info(f"Policy {policy_arn} attached to user {username}")
    except ClientError as e:
        logging.error(f"Error attaching policy: {e}")

# ----- IAM ROLE -----
def create_role(role_name, service_name):
    """
    service_name: AWS service, e.g., 'ec2.amazonaws.com', 'lambda.amazonaws.com'
    """
    assume_role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": service_name},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    try:
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=str(assume_role_policy).replace("'", '"'),
            Description=f"Role for {service_name}"
        )
        logging.info(f"IAM Role created: {role_name}")
        return response['Role']['Arn']
    except ClientError as e:
        logging.error(f"Error creating role {role_name}: {e}")
        return None

def delete_role(role_name):
    try:
        iam_client.delete_role(RoleName=role_name)
        logging.info(f"IAM Role deleted: {role_name}")
    except ClientError as e:
        logging.error(f"Error deleting role {role_name}: {e}")

def attach_role_policy(role_name, policy_arn):
    try:
        iam_client.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
        logging.info(f"Policy {policy_arn} attached to role {role_name}")
    except ClientError as e:
        logging.error(f"Error attaching policy to role: {e}")

# ----- IAM GROUP -----
def create_group(group_name):
    try:
        iam_client.create_group(GroupName=group_name)
        logging.info(f"IAM Group created: {group_name}")
    except ClientError as e:
        logging.error(f"Error creating group {group_name}: {e}")

def delete_group(group_name):
    try:
        iam_client.delete_group(GroupName=group_name)
        logging.info(f"IAM Group deleted: {group_name}")
    except ClientError as e:
        logging.error(f"Error deleting group {group_name}: {e}")

def add_user_to_group(username, group_name):
    try:
        iam_client.add_user_to_group(UserName=username, GroupName=group_name)
        logging.info(f"User {username} added to group {group_name}")
    except ClientError as e:
        logging.error(f"Error adding user to group: {e}")

# ================= MAIN =================
def main():
    # Example usage

    # Create a user
    create_user("dev-user")

    # Attach a managed policy to the user
    attach_user_policy("dev-user", "arn:aws:iam::aws:policy/AmazonS3FullAccess")

    # Create a group and add user
    create_group("developers")
    add_user_to_group("dev-user", "developers")

    # Create a role for EC2 service
    role_arn = create_role("EC2-S3-Access-Role", "ec2.amazonaws.com")
    if role_arn:
        attach_role_policy("EC2-S3-Access-Role", "arn:aws:iam::aws:policy/AmazonS3FullAccess")

    # Delete examples (uncomment to test deletion)
    # delete_user("dev-user")
    # delete_group("developers")
    # delete_role("EC2-S3-Access-Role")

if __name__ == "__main__":
    main()
