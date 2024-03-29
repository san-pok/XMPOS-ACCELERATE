#!/bin/bash

# Navigate to the Terraform directory, assuming the script is run from the project root
cd terraform

# Make sure Terraform is initialized and updated
terraform init
terraform apply -auto-approve

# Extract outputs and write/update them in the .env file in the backend directory
echo "AWS_REGION=$(terraform output -raw region)" > ../backend/.env
echo "COGNITO_USER_POOL_ID=$(terraform output -raw cognito_user_pool_id)" >> ../backend/.env
echo "COGNITO_APP_CLIENT_ID=$(terraform output -raw cognito_user_pool_client_id)" >> ../backend/.env
echo "COGNITO_APP_CLIENT_SECRET=$(terraform output -raw cognito_user_pool_client_secret)" >> ../backend/.env

# Navigate back to the project root
cd ..
