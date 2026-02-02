#!/usr/bin/env python3
import boto3
import subprocess
import time
import logging
import os

# ================= CONFIG =================
REGION = "us-east-1"
EKS_CLUSTER_NAME = "python-eks-cluster"
NODEGROUP_NAME = "python-eks-nodegroup"
NODE_ROLE_ARN = "<EKS_NODE_ROLE_ARN>"  # Replace with your IAM NodeRole
DOCKER_IMAGE = "<DOCKER_USERNAME>/python-nginx:latest"
K8S_DEPLOYMENT_FILE = "k8s-deployment.yaml"
AWS_ACCOUNT_ID = "<AWS_ACCOUNT_ID>"  # Needed for ECR
LOG_FILE = "/tmp/eks_deploy.log"

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)

# ================= AWS CLIENTS =================
eks_client = boto3.client("eks", region_name=REGION)
ec2_client = boto3.client("ec2", region_name=REGION)
ecr_client = boto3.client("ecr", region_name=REGION)

# ================= FUNCTIONS =================
def run(cmd):
    """Run shell command"""
    logging.info(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        logging.error(f"Command failed: {cmd}")
        exit(1)

def create_eks_cluster():
    """Create EKS cluster"""
    logging.info(f"Creating EKS cluster {EKS_CLUSTER_NAME}...")
    try:
        eks_client.create_cluster(
            name=EKS_CLUSTER_NAME,
            version='1.27',
            roleArn=NODE_ROLE_ARN,
            resourcesVpcConfig={
                'subnetIds': get_default_subnets(),
                'endpointPublicAccess': True
            }
        )
        logging.info("Cluster creation started. Waiting until ACTIVE...")
        waiter = eks_client.get_waiter('cluster_active')
        waiter.wait(name=EKS_CLUSTER_NAME)
        logging.info(f"EKS Cluster {EKS_CLUSTER_NAME} is ACTIVE")
    except eks_client.exceptions.ResourceInUseException:
        logging.info("Cluster already exists. Skipping creation.")

def get_default_subnets():
    """Get default VPC subnets"""
    vpcs = ec2_client.describe_vpcs(Filters=[{'Name':'isDefault','Values':['true']}])['Vpcs']
    if not vpcs:
        logging.error("No default VPC found")
        exit(1)
    vpc_id = vpcs[0]['VpcId']
    subnets = ec2_client.describe_subnets(Filters=[{'Name':'vpc-id','Values':[vpc_id]}])['Subnets']
    return [subnet['SubnetId'] for subnet in subnets]

def build_and_push_docker_image():
    """Build Docker image and push to Docker Hub"""
    logging.info("Building Docker image...")
    run(f"docker build -t {DOCKER_IMAGE} .")
    logging.info("Pushing Docker image...")
    run(f"docker push {DOCKER_IMAGE}")

def update_kubeconfig():
    """Update kubeconfig to access EKS"""
    logging.info("Updating kubeconfig...")
    run(f"aws eks update-kubeconfig --name {EKS_CLUSTER_NAME} --region {REGION}")

def deploy_k8s_stack():
    """Deploy Nginx + Prometheus + Grafana"""
    logging.info("Deploying Kubernetes manifests...")
    # Apply Nginx deployment
    run(f"kubectl apply -f {K8S_DEPLOYMENT_FILE}")
    # Helm repo add
    run("helm repo add prometheus-community https://prometheus-community.github.io/helm-charts")
    run("helm repo add grafana https://grafana.github.io/helm-charts")
    run("helm repo update")
    # Install Prometheus
    run("helm install prometheus prometheus-community/prometheus --namespace monitoring --create-namespace")
    # Install Grafana
    run("helm install grafana grafana/grafana --namespace monitoring")

def main():
    create_eks_cluster()
    build_and_push_docker_image()
    update_kubeconfig()
    deploy_k8s_stack()
    logging.info("EKS + Nginx + Prometheus + Grafana deployment completed!")

if __name__ == "__main__":
    main()
