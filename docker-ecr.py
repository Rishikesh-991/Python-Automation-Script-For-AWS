#!/usr/bin/env python3
import boto3
import subprocess
import docker
import os
import time
from botocore.exceptions import ClientError

# ================= CONFIG =================
REGION = "us-east-1"
REPOSITORY_NAME = "my-app-repo"
IMAGE_TAG = "latest"
ECR_URI = None  # Will be generated after the repository is created
DOCKERFILE_PATH = "./"  # Path to the Dockerfile
IMAGE_NAME = "my-app"  # Name of the Docker image
DOCKER_CONTEXT = "./"  # Path to the build context for the Docker image

# ================= AWS CLIENTS =================
ecr_client = boto3.client("ecr", region_name=REGION)
docker_client = docker.from_env()

# ================= FUNCTIONS =================
def create_ecr_repository():
    """Create an ECR repository if it doesn't exist."""
    global ECR_URI
    try:
        response = ecr_client.describe_repositories(repositoryNames=[REPOSITORY_NAME])
        ECR_URI = response["repositories"][0]["repositoryUri"]
        print(f"Repository {REPOSITORY_NAME} already exists. Using URI: {ECR_URI}")
    except ClientError:
        print(f"Repository {REPOSITORY_NAME} not found. Creating a new repository.")
        response = ecr_client.create_repository(repositoryName=REPOSITORY_NAME)
        ECR_URI = response["repository"]["repositoryUri"]
        print(f"Created repository {REPOSITORY_NAME}. URI: {ECR_URI}")
    return ECR_URI

def build_docker_image():
    """Build the Docker image from the Dockerfile."""
    print(f"Building Docker image {IMAGE_NAME}:{IMAGE_TAG}...")
    try:
        image, build_logs = docker_client.images.build(path=DOCKER_CONTEXT, tag=f"{IMAGE_NAME}:{IMAGE_TAG}")
        print(f"Built Docker image: {IMAGE_NAME}:{IMAGE_TAG}")
        return image
    except Exception as e:
        print(f"Error building Docker image: {e}")
        raise

def login_to_ecr():
    """Login to ECR using AWS CLI."""
    print("Logging into Amazon ECR...")
    try:
        login_cmd = f"aws ecr get-login-password --region {REGION} | docker login --username AWS --password-stdin {ECR_URI}"
        subprocess.run(login_cmd, shell=True, check=True)
        print("Logged into ECR successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error logging into ECR: {e}")
        raise

def tag_and_push_image(image):
    """Tag and push the Docker image to ECR."""
    print(f"Tagging Docker image {IMAGE_NAME}:{IMAGE_TAG} for ECR...")
    image.tag(f"{ECR_URI}:{IMAGE_TAG}")

    print(f"Pushing image {IMAGE_NAME}:{IMAGE_TAG} to ECR...")
    try:
        push_logs = docker_client.images.push(f"{ECR_URI}:{IMAGE_TAG}", stream=True, decode=True)
        for log in push_logs:
            print(log)
        print(f"Image {IMAGE_NAME}:{IMAGE_TAG} pushed successfully to {ECR_URI}.")
    except Exception as e:
        print(f"Error pushing Docker image to ECR: {e}")
        raise

def run_docker_container():
    """Run the Docker container."""
    print(f"Running Docker container from {ECR_URI}:{IMAGE_TAG}...")
    try:
        container = docker_client.containers.run(
            f"{ECR_URI}:{IMAGE_TAG}",
            detach=True,  # Run in background
            ports={'8080/tcp': 8080}  # Expose port 8080
        )
        print(f"Docker container {container.id} is running.")
        return container
    except Exception as e:
        print(f"Error running Docker container: {e}")
        raise

# ================= MAIN =================
def main():
    create_ecr_repository()  # Create the ECR repository if not exists
    build_docker_image()  # Build the Docker image
    login_to_ecr()  # Log into ECR
    tag_and_push_image(docker_client.images.get(f"{IMAGE_NAME}:{IMAGE_TAG}"))  # Push image to ECR
    run_docker_container()  # Run the container

if __name__ == "__main__":
    main()
