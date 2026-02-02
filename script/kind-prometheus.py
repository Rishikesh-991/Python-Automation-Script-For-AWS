#!/usr/bin/env python3
import subprocess
import sys
import logging
import time

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ================= FUNCTIONS =================
def run(cmd, check=True):
    """Run a shell command and optionally exit on failure"""
    logging.info(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        logging.error(f"Command failed: {cmd}")
        logging.error(result.stderr)
        sys.exit(1)
    return result.stdout.strip()

def create_kind_cluster(cluster_name="kind-prometheus-cluster"):
    """Create a kind cluster"""
    logging.info(f"Creating kind cluster: {cluster_name}")
    run(f"kind create cluster --name {cluster_name}")

    logging.info(f"Cluster '{cluster_name}' created. Checking nodes...")
    nodes = run("kubectl get nodes")
    logging.info(f"Nodes:\n{nodes}")

def deploy_prometheus():
    """Deploy Prometheus on the kind cluster"""
    logging.info("Adding Prometheus community helm repo...")
    run("helm repo add prometheus-community https://prometheus-community.github.io/helm-charts")
    run("helm repo update")

    logging.info("Creating 'monitoring' namespace...")
    run("kubectl create namespace monitoring")

    logging.info("Installing kube-prometheus-stack via Helm...")
    run("helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring")

    logging.info("Waiting for Prometheus pods to be ready...")
    # Wait until all pods are running (timeout: 3 min)
    for _ in range(30):
        pods_status = run("kubectl get pods -n monitoring --no-headers")
        if pods_status and all('Running' in line or 'Completed' in line for line in pods_status.splitlines()):
            logging.info("All Prometheus pods are running.")
            break
        logging.info("Waiting 10 seconds for pods to be ready...")
        time.sleep(10)
    else:
        logging.warning("Some Prometheus pods are not running yet. Check manually with 'kubectl get pods -n monitoring'.")

    logging.info("Prometheus deployed successfully. Access services with:")
    run("kubectl get svc -n monitoring")

# ================= MAIN =================
def main():
    create_kind_cluster()
    deploy_prometheus()

if __name__ == "__main__":
    main()
