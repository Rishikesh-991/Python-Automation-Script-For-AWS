#!/usr/bin/env python3
import boto3
from botocore.exceptions import ClientError
import logging
import time

# ================= CONFIG =================
REGION = "us-east-1"

DB_IDENTIFIER = "my-postgres-db"
DB_NAME = "mydb"
DB_USERNAME = "adminuser"
DB_PASSWORD = "StrongPassword123!"  # Must meet AWS RDS password rules
DB_INSTANCE_CLASS = "db.t3.micro"   # Free tier eligible
DB_ENGINE = "postgres"
DB_PORT = 5432

VPC_CIDR = "10.0.0.0/16"
SUBNET_CIDR = "10.0.1.0/24"
SECURITY_GROUP_NAME = "RDS-SG"
SECURITY_GROUP_DESC = "Allow PostgreSQL access"

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ================= AWS CLIENTS =================
ec2_client = boto3.client("ec2", region_name=REGION)
ec2_resource = boto3.resource("ec2", region_name=REGION)
rds_client = boto3.client("rds", region_name=REGION)

# ================= FUNCTIONS =================
def create_vpc():
    logging.info("Creating VPC...")
    vpc = ec2_resource.create_vpc(CidrBlock=VPC_CIDR)
    vpc.wait_until_available()
    vpc.create_tags(Tags=[{"Key": "Name", "Value": "RDSVPC"}])
    logging.info(f"VPC created: {vpc.id}")

    # Enable DNS hostnames
    ec2_client.modify_vpc_attribute(VpcId=vpc.id, EnableDnsHostnames={'Value': True})

    # Subnet
    subnet = vpc.create_subnet(CidrBlock=SUBNET_CIDR)
    logging.info(f"Subnet created: {subnet.id}")

    # Internet Gateway and route table (for public access)
    igw = ec2_resource.create_internet_gateway()
    vpc.attach_internet_gateway(InternetGatewayId=igw.id)
    route_table = vpc.create_route_table()
    route_table.create_route(DestinationCidrBlock="0.0.0.0/0", GatewayId=igw.id)
    route_table.associate_with_subnet(SubnetId=subnet.id)

    return vpc, subnet

def create_security_group(vpc_id):
    logging.info("Creating Security Group...")
    sg = ec2_client.create_security_group(
        GroupName=SECURITY_GROUP_NAME,
        Description=SECURITY_GROUP_DESC,
        VpcId=vpc_id
    )
    sg_id = sg['GroupId']

    # Open PostgreSQL port
    ec2_client.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[{
            'IpProtocol': 'tcp',
            'FromPort': DB_PORT,
            'ToPort': DB_PORT,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }]
    )
    logging.info(f"Security group {sg_id} allows port {DB_PORT}")
    return sg_id

def create_db_subnet_group(subnet_id):
    subnet_group_name = "rds-subnet-group"
    logging.info(f"Creating DB Subnet Group {subnet_group_name}...")
    try:
        rds_client.create_db_subnet_group(
            DBSubnetGroupName=subnet_group_name,
            DBSubnetGroupDescription="Subnet group for PostgreSQL RDS",
            SubnetIds=[subnet_id]
        )
    except ClientError as e:
        logging.error(f"Could not create DB Subnet Group: {e}")
        return None
    return subnet_group_name

def create_postgres_rds(sg_id, subnet_group_name):
    logging.info(f"Creating PostgreSQL RDS instance {DB_IDENTIFIER}...")
    try:
        response = rds_client.create_db_instance(
            DBName=DB_NAME,
            DBInstanceIdentifier=DB_IDENTIFIER,
            AllocatedStorage=20,  # GB
            DBInstanceClass=DB_INSTANCE_CLASS,
            Engine=DB_ENGINE,
            MasterUsername=DB_USERNAME,
            MasterUserPassword=DB_PASSWORD,
            VpcSecurityGroupIds=[sg_id],
            DBSubnetGroupName=subnet_group_name,
            PubliclyAccessible=True,
            Port=DB_PORT,
            MultiAZ=False
        )
        logging.info("RDS creation initiated. Waiting until available...")
        waiter = rds_client.get_waiter('db_instance_available')
        waiter.wait(DBInstanceIdentifier=DB_IDENTIFIER)
        db_instance = rds_client.describe_db_instances(DBInstanceIdentifier=DB_IDENTIFIER)['DBInstances'][0]
        endpoint = db_instance['Endpoint']['Address']
        logging.info(f"PostgreSQL RDS is available at {endpoint}:{DB_PORT}")
        return endpoint
    except ClientError as e:
        logging.error(f"Error creating RDS instance: {e}")
        return None

# ================= MAIN =================
def main():
    vpc, subnet = create_vpc()
    sg_id = create_security_group(vpc.id)
    subnet_group_name = create_db_subnet_group(subnet.id)
    if subnet_group_name:
        endpoint = create_postgres_rds(sg_id, subnet_group_name)
        if endpoint:
            logging.info(f"Connect to PostgreSQL using: psql -h {endpoint} -U {DB_USERNAME} -d {DB_NAME}")

if __name__ == "__main__":
    main()
