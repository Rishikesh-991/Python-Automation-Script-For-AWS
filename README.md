# AWS Automation with Python

## Overview
This repository contains Python scripts that **fully automate AWS resource provisioning, Kubernetes deployments, and monitoring setups**. Using **Boto3** (AWS SDK for Python) and Kubernetes YAML/automation scripts, you can programmatically create, configure, and manage AWS services and EKS clusters, as well as deploy monitoring stacks like **Prometheus** and **Grafana**.

Automation reduces manual errors, ensures consistency, and saves time when managing cloud environments.

---

## Features

| Feature | Description |
|---------|-------------|
| **EC2 Automation** | Launch, stop, start, and terminate EC2 instances with IAM roles and security groups. |
| **S3 Bucket Management** | Create, delete, and manage S3 buckets and objects. |
| **IAM Management** | Automate creation of IAM users, roles, groups, and policies. |
| **RDS Automation** | Create and manage PostgreSQL databases on AWS. |
| **Lambda Functions** | Deploy, configure, and monitor AWS Lambda functions. |
| **Docker Automation** | Build and push Docker images to AWS ECR or Docker Hub. |
| **CloudFormation** | Deploy AWS stacks programmatically and monitor status. |
| **EKS & Kubernetes** | Automate EKS cluster deployment and management, including:
  - Deploying services (nginx, applications)
  - Deploying monitoring stacks (Prometheus, Grafana)
  - Deploying Minikube and Kind clusters for testing |
| **Security Automation** | Automatically create security groups and attach policies. |

---

## Prerequisites
Before running the scripts, ensure you have:

- Python 3.7+
- AWS account with proper permissions
- AWS CLI installed and configured:
```bash
aws configure
