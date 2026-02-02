#!/usr/bin/env python3
import boto3
import logging
from botocore.exceptions import ClientError
import time

# ================= CONFIG =================
REGION = "us-east-1"
STACK_NAME = "MyTestStack"
TEMPLATE_FILE = "/path/to/template.yaml"  # CloudFormation template path
PARAMETERS = [
    # Example parameter format if your template has Parameters
    # {"ParameterKey": "InstanceType", "ParameterValue": "t2.micro"},
]

LOG_FILE = "/tmp/cloudformation.log"

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)

# ================= AWS CLIENT =================
cf_client = boto3.client("cloudformation", region_name=REGION)

# ================= FUNCTIONS =================

def load_template(file_path):
    with open(file_path, "r") as f:
        return f.read()

def stack_exists(stack_name):
    try:
        cf_client.describe_stacks(StackName=stack_name)
        return True
    except ClientError as e:
        if "does not exist" in str(e):
            return False
        else:
            logging.error(f"Error checking stack existence: {e}")
            return False

def create_stack(stack_name, template_body, parameters):
    try:
        logging.info(f"Creating stack {stack_name}...")
        cf_client.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=parameters,
            Capabilities=['CAPABILITY_NAMED_IAM', 'CAPABILITY_AUTO_EXPAND']
        )
        wait_for_completion(stack_name, "create")
    except ClientError as e:
        logging.error(f"Failed to create stack: {e}")

def update_stack(stack_name, template_body, parameters):
    try:
        logging.info(f"Updating stack {stack_name}...")
        cf_client.update_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=parameters,
            Capabilities=['CAPABILITY_NAMED_IAM', 'CAPABILITY_AUTO_EXPAND']
        )
        wait_for_completion(stack_name, "update")
    except ClientError as e:
        if "No updates are to be performed" in str(e):
            logging.info("Stack is already up-to-date")
        else:
            logging.error(f"Failed to update stack: {e}")

def delete_stack(stack_name):
    try:
        logging.info(f"Deleting stack {stack_name}...")
        cf_client.delete_stack(StackName=stack_name)
        wait_for_completion(stack_name, "delete")
    except ClientError as e:
        logging.error(f"Failed to delete stack: {e}")

def wait_for_completion(stack_name, action):
    logging.info(f"Waiting for stack {stack_name} to {action}...")
    waiter = None
    if action == "create":
        waiter = cf_client.get_waiter('stack_create_complete')
    elif action == "update":
        waiter = cf_client.get_waiter('stack_update_complete')
    elif action == "delete":
        waiter = cf_client.get_waiter('stack_delete_complete')

    elif action == "update":
        waiter = cf_client.get_waiter('stack_update_complete')
    else:
        logging.error(f"Unknown action {action}")
        return

    try:
        waiter.wait(StackName=stack_name)
        logging.info(f"Stack {stack_name} {action}d successfully!")
    except ClientError as e:
        logging.error(f"Error while waiting for stack {action}: {e}")

# ================= MAIN =================
def main():
    template_body = load_template(TEMPLATE_FILE)

    if stack_exists(STACK_NAME):
        logging.info(f"Stack {STACK_NAME} already exists. Updating...")
        update_stack(STACK_NAME, template_body, PARAMETERS)
    else:
        create_stack(STACK_NAME, template_body, PARAMETERS)

    # Uncomment to delete stack
    # delete_stack(STACK_NAME)

if __name__ == "__main__":
    main()
