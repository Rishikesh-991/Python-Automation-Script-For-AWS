#!/usr/bin/env python3
import docker
import getpass

# ================= CONFIG =================
DOCKER_USERNAME = "your_dockerhub_username"   # Replace with your Docker Hub username
DOCKER_PASSWORD = None  # Will be prompted for security
IMAGE_NAME = "my-app"    # Local image name
IMAGE_TAG = "latest"     # Tag
DOCKERFILE_PATH = "./"   # Path to the Dockerfile
DOCKER_CONTEXT = "./"    # Build context

# ================= FUNCTIONS =================
def build_image():
    client = docker.from_env()
    print(f"Building Docker image {IMAGE_NAME}:{IMAGE_TAG}...")
    try:
        image, build_logs = client.images.build(
            path=DOCKER_CONTEXT,
            dockerfile=f"{DOCKERFILE_PATH}/Dockerfile",
            tag=f"{IMAGE_NAME}:{IMAGE_TAG}"
        )
        print(f"Built image: {IMAGE_NAME}:{IMAGE_TAG}")
        return client, image
    except Exception as e:
        print(f"Error building Docker image: {e}")
        raise

def login_to_dockerhub(client):
    global DOCKER_PASSWORD
    if not DOCKER_PASSWORD:
        DOCKER_PASSWORD = getpass.getpass(f"Enter Docker Hub password for {DOCKER_USERNAME}: ")
    print(f"Logging into Docker Hub as {DOCKER_USERNAME}...")
    try:
        client.login(username=DOCKER_USERNAME, password=DOCKER_PASSWORD)
        print("Login successful!")
    except Exception as e:
        print(f"Error logging into Docker Hub: {e}")
        raise

def tag_and_push_image(client, image):
    full_image_name = f"{DOCKER_USERNAME}/{IMAGE_NAME}:{IMAGE_TAG}"
    print(f"Tagging image {IMAGE_NAME}:{IMAGE_TAG} -> {full_image_name}")
    image.tag(full_image_name)
    
    print(f"Pushing image {full_image_name} to Docker Hub...")
    try:
        push_logs = client.images.push(DOCKER_USERNAME + "/" + IMAGE_NAME, tag=IMAGE_TAG, stream=True, decode=True)
        for log in push_logs:
            print(log)
        print(f"Image pushed successfully: {full_image_name}")
    except Exception as e:
        print(f"Error pushing image to Docker Hub: {e}")
        raise

def main():
    client, image = build_image()
    login_to_dockerhub(client)
    tag_and_push_image(client, image)

if __name__ == "__main__":
    main()
