# AWS Automation & EKS Deployment – Step-by-Step Guide

This guide provides **exact copy-paste steps** to install, configure, and deploy AWS infrastructure, EKS, applications, and monitoring.

---

## STEP 1: Clone Repository

```bash
git clone https://github.com/Rishikesh-991/Python-Automation-Script-For-AWS.git
cd Python-Automation-Script-For-AWS
```

---

## STEP 2: Install System Requirements

### Install Python dependencies

```bash
pip install -r requirements.txt
```

### Install AWS CLI

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscliv2.zip
unzip awscliv2.zip
sudo ./aws/install
```

Verify:

```bash
aws --version
```

### Install kubectl

```bash
curl -LO https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

Verify:

```bash
kubectl version --client
```

---

## STEP 3: Configure AWS Credentials

```bash
aws configure
```

Enter:

```
AWS Access Key ID     : <YOUR_KEY>
AWS Secret Access Key : <YOUR_SECRET>
Default region name   : us-east-1
Default output format : json
```

---

## STEP 4: Configure Environment File

```bash
cp .env.example .env
nano .env
```

Update values:

- `AWS_REGION`
- `CLUSTER_NAME`
- `DB_NAME`
- `DB_USERNAME`
- `DB_PASSWORD`
- `DOCKER_IMAGE_NAME`

Save and exit.

---

## STEP 5: Create VPC and EC2

```bash
python ec2-and-vpc.py
```

---

## STEP 6: Create Security Groups

```bash
python securtity-group.py
```

---

## STEP 7: Attach IAM Role to EC2

```bash
python ec2-IAM-role-security-group.py
```

---

## STEP 8: Create IAM Roles & Policies

```bash
python IAM-roles.py
```

---

## STEP 9: Create S3 Bucket

```bash
python s3-bucket.py
```

---

## STEP 10: Create PostgreSQL RDS

```bash
python create-postgress.py
```

---

## STEP 11: Push Docker Image to AWS ECR

```bash
python docker-ecr.py
```

---

## STEP 12: Push Docker Image to Docker Hub

```bash
python docker-hub.py
```

---

## STEP 13: Create EKS Cluster

```bash
python eks.py
```

Update kubeconfig:

```bash
aws eks update-kubeconfig --region us-east-1 --name <CLUSTER_NAME>
```

Verify nodes:

```bash
kubectl get nodes
```

---

## STEP 14: Deploy Application to EKS

```bash
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/nginx-deployment.yml
```

Check:

```bash
kubectl get pods
kubectl get svc
```

---

## STEP 15: Deploy Prometheus Monitoring

```bash
kubectl apply -f k8s/prometheus-service.yml
```

---

## STEP 16: Deploy Grafana Dashboard

```bash
kubectl apply -f k8s/grafana-service.yml
```

Verify:

```bash
kubectl get pods
```

---

## STEP 17: Access Grafana

```bash
kubectl port-forward svc/grafana 3000:3000
```

Open browser:

```
http://localhost:3000
```

Login:

```
Username: admin
Password: admin
```

---

## STEP 18: Deploy CloudFormation Stack (Optional)

```bash
python cloud-formation.py
```

---

## STEP 19: Deploy Lambda Function

```bash
python Lambda-function.py
```

---

## STEP 20: Health Check

```bash
python ecommerce_healthcheck.py
```

---

## STEP 21: Local Kubernetes Testing (Optional)

### Kind Cluster

```bash
python kind-cluster.py
python kind-prometheus.py
python kind-grafana.py
```

### Minikube on EC2

```bash
python minikube.py
```

---

## STEP 22: Cleanup (VERY IMPORTANT)

```bash
kubectl delete -f k8s/
```

Manually delete from AWS Console:

- EKS Cluster
- EC2 Instances
- RDS
- Load Balancers
- S3 Buckets

---

## DONE ✅

AWS Infrastructure, EKS, Applications, and Monitoring successfully deployed.

---

## Author

**Rishikesh-991** 🚀


