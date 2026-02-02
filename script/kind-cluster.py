#!/usr/bin/env python3
import subprocess
import sys
import logging

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ================= FUNCTIONS =================
def run(cmd):
    """Run a shell command and exit on failure"""
    logging.info(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Command failed: {cmd}")
        logging.error(result.stderr)
        sys.exit(1)
    return result.stdout.strip()

def create_kind_cluster(cluster_name="my-kind-cluster"):
    """Create a kind cluster"""
    # Step 1: Create cluster
    logging.info(f"Creating kind cluster: {cluster_name}")
    run(f"kind create cluster --name {cluster_name}")

    # Step 2: Check cluster info
    logging.info(f"Checking cluster info for {cluster_name}")
    info = run(f"kubectl cluster-info --context kind-{cluster_name}")
    logging.info(f"Cluster Info:\n{info}")

    # Step 3: List nodes
    nodes = run(f"kubectl get nodes")
    logging.info(f"Cluster Nodes:\n{nodes}")

# ================= MAIN =================
def main():
    create_kind_cluster()

if __name__ == "__main__":
    main()
