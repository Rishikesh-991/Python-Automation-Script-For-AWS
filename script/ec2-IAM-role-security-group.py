# List all VPCs in the account.

# List all EC2 instances in each VPC.

# Check and attach a security group (with ports 8080 & 3001 open) to each instance.

# Attach IAM roles or policies to instances if they are missing.

# Log everything for auditing.


#!/usr/bin/env python3
import boto3
from botocore.exceptions import ClientError
import logging
import time

# ================= CONFIG =================
REGION = "us-east-1"
SECURITY_GROUP_NAME = "AutoSecGroup"
SECURITY_GROUP_DESC = "Automated Security Group for all EC2"
POLICIES = [
    "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
    "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
]
LOG_FILE = "/tmp/full_security_automation.log"

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)

# ================= AWS CLIENTS =================
ec2_client = boto3.client("ec2", region_name=REGION)
iam_client = boto3.client("iam", region_name=REGION)
ec2_resource = boto3.resource("ec2", region_name=REGION)

# ================= FUNCTIONS =================

def create_security_group(vpc_id):
    """Create or get security group in a VPC"""
    try:
        response = ec2_client.create_security_group(
            GroupName=SECURITY_GROUP_NAME,
            Description=SECURITY_GROUP_DESC,
            VpcId=vpc_id
        )
        sg_id = response['GroupId']
        logging.info(f"Created Security Group {sg_id} in VPC {vpc_id}")
    except ClientError as e:
        if "InvalidGroup.Duplicate" in str(e):
            logging.info(f"Security Group {SECURITY_GROUP_NAME} already exists in VPC {vpc_id}")
            response = ec2_client.describe_security_groups(
                Filters=[{"Name": "group-name", "Values": [SECURITY_GROUP_NAME]},
                         {"Name": "vpc-id", "Values": [vpc_id]}]
            )
            sg_id = response['SecurityGroups'][0]['GroupId']
        else:
            logging.error(f"Failed to create Security Group: {e}")
            return None

    # Add ingress rules
    try:
        ec2_client.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {'IpProtocol': 'tcp', 'FromPort': 8080, 'ToPort': 8080, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp', 'FromPort': 3001, 'ToPort': 3001, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
            ]
        )
    except ClientError as e:
        if "InvalidPermission.Duplicate" in str(e):
            logging.info("Ingress rules already exist")
        else:
            logging.error(f"Error adding ingress rules: {e}")

    # Allow all outbound
    try:
        ec2_client.authorize_security_group_egress(
            GroupId=sg_id,
            IpPermissions=[{'IpProtocol': '-1', 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}]
        )
    except ClientError as e:
        if "InvalidPermission.Duplicate" in str(e):
            logging.info("Egress rules already exist")
        else:
            logging.error(f"Error adding egress rules: {e}")

    return sg_id

def attach_sg_to_instance(instance_id, sg_id):
    """Attach security group to an EC2 instance"""
    instance = ec2_resource.Instance(instance_id)
    current_sgs = [sg['GroupId'] for sg in instance.security_groups]
    if sg_id not in current_sgs:
        new_sgs = current_sgs + [sg_id]
        instance.modify_attribute(Groups=new_sgs)
        logging.info(f"Attached SG {sg_id} to instance {instance_id}")
    else:
        logging.info(f"Instance {instance_id} already has SG {sg_id}")

def attach_policies_to_role(role_name, policies):
    """Attach IAM policies to a role"""
    for policy_arn in policies:
        try:
            iam_client.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
            logging.info(f"Attached {policy_arn} to role {role_name}")
        except ClientError as e:
            if "EntityAlreadyExists" in str(e):
                logging.info(f"Policy {policy_arn} already attached to role {role_name}")
            else:
                logging.error(f"Error attaching policy {policy_arn}: {e}")

def get_all_vpcs():
    """Return all VPC IDs in the region"""
    vpcs = ec2_client.describe_vpcs()
    return [vpc['VpcId'] for vpc in vpcs['Vpcs']]

def get_instances_in_vpc(vpc_id):
    """Return all EC2 instance IDs in a VPC"""
    instances = ec2_client.describe_instances(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])
    instance_ids = []
    for res in instances['Reservations']:
        for inst in res['Instances']:
            instance_ids.append(inst['InstanceId'])
    return instance_ids

# ================= MAIN =================
def main():
    vpcs = get_all_vpcs()
    logging.info(f"Found VPCs: {vpcs}")

    for vpc_id in vpcs:
        sg_id = create_security_group(vpc_id)
        instances = get_instances_in_vpc(vpc_id)
        if not instances:
            logging.info(f"No EC2 instances in VPC {vpc_id}")
            continue
        for instance_id in instances:
            attach_sg_to_instance(instance_id, sg_id)

            # Attach IAM role policies if instance has IAM role
            instance = ec2_resource.Instance(instance_id)
            if 'IamInstanceProfile' in instance.meta.data:
                arn = instance.iam_instance_profile_arn
                role_name = arn.split('/')[-1]
                attach_policies_to_role(role_name, POLICIES)

if __name__ == "__main__":
    main()
