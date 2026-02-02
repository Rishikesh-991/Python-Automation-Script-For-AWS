#!/usr/bin/env python3
import boto3
from botocore.exceptions import ClientError
import logging

# ================= CONFIG =================
REGION = "us-east-1"
VPC_ID = "vpc-xxxxxxxx"  # Replace with your VPC ID
SECURITY_GROUP_NAME = "AutoSecGroup"
SECURITY_GROUP_DESC = "Automated Security Group"
LOG_FILE = "/tmp/security_automation.log"

# IAM policies to attach (example)
POLICIES = [
    "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
    "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
]

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)

# ================= AWS CLIENTS =================
ec2_client = boto3.client("ec2", region_name=REGION)
iam_client = boto3.client("iam", region_name=REGION)

# ================= FUNCTIONS =================

def create_security_group(sg_name, description, vpc_id):
    """Create a security group in a VPC"""
    try:
        response = ec2_client.create_security_group(
            GroupName=sg_name,
            Description=description,
            VpcId=vpc_id
        )
        sg_id = response['GroupId']
        logging.info(f"Security Group created: {sg_id}")
        return sg_id
    except ClientError as e:
        if "InvalidGroup.Duplicate" in str(e):
            logging.info(f"Security Group {sg_name} already exists, fetching ID...")
            response = ec2_client.describe_security_groups(
                Filters=[{"Name": "group-name", "Values": [sg_name]}]
            )
            return response['SecurityGroups'][0]['GroupId']
        logging.error(f"Error creating security group: {e}")
        return None

def add_sg_rules(sg_id):
    """Add inbound and outbound rules to security group"""
    try:
        # Allow HTTP (8080) and custom port (3001)
        ec2_client.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 8080,
                    'ToPort': 8080,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 3001,
                    'ToPort': 3001,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }
            ]
        )
        logging.info(f"Ingress rules added to SG: {sg_id}")

        # Allow all outbound traffic
        ec2_client.authorize_security_group_egress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    'IpProtocol': '-1',
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }
            ]
        )
        logging.info(f"Egress rules added to SG: {sg_id}")

    except ClientError as e:
        if "InvalidPermission.Duplicate" in str(e):
            logging.info(f"Rules already exist for SG: {sg_id}")
        else:
            logging.error(f"Error adding SG rules: {e}")

def attach_policies_to_user(user_name, policies):
    """Attach IAM policies to a specific IAM user"""
    for policy_arn in policies:
        try:
            iam_client.attach_user_policy(
                UserName=user_name,
                PolicyArn=policy_arn
            )
            logging.info(f"Attached {policy_arn} to user {user_name}")
        except ClientError as e:
            logging.error(f"Error attaching policy {policy_arn}: {e}")

def attach_policies_to_role(role_name, policies):
    """Attach IAM policies to a specific IAM role"""
    for policy_arn in policies:
        try:
            iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
            logging.info(f"Attached {policy_arn} to role {role_name}")
        except ClientError as e:
            logging.error(f"Error attaching policy {policy_arn}: {e}")

# ================= MAIN =================
def main():
    sg_id = create_security_group(SECURITY_GROUP_NAME, SECURITY_GROUP_DESC, VPC_ID)
    if sg_id:
        add_sg_rules(sg_id)

    # Example: attach policies
    # Replace with actual user or role
    attach_policies_to_user("my-iam-user", POLICIES)
    attach_policies_to_role("my-iam-role", POLICIES)

if __name__ == "__main__":
    main()
