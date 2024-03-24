from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import logging
import datetime


logging.basicConfig(level=logging.INFO)




app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:8000"}})


def generate_ssh_key(user_input):
    # Use user_input in some form if needed, like a passphrase or to generate a unique key pair per user input.
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key().public_bytes(
        serialization.Encoding.OpenSSH,
        serialization.PublicFormat.OpenSSH
    )
    # Note: For production use, securely store the private key if it's ever needed again.
    return public_key.decode('utf-8')

@app.route('/deploy', methods=['POST'])
def deploy_instance():
    data = request.json
    ssh_key_user_input = data.get('sshKey', 'default')  # Use 'default' if 'sshKey' not provided

    # Generate SSH key based on the user input
    public_ssh_key = generate_ssh_key(ssh_key_user_input)

    # Setup environment variables for Terraform
    os.environ['TF_VAR_ssh_key'] = public_ssh_key
    os.environ['TF_VAR_instance_name'] = data.get('instanceName', 'XMOPSTeamTwo')
    os.environ['TF_VAR_bundle_id'] = data.get('instanceSize', 'nano_3_2')
    os.environ['TF_VAR_key_pair_name'] = 'my_key_pair'

    terraform_dir = "../terraform"
    deployment_status = "failed"  # Assume failure by default

    try:
        # Initialize Terraform
        init_output = subprocess.run(["terraform", "init"], cwd=terraform_dir, capture_output=True, text=True)
        print(init_output.stdout)
        if init_output.returncode != 0:
            print(init_output.stderr)
            raise Exception('Error initializing Terraform')

        # Plan Terraform
        plan_output = subprocess.run(["terraform", "plan"], cwd=terraform_dir, capture_output=True, text=True)
        print(plan_output.stdout)
        if plan_output.returncode != 0:
            print(plan_output.stderr)
            raise Exception('Error planning with Terraform')

        # Apply Terraform
        apply_output = subprocess.run(["terraform", "apply", "-auto-approve"], cwd=terraform_dir, capture_output=True, text=True)
        print(apply_output.stdout)
        if apply_output.returncode != 0:
            print(apply_output.stderr)
            raise Exception('Error applying Terraform')

        # Update the deployment status to 'success' after successful Terraform apply
        deployment_status = "success"

        # Parse outputs
        output = subprocess.run(["terraform", "output", "-json"], cwd=terraform_dir, capture_output=True, text=True)
        outputs = json.loads(output.stdout)
        wordpressInstallationUrl = outputs.get('wordpress_setup_url', {}).get('value', '')

        # Save deployment status to S3
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_deployment_to_s3(data.get('instanceName', 'XMOPSTeamTwo'), timestamp, deployment_status)

        return jsonify({'message': 'Lightsail deployed successfully!', 'wordpressInstallationUrl': wordpressInstallationUrl})

    except Exception as e:
        # Log the error and save the 'failed' status if an exception is caught
        print(f"Deployment failed: {str(e)}")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "success"  # or "failed" based on your deployment outcome
        save_deployment_to_s3(instance_name, timestamp, status)


        return jsonify({'message': 'Error deploying Lightsail instance', 'error': str(e)}), 500























# code for s3 starts

# Your AWS S3 bucket name
BUCKET_NAME = 'xmops-team2-abs'

# Initialize boto3 client
s3_client = boto3.client('s3')

def create_bucket_if_not_exists(bucket_name):
    """
    Create an S3 bucket in a specified region.
    """
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        logging.info(f"Bucket {bucket_name} already exists.")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            try:
                # Since your AWS region is ap-southeast-2, set LocationConstraint explicitly
                location = {'LocationConstraint': 'ap-southeast-2'}
                s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
                logging.info(f"Bucket {bucket_name} created in ap-southeast-2.")
            except ClientError as e:
                logging.error("Failed to create bucket: %s", e)
                raise
        else:
            logging.error("Failed to check bucket: %s", e)
            raise

def save_deployment_to_s3(instance_name, timestamp, status):
    history_file_key = 'deployment_history.json'
    # Fetch the current deployment history if it exists
    try:
        current_history = s3_client.get_object(Bucket=BUCKET_NAME, Key=history_file_key)
        deployment_history = json.loads(current_history['Body'].read().decode('utf-8'))
    except s3_client.exceptions.NoSuchKey:
        deployment_history = []  # Initialize if the history file does not exist
    
    # Append the new deployment record
    deployment_history.append({
        'timestamp': timestamp,
        'status': status
    })
    
    # Update the S3 object with the new history
    s3_client.put_object(Body=json.dumps(deployment_history), Bucket=BUCKET_NAME, Key=history_file_key)




@app.route('/fetch-deployment-history', methods=['GET'])
def get_deployment_history():
    history_file_key = 'deployment_history.json'
    try:
        # Attempt to fetch the deployment history JSON file from the S3 bucket
        obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=history_file_key)
        deployment_history = json.loads(obj['Body'].read().decode('utf-8'))
        
        # Return the content of the deployment history file as JSON
        return jsonify(deployment_history)
    except s3_client.exceptions.NoSuchKey:
        # If the deployment history file does not exist, return an empty list
        print("No deployment history file found.")
        return jsonify([]), 404
    except Exception as e:
        # Handle other exceptions
        print(f"Error fetching deployment history: {e}")
        return jsonify({'error': 'Error fetching deployment history'}), 500










if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
