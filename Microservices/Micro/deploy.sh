#!/bin/bash

# Initialize Terraform
terraform init

# Generate and show an execution plan
terraform plan

# Apply the changes to deploy infrastructure
terraform apply -auto-approve
