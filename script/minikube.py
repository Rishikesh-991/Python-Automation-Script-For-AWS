#!/usr/bin/env python3
import subprocess
import sys
import logging

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def run(cmd, check=True):
    """Run a shell command and optionally exit on failure"""
    logging.info(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        logging.error(f"Command failed: {cmd}")
        logging.error(result.stderr)
        sys.exit(1)
    return result.stdout.strip()

def install_dependencies():
    """Install Docker, Kubectl, Minikube"""
    logging.info("Updating system packages...")
    run("sudo apt update && sudo apt install -y curl apt-transport-https ca-certificates gnupg lsb-release")

    logging.info("Installing Docker...")
    run("sudo apt install -y docker.io")
    run("sudo systemctl enable --now docker")

    logging.info("Installing kubectl...")
    run("curl -LO https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl")
    run("sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl")
    run("rm kubectl")

    logging.info("Installing Minikube...")
    run("curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64")
    run("sudo install minikube-linux-amd64 /usr/local/bin/minikube")
    run("rm minikube-linux-amd64")

def start_minikube():
    """Start Minikube cluster"""
    logging.info("Starting Minikube cluster...")
    run("minikube start --driver=docker")
    logging.info("Minikube started successfully.")
    run("kubectl config use-context minikube")
    logging.info("Kubectl context set to Minikube.")

def main():
    install_dependencies()
    start_minikube()
    logging.info("Minikube is running. Test with 'kubectl get nodes'.")

if __name__ == "__main__":
    main()
