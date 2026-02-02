#!/usr/bin/env python3
import subprocess
import sys
import logging
import time
import threading
import signal

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

def create_kind_cluster(cluster_name="kind-monitoring-cluster"):
    """Create a kind cluster"""
    logging.info(f"Creating kind cluster: {cluster_name}")
    run(f"kind create cluster --name {cluster_name}")
    logging.info("Cluster created. Nodes:")
    nodes = run("kubectl get nodes")
    logging.info(nodes)

def deploy_prometheus_grafana():
    """Deploy Prometheus + Grafana via kube-prometheus-stack"""
    logging.info("Adding Prometheus Helm repo...")
    run("helm repo add prometheus-community https://prometheus-community.github.io/helm-charts")
    run("helm repo update")

    logging.info("Creating 'monitoring' namespace...")
    run("kubectl create namespace monitoring")

    logging.info("Installing kube-prometheus-stack (Prometheus + Grafana)...")
    run("helm install monitoring-stack prometheus-community/kube-prometheus-stack -n monitoring")

    logging.info("Waiting for all monitoring pods to be ready (this may take a few minutes)...")
    for _ in range(30):  # check up to 5 minutes
        pods_status = run("kubectl get pods -n monitoring --no-headers")
        if pods_status and all('Running' in line or 'Completed' in line for line in pods_status.splitlines()):
            logging.info("All Prometheus/Grafana pods are running.")
            break
        logging.info("Pods not ready yet. Waiting 10 seconds...")
        time.sleep(10)
    else:
        logging.warning("Some pods are not ready. Check manually with 'kubectl get pods -n monitoring'")

def port_forward(namespace, service, local_port, remote_port):
    """Port-forward a Kubernetes service"""
    cmd = f"kubectl port-forward svc/{service} {local_port}:{remote_port} -n {namespace}"
    logging.info(f"Starting port-forward: {cmd}")

    # Start subprocess that stays alive
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    def stream_output():
        for line in proc.stdout:
            logging.info(line.decode().strip())
    threading.Thread(target=stream_output, daemon=True).start()
    
    return proc

def main():
    # Step 1: Create cluster and deploy monitoring stack
    create_kind_cluster()
    deploy_prometheus_grafana()

    # Step 2: Start port-forwards for Grafana and Prometheus
    grafana_proc = port_forward("monitoring", "monitoring-stack-grafana", 3000, 80)
    prometheus_proc = port_forward("monitoring", "monitoring-stack-kube-prometheus-prometheus", 9090, 9090)

    logging.info("Grafana available at http://localhost:3000")
    logging.info("Prometheus available at http://localhost:9090")
    logging.info("Press Ctrl+C to stop port-forwarding and exit.")

    # Handle Ctrl+C to terminate subprocesses
    def signal_handler(sig, frame):
        logging.info("Stopping port-forwards...")
        grafana_proc.terminate()
        prometheus_proc.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Keep main thread alive
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
