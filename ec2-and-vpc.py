#!/usr/bin/env python3
import boto3
from botocore.exceptions import ClientError
import logging
import time

# ================= CONFIG =================
REGION = "us-east-1"
AMI_ID = "ami-0c94855ba95c71c99"  # Amazon Linux 2
INSTANCE_TYPE = "t2.micro"
KEY_NAME = "my-key"  # Must exist in your AWS account

VPC_CIDR = "10.0.0.0/16"
SUBNET_CIDR = "10.0.1.0/24"
SECURITY_GROUP_NAME = "MySecurityGroup"
SECURITY_GROUP_DESC = "Security group for ports 8080 and 3001"

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ================= AWS CLIENTS =================
ec2_client = boto3.client("ec2", region_name=REGION)
ec2_resource = boto3.resource("ec2", region_name=REGION)

# ================= FUNCTIONS =================
def create_vpc():
    logging.info("Creating VPC...")
    vpc = ec2_resource.create_vpc(CidrBlock=VPC_CIDR)
    vpc.wait_until_available()
    vpc.create_tags(Tags=[{"Key": "Name", "Value": "MyVPC"}])
    logging.info(f"VPC created: {vpc.id}")

    # Enable DNS support
    ec2_client.modify_vpc_attribute(VpcId=vpc.id, EnableDnsHostnames={'Value': True})
    logging.info(f"Enabled DNS hostnames for VPC {vpc.id}")

    # Create subnet
    subnet = vpc.create_subnet(CidrBlock=SUBNET_CIDR)
    logging.info(f"Subnet created: {subnet.id}")

    # Create Internet Gateway and attach
    igw = ec2_resource.create_internet_gateway()
    vpc.attach_internet_gateway(InternetGatewayId=igw.id)
    logging.info(f"Internet Gateway created and attached: {igw.id}")

    # Create route table
    route_table = vpc.create_route_table()
    route_table.create_route(DestinationCidrBlock="0.0.0.0/0", GatewayId=igw.id)
    route_table.associate_with_subnet(SubnetId=subnet.id)
    logging.info(f"Route table configured with IGW for subnet {subnet.id}")

    return vpc, subnet

def create_security_group(vpc_id):
    logging.info("Creating Security Group...")
    sg = ec2_client.create_security_group(
        GroupName=SECURITY_GROUP_NAME,
        Description=SECURITY_GROUP_DESC,
        VpcId=vpc_id
    )
    sg_id = sg['GroupId']
    logging.info(f"Security Group created: {sg_id}")

    # Open ports 8080 and 3001 for inbound traffic
    ec2_client.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {'IpProtocol': 'tcp',
             'FromPort': 8080,
             'ToPort': 8080,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp',
             'FromPort': 3001,
             'ToPort': 3001,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ]
    )
    logging.info("Opened ports 8080 and 3001")
    return sg_id

def launch_ec2_instance(subnet_id, sg_id):
    logging.info("Launching EC2 instance with Nginx setup...")

    # User-data script to install and configure Nginx
    user_data_script = """#!/bin/bash
yum update -y
amazon-linux-extras enable nginx1
yum install -y nginx
mkdir -p /usr/share/nginx/html
echo "<h1>Nginx running on port 8080</h1>" > /usr/share/nginx/html/index.html
# Configure Nginx to listen on 8080 and 3001
sed -i 's/listen       80;/listen       8080;/' /etc/nginx/nginx.conf
echo 'server { listen 3001; location / { root /usr/share/nginx/html; index index.html; } }' >> /etc/nginx/conf.d/custom.conf
systemctl enable nginx
systemctl start nginx
"""

    instances = ec2_resource.create_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        MaxCount=1,
        MinCount=1,
        UserData=user_data_script,
        NetworkInterfaces=[{
            'SubnetId': subnet_id,
            'DeviceIndex': 0,
            'AssociatePublicIpAddress': True,
            'Groups': [sg_id]
        }]
    )
    instance = instances[0]
    logging.info(f"Instance {instance.id} launched. Waiting for running state...")
    instance.wait_until_running()
    instance.reload()
    logging.info(f"Instance is running at public IP: {instance.public_ip_address}")
    return instance.id, instance.public_ip_address

# ================= MAIN =================
def main():
    vpc, subnet = create_vpc()
    sg_id = create_security_group(vpc.id)
    instance_id, public_ip = launch_ec2_instance(subnet.id, sg_id)
    logging.info(f"EC2 instance {instance_id} is ready.")
    logging.info(f"Access Nginx on http://{public_ip}:8080 and http://{public_ip}:3001")

if __name__ == "__main__":
    main()
