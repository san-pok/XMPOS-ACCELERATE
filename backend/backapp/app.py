from flask import Flask, jsonify, request, redirect
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


highbucket_name = 'amirxmopbucket'
region_name = 'ap-southeast-2'
create_bucket_config = {
    'LocationConstraint': region_name
}

# Define the prefix
high_prefix = '/highly'
mono_prefix = '/mono'

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:8000"}})


@app.route(f'{high_prefix}/deploy', methods=['POST'])
def deploy_infrastructure():
    try:

        high_terraform_dir = "../../terraform/highly"

        # Initialize Terraform
        init_output = subprocess.run(["terraform", "init"], cwd=high_terraform_dir, capture_output=True, text=True)
        print(init_output.stdout)
        if init_output.returncode != 0:
            print(init_output.stderr)
            raise Exception('Error initializing Terraform')

        # Plan Terraform
        plan_output = subprocess.run(["terraform", "plan"], cwd=high_terraform_dir, capture_output=True, text=True)
        print(plan_output.stdout)
        if plan_output.returncode != 0:
            print(plan_output.stderr)
            raise Exception('Error planning with Terraform')

        return jsonify({'message': 'High deployed successfully!'})

    except Exception as e:
        # Log the error and save the 'failed' status if an exception is caught

        return jsonify({'message': 'Error deploying High instance', 'error': str(e)}), 500


@app.route(f'{high_prefix}/destroy', methods=['POST'])
def destroy_infrastructure():
    try:
        # Check if the destroy.sh script exists
        script_path = '../../terraform/highly/destroy.sh'
        print("Absolute path of script:", os.path.abspath(script_path))  # Debugging line
        if not os.path.exists(script_path):
            error_message = 'Error: destroy.sh script not found'
            return jsonify({'error': error_message}), 500

        # Execute the destroy.sh script
        subprocess.run([script_path], check=True)

        return jsonify({'message': 'Infrastructure destruction triggered successfully by py'}), 200
    except subprocess.CalledProcessError as e:
        error_message = f'Error destroying infrastructure by py: {e.stderr.decode()}'
        return jsonify({'error': error_message}), 500
    except Exception as e:
        error_message = f'Unknown error: {str(e)}'
        return jsonify({'error': error_message}), 500


@app.route(f'{high_prefix}/validate_form', methods=['POST'])
def validate_form():
    try:
        data = request.get_json()  # Get JSON data from request

        # Perform form validations
        errors = {}
        for key, value in data.items():
            # Check for required fields
            if not value.strip():
                errors[key] = 'This field is required'
            # Check for numeric fields
            if key.endswith('min_instances') or key.endswith('max_instances'):
                if not value.isdigit():
                    errors[key] = 'Please enter a numeric value'

        if errors:
            return jsonify({'error': 'Form validation failed', 'errors': errors}), 400
        else:

            # Check if the user chose to create a new key pair
            if 'new_key_pair_name' in data:

                create_key_pair(data)

                data['key_pair_name'] = data['new_key_pair_name']
                data.pop('new_key_pair_name')

            else:

                data['key_pair_name'] = data['existing_key_pair_name']
                data.pop('existing_key_pair_name')

            # Read existing terraform.auto.tfvars content
            with open('terraform.auto.tfvars', 'r') as f:
                existing_content = f.readlines()

            # Update validated input fields
            for key, value in data.items():
                # Exclude double quotations for numeric fields
                if key.endswith('min_instances') or key.endswith('max_instances'):
                    new_line = f"{key} = {value}\n"
                else:
                    new_line = f"{key} = \"{value}\"\n"

                # Check if the variable already exists in terraform.auto.tfvars
                for i, line in enumerate(existing_content):
                    if key in line:
                        existing_content[i] = new_line
                        break
                else:
                    # If the variable doesn't exist, append it to the content
                    existing_content.append(new_line)

            # Write updated content back to terraform.auto.tfvars
            with open('terraform.auto.tfvars', 'w') as f:
                f.writelines(existing_content)

                # Trigger infrastructure deployment
                # response = deploy_infrastructure()

                # if response[1] == 200:  # Check the status code
                return jsonify({'message': 'Form validation successful and infrastructure deployment triggered'}), 200
            # else:
            #   return jsonify({'error': 'Failed to trigger infrastructure deployment after form validation'}), 500

    except Exception as e:
        error_message = f'Error validating form data: {str(e)}'
        return jsonify({'error': error_message}), 500


@app.route(f'{high_prefix}/existing_key_pairs', methods=['POST'])
def get_key_pairs():
    region = request.form.get('region')

    try:
        ec2 = boto3.client('ec2', region_name=region)

        # Retrieve the list of existing key pairs
        response = ec2.describe_key_pairs()
        key_pairs = [key_pair['KeyName'] for key_pair in response['KeyPairs']]

        return jsonify({'existing_key_pairs': key_pairs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route(f'{high_prefix}/create_key_pair', methods=['POST'])
def create_key_pair():
    try:

        region = request.form.get('region')
        new_key_pair_name = request.form.get('new_key_pair_name')

        ec2 = boto3.client('ec2', region_name=region)

        # Generate a new key pair
        response = ec2.create_key_pair(KeyName=new_key_pair_name)

        # Save the private key to a file
        with open(f"{new_key_pair_name}.pem", 'w') as key_file:
            key_file.write(response['KeyMaterial'])

        return jsonify({'message': 'Key pair created successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route(f'{high_prefix}/get_regions', methods=['GET'])
def get_all_regions():
    ec2_client = boto3.client('ec2')

    try:
        response = ec2_client.describe_regions()

        # Extract region names from the response
        all_regions = [region['RegionName'] for region in response['Regions']]
        return all_regions
    except Exception as e:
        print(f"Error retrieving regions: {e}")
        return []


@app.route(f'{high_prefix}/amis', methods=['POST'])
def get_amis_by_os():
    region = request.form.get('region')
    os_type = request.form.get('os_type')

    ec2_client = boto3.client('ec2', region_name=region)

    if os_type == 'linux':
        name_filter = 'amzn2-ami-hvm-*'
    elif os_type == 'windows':
        name_filter = 'Windows_Server-*'
    elif os_type == 'ubuntu':
        name_filter = 'ubuntu/images/*'
    else:
        return jsonify({'error': 'Invalid OS type'}), 400

    filters = [
        {'Name': 'name', 'Values': [name_filter]},
        {'Name': 'architecture', 'Values': ['x86_64']},
        {'Name': 'root-device-type', 'Values': ['ebs']},
        {'Name': 'virtualization-type', 'Values': ['hvm']},
        {'Name': 'state', 'Values': ['available']},

    ]

    # Retrieve AMIs based on the filters
    try:
        response = ec2_client.describe_images(Filters=filters)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Extract relevant information from the response
    ami_list = []
    for image in response['Images']:
        ami_list.append({
            'ImageId': image['ImageId'],
            'Name': image['Name'],
            'Description': image['Description'],
        })

    return jsonify(ami_list)


@app.route(f'{high_prefix}/instance_types', methods=['POST'])
def get_instance_types():
    try:
        region = request.form.get('region')

        # Initialize AWS EC2 client
        ec2_client = boto3.client('ec2', region_name=region)

        # Get all instance types available in the region
        response = ec2_client.describe_instance_type_offerings(
            LocationType='region',
            Filters=[
                {'Name': 'location', 'Values': [region]}
            ]
        )

        instance_types = [instance['InstanceType'] for instance in response['InstanceTypeOfferings']]

        return jsonify(instance_types)

    except Exception as e:
        error_message = f"Error: {e}"
        return jsonify({"error": error_message})


@app.route(f'{high_prefix}/db_engine_types', methods=['POST'])
def list_db_engine_types():
    region = request.form.get('region')

    rds_client = boto3.client('rds',
                              region_name=region)
    response = rds_client.describe_db_engine_versions()

    engine_types = set()  # Using a set to store unique engine types

    for engine in response['DBEngineVersions']:
        engine_types.add(engine['Engine'])

    return jsonify(list(engine_types))


@app.route(f'{high_prefix}/db_engine_versions', methods=['POST'])
def list_db_engine_versions():
    region = request.form.get('region')
    engine = request.form.get('engine')

    rds_client = boto3.client('rds',
                              region_name=region)

    response = rds_client.describe_db_engine_versions(Engine=engine)

    mysql_versions = [version['EngineVersion'] for version in response['DBEngineVersions']]

    return jsonify(mysql_versions)


@app.route(f'{high_prefix}/deployment_info', methods=['GET'])
def deployment_info():
    try:

        s3_client = boto3.client('s3', region_name=region_name)

        # List objects in the specified bucket
        response = s3_client.list_objects_v2(Bucket=highbucket_name)

        # Extract object keys from the response
        object_keys = []
        if 'Contents' in response:
            object_keys = [obj['Key'] for obj in response['Contents']]

        # Retrieve and extract content of each object
        object_contents = []
        for key in object_keys:
            obj_response = s3_client.get_object(Bucket=highbucket_name, Key=key)
            obj_content = obj_response['Body'].read().decode('utf-8')
            object_contents.append(json.loads(obj_content))

        return jsonify({'objects': object_contents}), 200
    except Exception as e:
        error_message = f'Error listing S3 objects: {str(e)}'
        return jsonify({'error': error_message}), 500


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
    os.environ['TF_VAR_key_pair_name'] = 'integrateLightsail'

    terraform_dir = "../../terraform/lightsail"
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

#Add Monolitic Routes only

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)