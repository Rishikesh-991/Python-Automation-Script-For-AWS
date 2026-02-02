# AWS Automation with Python

## Overview
This repository contains **Python scripts that fully automate AWS resource provisioning and management**. Using **Boto3** (the official AWS SDK for Python), these scripts allow you to programmatically create, configure, and manage AWS services such as:

- EC2 Instances
- S3 Buckets
- IAM Users, Roles, and Policies
- RDS Databases (PostgreSQL)
- Lambda Functions
- EKS Clusters
- Docker Images (ECR & Docker Hub)
- Security Groups
- CloudFormation Stacks
- Minikube/Kubernetes Monitoring (Grafana, Prometheus)

Automation reduces manual errors, ensures consistency, and saves time when managing cloud resources.

---

## Features

| Feature | Description |
|---------|-------------|
| **EC2 Automation** | Launch, stop, start, and terminate EC2 instances, configure IAM roles and security groups. |
| **S3 Bucket Management** | Create and delete S3 buckets, manage objects and permissions. |
| **IAM Management** | Automate creation and assignment of IAM users, roles, and policies. |
| **RDS Automation** | Create and manage PostgreSQL databases in AWS. |
| **Lambda Functions** | Deploy, configure, and monitor AWS Lambda functions. |
| **EKS & Kubernetes** | Automate EKS cluster deployment, including monitoring with Grafana and Prometheus. |
| **Docker Automation** | Push Docker images to AWS ECR or Docker Hub automatically. |
| **CloudFormation** | Deploy AWS stacks programmatically and monitor their status. |
| **Security** | Automate security group creation and policy attachment. |

---

## Prerequisites
Before running these scripts, ensure you have:

- **Python 3.7+**
- An **AWS account** with proper permissions
- **AWS CLI** installed and configured:  
```bash
aws configure
