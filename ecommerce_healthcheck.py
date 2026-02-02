#!/usr/bin/env python3
import boto3
import time
import logging

# ================= CONFIG =================
REGION = "us-east-1"
CLUSTER_NAME = "my-eks-cluster"
NODEGROUP_NAME = "my-eks-nodes"
NODE_ROLE_ARN = "arn:aws:iam::<account_id>:role/EKSNodeRole"  # Pre-created IAM role for nodes
SUBNET_IDS = ["subnet-xxxxxx", "subnet-yyyyyy"]  # VPC subnets
INSTANCE_TYPES = ["t3.medium"]
DESIRED_NODES = 2
MAX_NODES = 3
MIN_NODES = 1

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ================= AWS CLIENT =================
eks_client = boto3.client("eks", region_name=REGION)

# ================= FUNCTIONS =================
def create_eks_cluster():
    """Create an EKS cluster"""
    logging.info(f"Creating EKS cluster {CLUSTER_NAME}...")
    response = eks_client.create_cluster(
        name=CLUSTER_NAME,
        version="1.28",
        roleArn=NODE_ROLE_ARN,
        resourcesVpcConfig={
            "subnetIds": SUBNET_IDS,
            "endpointPublicAccess": True
        }
    )
    logging.info("EKS cluster creation started...")
    wait_for_cluster(CLUSTER_NAME)
    logging.info(f"EKS cluster {CLUSTER_NAME} is ACTIVE")
    create_nodegroup()

def wait_for_cluster(cluster_name):
    """Wait until cluster is ACTIVE"""
    while True:
        response = eks_client.describe_cluster(name=cluster_name)
        status = response['cluster']['status']
        logging.info(f"Cluster status: {status}")
        if status == "ACTIVE":
            break
        time.sleep(30)

def create_nodegroup():
    """Create managed node group"""
    logging.info(f"Creating Node Group {NODEGROUP_NAME}...")
    eks_client.create_nodegroup(
        clusterName=CLUSTER_NAME,
        nodegroupName=NODEGROUP_NAME,
        scalingConfig={
            "minSize": MIN_NODES,
            "maxSize": MAX_NODES,
            "desiredSize": DESIRED_NODES
        },
        subnets=SUBNET_IDS,
        instanceTypes=INSTANCE_TYPES,
        nodeRole=NODE_ROLE_ARN
    )
    logging.info("Node group creation started...")
    wait_for_nodegroup(NODEGROUP_NAME)

def wait_for_nodegroup(nodegroup_name):
    """Wait until node group is ACTIVE"""
    while True:
        response = eks_client.describe_nodegroup(clusterName=CLUSTER_NAME, nodegroupName=nodegroup_name)
        status = response['nodegroup']['status']
        logging.info(f"Node group status: {status}")
        if status == "ACTIVE":
            break
        time.sleep(30)
    logging.info("Node group is ACTIVE")

# ================= MAIN =================
if __name__ == "__main__":
    create_eks_cluster()
    logging.info("EKS cluster and node group setup complete.")                  



            