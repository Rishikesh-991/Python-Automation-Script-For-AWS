# AWS Automation with Python 🚀

[![Python](https://img.shields.io/badge/python-3.7+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Scripts & Functionality](#scripts--functionality)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Kubernetes & EKS Deployment](#kubernetes--eks-deployment)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Overview
This repository provides **Python-based automation for AWS infrastructure and Kubernetes deployments**.  
Using **Boto3**, Docker, and Kubernetes manifests, it enables **end-to-end cloud automation**, including:

- EC2, S3, IAM, Lambda, RDS
- Docker image automation (ECR & Docker Hub)
- CloudFormation stack deployment
- Kubernetes / EKS cluster provisioning
- Monitoring with **Prometheus** and **Grafana**
- Security automation using IAM roles and Security Groups

This project is designed to reduce manual effort, improve consistency, and speed up cloud deployments.

---

## Features

| Feature | Description |
|-------|-------------|
| **EC2 Automation** | Create, start, stop, and terminate EC2 instances with IAM roles and security groups |
| **S3 Bucket Management** | Create and manage S3 buckets and permissions |
| **IAM Management** | Automate IAM users, roles, and policies |
| **RDS Automation** | Provision PostgreSQL RDS databases |
| **Lambda Functions** | Create and monitor AWS Lambda functions |
| **Docker Automation** | Push images to AWS ECR and Docker Hub |
| **CloudFormation** | Deploy and monitor CloudFormation stacks |
| **EKS & Kubernetes** | Deploy EKS clusters, applications, and monitoring tools |
| **Monitoring** | Prometheus & Grafana setup on EKS / Kind |
| **Security Automation** | Security groups and IAM role attachment |

---

## Scripts & Functionality

| Script / File | Description |
|--------------|-------------|
| `ec2-and-vpc.py` | EC2 instance and VPC automation |
| `ec2-IAM-role-security-group.py` | EC2 with IAM roles and security groups |
| `s3-bucket.py` | S3 bucket creation and management |
| `IAM-roles.py` | IAM users, roles, and policies |
| `Lambda-function.py` | Lambda deployment and monitoring |
| `cloud-formation.py` | CloudFormation stack automation |
| `create-postgress.py` | PostgreSQL RDS creation |
| `docker-ecr.py` | Push Docker images to AWS ECR |
| `docker-hub.py` | Push Docker images to Docker Hub |
| `eks.py` | EKS cluster creation |
| `eks-deployment.py` | Deploy workloads to EKS |
| `minikube.py` | Minikube setup on EC2 |
| `kind-cluster.py` | Local Kubernetes cluster using Kind |
| `kind-grafana.py` | Grafana deployment on Kind |
| `kind-prometheus.py` | Prometheus deployment on Kind |
| `securtity-group.py` | Security group automation |
| `ecommerce_healthcheck.py` | Sample application health check |

### Kubernetes YAML Files (`/k8s`)
- `deployment.yml` – Application deployment  
- `nginx-deployment.yml` – NGINX deployment  
- `eks-deployment.yml` – EKS workload deployment  
- `prometheus-service.yml` – Prometheus service  
- `grafana-service.yml` – Grafana service  

---

## Prerequisites
Ensure the following are installed and configured:

- **Python 3.7+**
- **AWS Account** with required permissions
- **AWS CLI**
```bash
aws configure
