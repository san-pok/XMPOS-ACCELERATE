from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
import subprocess
import os
import boto3
import json

app = Flask(__name__)
CORS(app, origins='*')


@app.route('/deploy', methods=['POST'])
def deploy_infrastructure():
    try:
        # Check if the deploy.sh script exists
        script_path = './deploy.sh'
        if not os.path.exists(script_path):
            error_message = 'Error: deploy.sh script not found'
            return jsonify({'error': error_message}), 500

        # Execute the deploy.sh script
        subprocess.run([script_path], check=True)

        return jsonify({'message': 'Infrastructure deployment triggered successfully by py'}), 200
    except subprocess.CalledProcessError as e:
        error_message = f'Error deploying infrastructure by py: {e.stderr.decode()}'
        return jsonify({'error': error_message}), 500
    except Exception as e:
        error_message = f'Unknown error: {str(e)}'
        return jsonify({'error': error_message}), 500


@app.route('/destroy', methods=['POST'])
def destroy_infrastructure():
    try:
        # Check if the destroy.sh script exists
        script_path = './destroy.sh'
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


@app.route('/validate_form', methods=['POST'])
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


@app.route('/existing_key_pairs', methods=['GET'])
def get_key_pairs():
    try:
        region = 'ap-southeast-2'  # Sydney region
        ec2 = boto3.client('ec2', region_name=region)

        # Retrieve the list of existing key pairs
        response = ec2.describe_key_pairs()
        key_pairs = [key_pair['KeyName'] for key_pair in response['KeyPairs']]

        return jsonify({'existing_key_pairs': key_pairs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/create_key_pair', methods=['POST'])
def create_key_pair(data):
    try:

        region = data['aws_region']
        ec2 = boto3.client('ec2', region_name=region)

        data['key_pair'] = "new_key_pair_name"

        # Generate a new key pair
        response = ec2.create_key_pair(KeyName=data['new_key_pair_name'])

        # Save the private key to a file
        with open(f"{data['new_key_pair_name']}.pem", 'w') as key_file:
            key_file.write(response['KeyMaterial'])

        return jsonify({'message': 'Key pair created successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_regions', methods=['GET'])
def get_all_regions():
    # Create an EC2 client
    ec2_client = boto3.client('ec2')

    try:
        # Describe all regions
        response = ec2_client.describe_regions()

        # Extract region names from the response
        all_regions = [region['RegionName'] for region in response['Regions']]
        return all_regions
    except Exception as e:
        print(f"Error retrieving regions: {e}")
        return []


@app.route('/instance-types2')
def get_instance_types2():
    try:
        # Initialize AWS EC2 client
        ec2_client = boto3.client('ec2', region_name='ap-southeast-2')

        # Get all instance types using the Pricing API
        paginator = ec2_client.get_paginator('describe_instance_type_offerings')
        page_iterator = paginator.paginate(
            LocationType='region',
            Filters=[
                {'Name': 'location', 'Values': ['ap-southeast-2']}
            ]
        )

        instance_types = []
        for page in page_iterator:
            for instance_type in page['InstanceTypeOfferings']:
                instance_types.append(instance_type['InstanceType'])

        return jsonify({"instance_types": instance_types})
    except Exception as e:
        error_message = f"Error: {e}"
        return jsonify({"error": error_message})


@app.route('/get_instance_type')
def get_instance_types():
    try:
        region = 'ap-southeast-2'  # Specify the region here

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


@app.route('/db_engine_types')
def list_db_engine_types():
    rds_client = boto3.client('rds',
                              region_name='ap-southeast-2')
    response = rds_client.describe_db_engine_versions()

    engine_types = set()  # Using a set to store unique engine types

    for engine in response['DBEngineVersions']:
        engine_types.add(engine['Engine'])

    return jsonify(list(engine_types))


@app.route('/db_engine_versions')
def list_db_engine_versions():

    engine = 'aurora-postgresql'

    rds_client = boto3.client('rds', region_name='ap-southeast-2')  # Replace 'your-region-name' with your actual AWS region
    response = rds_client.describe_db_engine_versions(Engine=engine)

    mysql_versions = [version['EngineVersion'] for version in response['DBEngineVersions']]

    return jsonify(mysql_versions)


@app.route('/amis', methods=['GET'])
def get_amis():
    try:
        ec2 = boto3.client('ec2', region_name='ap-southeast-2')

        # Retrieve AMIs for Linux
        linux_images = ec2.describe_images(Filters=[
            {'Name': 'name', 'Values': ['amzn2-ami-hvm-*']},
            {'Name': 'architecture', 'Values': ['x86_64']},
            {'Name': 'root-device-type', 'Values': ['ebs']},
            {'Name': 'virtualization-type', 'Values': ['hvm']},
        ])

        # Retrieve AMIs for Windows
        windows_images = ec2.describe_images(Filters=[
            {'Name': 'platform', 'Values': ['windows']},
            {'Name': 'architecture', 'Values': ['x86_64']},
            {'Name': 'root-device-type', 'Values': ['ebs']},
            {'Name': 'virtualization-type', 'Values': ['hvm']},
        ])

        # Retrieve AMIs for Ubuntu
        ubuntu_images = ec2.describe_images(Filters=[
            {'Name': 'name', 'Values': ['ubuntu/images/*']},
            {'Name': 'architecture', 'Values': ['x86_64']},
            {'Name': 'root-device-type', 'Values': ['ebs']},
            {'Name': 'virtualization-type', 'Values': ['hvm']},
        ])

        # Extract desired attributes for Linux AMIs
        linux_amis = extract_info(linux_images['Images'])

        # Extract desired attributes for Windows AMIs
        windows_amis = extract_info(windows_images['Images'])

        # Extract desired attributes for Ubuntu AMIs
        ubuntu_amis = extract_info(ubuntu_images['Images'])

        return {
            'linux_amis': linux_amis,
            'windows_amis': windows_amis,
            'ubuntu_amis': ubuntu_amis
        }
    except Exception as e:
        return {'error': str(e)}


def extract_info(images):
    return images
    for image in images:
        extracted_image = {
            'Architecture': image['Architecture'],
            'ImageId': image['ImageId'],
            'PlatformDetails': image['PlatformDetails'],
            'RootDeviceType': image['RootDeviceType'],
            'VirtualizationType': image['VirtualizationType']
        }
        # Check if the Description attribute exists
        if 'Description' in image:
            extracted_image['Description'] = image['Description']
        extracted_images.append(extracted_image)
    return extracted_images


@app.route('/lamis', methods=['GET'])
def list_linux_amis():
    # Create a Boto3 EC2 client
    region = 'ap-southeast-2'  # Sydney region
    ec2_client = boto3.client('ec2', region_name=region)

    # Retrieve AMIs for Linux
    response = ec2_client.describe_images(Filters=[
        {'Name': 'name', 'Values': ['amzn2-ami-hvm-*']},
        {'Name': 'architecture', 'Values': ['x86_64']},
        {'Name': 'root-device-type', 'Values': ['ebs']},
        {'Name': 'virtualization-type', 'Values': ['hvm']},
    ])

    return jsonify(response)

    # Extract relevant information from the response
    ami_list = []
    for image in response['Images']:
        ami_list.append({
            'ImageId': image['ImageId'],
            'Name': image['Name'],
            'Description': image['Description'],
            'CreationDate': image['CreationDate']
        })

    # Return the AMI list as JSON response
    return jsonify(ami_list)


if __name__ == '__main__':
    app.run(debug=True)
