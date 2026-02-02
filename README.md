# AWS Automation with Python

## Overview
This repository contains Python scripts that **fully automate the creation and management of AWS resources**. Using the official AWS SDK for Python (**Boto3**), these scripts allow you to programmatically provision, configure, and manage AWS services such as EC2, S3, IAM, RDS, Lambda, and more.  

Automation helps save time, reduce errors, and ensure consistent cloud environments.

---

## Features
- **Automate EC2 Instances**: Launch, stop, start, and terminate EC2 instances with custom configurations.
- **S3 Bucket Management**: Create, delete, and manage S3 buckets and objects.
- **IAM Users and Roles**: Create and assign IAM users, groups, and roles automatically.
- **RDS Automation**: Create, delete, and configure RDS databases.
- **CloudFormation Integration**: Deploy AWS stacks programmatically.
- **Lambda Functions**: Automate creation and deployment of AWS Lambda functions.
- **Security Automation**: Automatically attach policies and configure security groups.
- **Modular & Configurable**: Scripts can be customized for different AWS accounts and regions.

---

## Prerequisites
Before using these scripts, make sure you have:

- Python 3.7+ installed
- AWS account with proper permissions
- AWS CLI installed and configured:
```bash
aws configure
make chnages