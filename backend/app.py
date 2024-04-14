from flask import Flask, jsonify, render_template, request, redirect, session
from flask_cors import CORS
import subprocess
import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os
import boto3
from botocore.exceptions import ClientError
from botocore.exceptions import NoCredentialsError, ClientError
import logging
import datetime
import botocore
from operator import itemgetter
from handler import capture_ec2_and_lightsail_instance_output, generate_timestamp, generate_unique_id, get_instance_data_from_s3, prepare_eamil, save_instance_data_to_s3


from dotenv import load_dotenv

load_dotenv()

load_dotenv()

highbucket_name = 'amirxmopbucket'
region_name = 'ap-southeast-2'
create_bucket_config = {
    'LocationConstraint': region_name
}

# Define the prefix
high_prefix = '/highly'
mono_prefix = '/monolith'

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:8000"}})
CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# getting the userpool details from env file
AWS_REGION = os.getenv('AWS_REGION')
COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
COGNITO_APP_CLIENT_ID = os.getenv('COGNITO_APP_CLIENT_ID')

cognito_client = boto3.client('cognito-idp', region_name=AWS_REGION)

app.secret_key = 'your_secret_key'


@app.route('/')
def index():
    return "Welcome to the Deployment Platform!"


@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')


    try:
        response = cognito_client.sign_up(
            ClientId=os.getenv('COGNITO_APP_CLIENT_ID'),
            Username=email,
            Password=password,
            UserAttributes=[{'Name': 'email', 'Value': email}],
        )
        return jsonify({'message': 'Signup successful. Please check your email to verify your account.'}), 200
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'UsernameExistsException':
            return jsonify({'error': 'User already exists.'}), 409  # 409 Conflict
        else:
            return jsonify({'error': 'Failed to sign up. Please try again.'}), 500


@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')

    try:
        response = cognito_client.confirm_sign_up(
            ClientId=os.getenv('COGNITO_APP_CLIENT_ID'),
            Username=email,
            ConfirmationCode=code,
            ForceAliasCreation=False
        )
        return jsonify({'message': 'Account verified successfully'}), 200
    except cognito_client.exceptions.UserNotFoundException:
        return jsonify({'error': 'User does not exist.'}), 404
    except cognito_client.exceptions.CodeMismatchException:
        return jsonify({'error': 'Invalid verification code.'}), 400
    except cognito_client.exceptions.NotAuthorizedException:
        return jsonify({'error': 'User is already confirmed.'}), 400
    except Exception as e:
        # Generic error handling
        return jsonify({'error': str(e)}), 500


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        auth_result = cognito_client.initiate_auth(
            ClientId=COGNITO_APP_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={'USERNAME': email, 'PASSWORD': password}
        )
        return jsonify({'message': 'Login successful', 'tokens': auth_result}), 200
    except cognito_client.exceptions.NotAuthorizedException:
        return jsonify({'error': 'Incorrect username or password.'}), 401
    except cognito_client.exceptions.UserNotFoundException:
        return jsonify({'error': 'User does not exist.'}), 404
    except cognito_client.exceptions.UserNotConfirmedException:
        return jsonify({'error': 'User is not confirmed. Please check your email for the confirmation link.'}), 401
    except Exception as e:
        # Log the exception details for debugging purposes
        print(e)
        return jsonify({'error': 'Login failed due to an unexpected error. Please try again later.'}), 500


@app.route('/menu')
def menu():
    # Placeholder for actual logic
    return jsonify([
        {"name": "Deploy Monolith", "url": "/deploy-monolith"},
        {"name": "Deploy Highly Available", "url": "/deploy-highly-available"},
        {"name": "Deploy Lightsail", "url": "/deploy-lightsail"},
        {"name": "Deployment History", "url": "/deployment-history"},
    ]), 200


@app.route(f'{high_prefix}/deploy', methods=['POST'])
def deploy_infrastructure():
    try:

        high_terraform_dir = "../../terraform/highly"

        # Initialize Terraform
        init_output = subprocess.run(["terraform", "init"], cwd=high_terraform_dir, capture_output=True, text=True)

        if init_output.returncode != 0:
            raise Exception('Error initializing Terraform')

        # Plan Terraform
        plan_output = subprocess.run(["terraform", "plan"], cwd=high_terraform_dir, capture_output=True, text=True)
        if plan_output.returncode != 0:
            raise Exception('Error planning with Terraform')

        # Apply Terraform
        apply_output = subprocess.run(["terraform", "apply", "-auto-approve"], cwd=terraform_dir, capture_output=True,
                                      text=True)
        print(apply_output.stdout)
        if apply_output.returncode != 0:
            print(apply_output.stderr)
            raise Exception('Error applying Terraform')

        return jsonify({'message': 'Highly available instance deployed successfully!'})

    except Exception as e:

        return jsonify({'message': 'Error deploying Highly available application instance', 'error': str(e)}), 500


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
        data = request.get_json()

        # Perform form validations
        errors = {}
        for item in data:
            key = item.get('name')
            value = item.get('value')

            # Check for required fields
            if key in ['ami_type', 'instance_type', 'min_instances', 'max_instances', 'key_pair_selection', 'storage_size', 'db_engine', 'engine_version']:
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

            key_pair_selection = next((item.get('value') for item in data if item.get('name') == 'key_pair_selection'), None)

            if key_pair_selection == "create":
                create_key_pair(data)

                new_key_pair_name = next((item.get('value') for item in data if item.get('name') == 'new_key_pair_name'), None)

                data.append({'name': 'key_pair_name', 'value': new_key_pair_name})

            else:
                existing_key_pair_name = next((item.get('value') for item in data if item.get('name') == 'existing_key_pair'), None)
                data.append({'name': 'key_pair_name', 'value': existing_key_pair_name})

            with open('../terraform/highly/terraform.auto.tfvars', 'r') as f:
                existing_content = f.readlines()

            # Update validated input fields
            for item in data:
                key = item.get('name')
                value = item.get('value')

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
            with open('../terraform/highly/terraform.auto.tfvars', 'w') as f:
                f.writelines(existing_content)

            # Trigger infrastructure deployment
            # response = deploy_infrastructure()

            # if response[1] == 200:  # Check the status code
            return jsonify({'message': 'Form validation successful and infrastructure deployment triggered'}), 200

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
        # Retrieve information about all available AWS regions
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

    # Define filters to retrieve images
    filters = [
        {'Name': 'name', 'Values': [name_filter]},
        {'Name': 'architecture', 'Values': ['x86_64']},
        {'Name': 'root-device-type', 'Values': ['ebs']},
        {'Name': 'virtualization-type', 'Values': ['hvm']},
        {'Name': 'state', 'Values': ['available']},

    ]

    try:
        response = ec2_client.describe_images(Filters=filters)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

    engine_types.add('mysql')

    return jsonify(list(engine_types))


@app.route(f'{high_prefix}/db_engine_versions', methods=['POST'])
def list_db_engine_versions():
    try:
        region = request.form.get('region')
        engine = request.form.get('engine')

        rds_client = boto3.client('rds', region_name=region)

        # Retrieve information about available database engine versions for the specified engine
        response = rds_client.describe_db_engine_versions(Engine=engine)

        # Extract engine versions from the response
        versions = [version['EngineVersion'] for version in response['DBEngineVersions']]

        return jsonify(versions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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


#Highly Available Deployment Routes up to here

#LightSail Routes starts from here

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
    ssh_key_user_input = data.get('sshKey', 'XmopsTeamTwo')  # Use 'default' if 'sshKey' not provided

    # Generate SSH key based on the user input
    public_ssh_key = generate_ssh_key(ssh_key_user_input)

    # Setup environment variables for Terraform
    os.environ['TF_VAR_ssh_key'] = public_ssh_key
    os.environ['TF_VAR_instance_name'] = data.get('instanceName', 'XMOPSTeamTwo')
    os.environ['TF_VAR_bundle_id'] = data.get('instanceSize', 'nano_3_2')
    os.environ['TF_VAR_key_pair_name'] = 'integrateLightsail'

    terraform_dir = "../terraform/lightsail"
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
        apply_output = subprocess.run(["terraform", "apply", "-auto-approve"], cwd=terraform_dir, capture_output=True,
                                      text=True)
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

        return jsonify(
            {'message': 'Lightsail deployed successfully!', 'wordpressInstallationUrl': wordpressInstallationUrl})

    except Exception as e:
        # Log the error and save the 'failed' status if an exception is caught
        print(f"Deployment failed: {str(e)}")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "success"  # or "failed" based on your deployment outcome
        save_deployment_to_s3("XMOPSteamTwo", timestamp, status)

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


# Add Monolitic Routes only
##############################   Add Monolitic Routes only     ####################

# route to fetch instance status data
@app.route('/fetch-instance-status')
def fetch_instance_status():
    # return render_template('dashboard.html')
    instance_data = get_instance_data_from_s3(bucket_name, key_prefix)
    return jsonify(instance_data)
    
#route to fetch aws regions 
@app.route(f'{mono_prefix}/get-regions', methods=['GET'])
def get_all_regions_monolith():
    # Create an EC2 client
    ec2_client = boto3.client('ec2')
    try:
        # Describe all regions
        response = ec2_client.describe_regions()

        # Extract region names from the response
        all_regions = [{'DisplayName': region['RegionName'], 'Endpoint': region['Endpoint'], 'RegionName': region['RegionName']} for region in response['Regions']]

        # Check each region for permissions to run instances
        authorized_regions = []

        # Iterate over each region
        for region in all_regions:
            region_name = region['RegionName']
            
            # Create an EC2 client for the specific region
            ec2_client = boto3.client('ec2', region_name=region_name)

            try:
                # Get all EC2 instances in the current region
                instances_response = ec2_client.describe_instances()
                region['DisplayName'] += ' (******* Access *******)'
                authorized_regions.append(region)
                
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'UnauthorizedOperation':
                    # Append "No Access" to regions with UnauthorizedOperation errors
                    region['DisplayName'] += ' (No Access)'
            
        # Store AWS regions in the session
        session['aws_regions'] = all_regions

        return jsonify({'regions': all_regions})
    except Exception as e:
        print(f"Error retrieving regions: {e}")
        return []

@app.route(f'{mono_prefix}/amis', methods=['GET'])
def get_amis_monolith():
    try:
        region = request.args.get('region')
        os_type = request.args.get('os_type')

        ec2 = boto3.client('ec2', region_name=region)

        # Define filters based on the OS type
        if os_type == 'ubuntu':
            filters = [
                {'Name': 'name', 'Values': ['ubuntu/images/*']},
                # {'Name': 'description', 'Values': ['*Ubuntu*']},
                {'Name': 'architecture', 'Values': ['x86_64']},
                {'Name': 'root-device-type', 'Values': ['ebs']},
                {'Name': 'virtualization-type', 'Values': ['hvm']},
                {'Name': 'state', 'Values': ['available']},
                {'Name': 'is-public', 'Values': ['true']},
                {'Name': 'owner-id', 'Values': ['099720109477']}  # AWS-owned AMIs
                
            ]
        elif os_type == 'windows':
            filters = [
                {'Name': 'platform', 'Values': ['windows']},
                {'Name': 'architecture', 'Values': ['x86_64']},
                {'Name': 'root-device-type', 'Values': ['ebs']},
                {'Name': 'virtualization-type', 'Values': ['hvm']},
                {'Name': 'state', 'Values': ['available']},
                {'Name': 'is-public', 'Values': ['true']},
                {'Name': 'owner-id', 'Values': ['099720109477']},  # AWS-owned AMIs
            ]
        else:  # Assume Linux AMIs
            filters = [
                {'Name': 'name', 'Values': ['amzn2-ami-hvm-*']},
                {'Name': 'architecture', 'Values': ['x86_64']},
                {'Name': 'root-device-type', 'Values': ['ebs']},
                {'Name': 'virtualization-type', 'Values': ['hvm']},
                {'Name': 'state', 'Values': ['available']},
                {'Name': 'is-public', 'Values': ['true']},
                {'Name': 'owner-id', 'Values': ['099720109477']},  # AWS-owned AMIs
            ]
        print ('Selected os: ', filters)
        # Retrieve AMIs based on the filters
        images = ec2.describe_images(Filters=filters)['Images']
        
        # Extract desired attributes for the fetched AMIs
        amis = extract_info(images)
        amisJson =json.dumps(amis, indent = 4 )
        # print ('Selected AMIs: ', amisJson)
        # return jsonify({os_type: amis})
        return amisJson
    except Exception as e:
        return {'error': str(e)}
def extract_info(images):
    extracted_images = []
    for image in images:
        # Exclude Marketplace AMIs
        extracted_image = {
            'Architecture': image['Architecture'],
            'ImageId': image['ImageId'],
            'PlatformDetails': image['PlatformDetails'],
            'RootDeviceType': image['RootDeviceType'],
            'VirtualizationType': image['VirtualizationType'],
            'Description': image['Description'],
            'ImageType': image['ImageType'],
            'Public': image['Public']
        }
        extracted_images.append(extracted_image)
    return extracted_images

@app.route(f'{mono_prefix}/instance-types', methods=['GET'])
def get_instance_types_monolith():
    try:
        region = request.args.get('region')
        # region = 'ap-southeast-2'
        ec2 = boto3.client('ec2', region_name=region)
        instance_types = ec2.describe_instance_type_offerings()

        # Extract instance type names from the response
        instance_type_names = [instance['InstanceType'] for instance in instance_types['InstanceTypeOfferings']]

        # Sort instance types in ascending order
        sorted_instance_types = sorted(instance_type_names)

        # Filter instance types based on FreeTierEligible attribute
        # free_tier_instance_types = [instance_type for instance_type in instance_types if instance_type.get('FreeTierEligible', True)]

        # return jsonify({'instance_types': instance_type_names, 'Free_instance_types': free_tier_instance_types} )
        return jsonify({'instance_types': sorted_instance_types})
    except Exception as e:
        return jsonify({'error': str(e)})
    
@app.route(f'{mono_prefix}/existing_key_pairs', methods=['GET'])
def get_existing_key_pairs():
    region = request.args.get('region')

    try:
        ec2 = boto3.client('ec2', region_name=region)

        # Retrieve the list of existing key pairs
        response = ec2.describe_key_pairs()
        key_pairs = [key_pair['KeyName'] for key_pair in response['KeyPairs']]
        print(f"Existing Key Pairs in {region}:", key_pairs)

        return jsonify({'existing_key_pairs': key_pairs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route(f'{mono_prefix}/generate_key_pair', methods=['POST'])
def generate_new_key_pair():
    data = request.get_json()
    region = data.get('region')
    new_key_pair_name = data.get('new_key_pair_name')
    print('Region:', region)
    print('New Key Pair Name:', new_key_pair_name)

    try:
        ec2 = boto3.client('ec2', region_name=region)

        # Generate a new key pair
        response = ec2.create_key_pair(KeyName=new_key_pair_name)

        # Save the private key to a file
        key_material = response['KeyMaterial']
        key_file_path = f"{new_key_pair_name}.pem"
        with open(key_file_path, 'w') as key_file:
            key_file.write(key_material)

        return jsonify({'message': 'Key pair created successfully', 'key_file_path': key_file_path}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route(f'{mono_prefix}/get-security-groups')
def get_security_groups():
    aws_region = request.args.get('region')
    try: 
        # aws_region = 'ap-southeast-1'
        ec2_client = boto3.client('ec2', region_name = aws_region)
        response = ec2_client.describe_security_groups()
        # Extract security group information from the response
        security_groups = response['SecurityGroups']
        # Extract relevant data from security groups 
        formatted_security_groups = []
        for group in security_groups:
            formatted_security_groups.append({
                'GroupName': group['GroupName'],
                'GroupId': group['GroupId'],
            })
        return jsonify({'security_groups': formatted_security_groups})
    except Exception as e:
        return jsonify({'error': str(e)})
    
@app.route(f'{mono_prefix}/create_security_group', methods=['POST'])
def create_security_group():
    data = request.json
    group_name = data.get('new_sg_name')
    description = data.get('new_sg_description')
    aws_region = data.get('region')
    # group_name = 'group_name'
    # description ='description'
    ec2_client = boto3.client('ec2', region_name = aws_region)

    if not all([group_name, description]):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    try:
        response = ec2_client.create_security_group(
            GroupName=group_name,
            Description=description
        )
        return jsonify({'generated_sg': response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route(f'{mono_prefix}/deploy-monolith', methods=['POST'])
def submit_form_monolith():
    os.chdir('../terraform/monolithic')
    try: 
        aws_region = request.json.get('aws-region')
        ami_id = request.json.get('aws-ami')
        instance_type = request.json.get('instance-type')
        key_pair = request.json.get('key_pair')
        security_group = request.json.get('security_group')
        security_group_description = request.json.get('security_group_description')
        allow_ssh = request.json.get('allow-ssh')
        allow_http = request.json.get('allow-http')
        selectedSGId = request.json.get('selectedSGId')
        createdSG = request.json.get('createdSG')
        newSecurityGroupName = request.json.get('newSecurityGroupName')
        storage_size_gb = request.json.get('ebs-storage')
        database_type = request.json.get('database_type')
        web_server_engine = request.json.get('web-server')

        if allow_ssh == 'on':
            allow_ssh = 'true'
        else:
            allow_ssh = 'false'

        if allow_http == 'on':
            allow_http = 'true'
        else:
            allow_http = 'false'

        # # Check if selectedSGId is not empty, otherwise use createdSG
        # selectedSG_to_pass = security_group if security_group else createdSG
        # print ('Selected SG to pass ', selectedSG_to_pass)
        

        print("Received data:")
        print("AWS Region:", aws_region)
        print("AMI ID:", ami_id)
        print("Instance Type:", instance_type)
        print("Key Pair:", key_pair)
        print("Created SG Name:", newSecurityGroupName)
        print("SG id:", selectedSGId)
        print("storage_size_gb:", storage_size_gb)
        print("database_type:", database_type)
        print("web_server_engine:", web_server_engine)


        # Generate unique identifier for the deployment 
        deployment_id = generate_unique_id()
        print(f'deployment_id: {deployment_id}')

        # Get the absolute path to terraform.auto.tfvars for debugging
        tfvars_file = os.path.abspath('terraform.auto.tfvars')
        print("Absolute path to terraform.auto.tfvars:", tfvars_file)

        # Write the user-submitted values to a TFVars file
        # with open('./terraform/wordpress-ec2/terraform.auto.tfvars', 'w') as f:
        with open('terraform.auto.tfvars', 'w') as f:
            f.write(f'aws_region = "{aws_region}"\n')
            f.write(f'ami_id = "{ami_id}"\n')
            f.write(f'instance_type = "{instance_type}"\n')
            f.write(f'key_name = "{key_pair}"\n')
            f.write(f'security_group_name = "{newSecurityGroupName}"\n')
            f.write(f'security_group_description = "{security_group_description}"\n')
            f.write(f'allow_ssh = {allow_ssh}\n')
            f.write(f'allow_http = {allow_http}\n')
            f.write(f'storage_size_gb = {storage_size_gb}\n')
            f.write(f'database_type = "{database_type}"\n')
            f.write(f'web_server = "{web_server_engine}"\n')

        #define directory path for the deployment's state file
        state_file_dir = f'state_files'
    
        # specify path to the Terraform state file
        state_file_path = f'{state_file_dir}/{deployment_id}.terraform.tfstate'
        subprocess.run(['terraform', 'init',], check=True)
        subprocess.run(['terraform', 'apply', '-auto-approve', f'-state={state_file_path}'], check=True)  
        
        output_data_of_ec2 = capture_ec2_and_lightsail_instance_output(state_file_path)
        print('incoming data from creation ec2 \n', output_data_of_ec2)
        # Generate current timestamp
        current_timestamp = generate_timestamp()
        print ('Output of current time', current_timestamp)
        # Add deployment type to instance data
        output_data_of_ec2['deployment_id'] = deployment_id
        output_data_of_ec2['deployment_type'] = 'Monolith'
        # Add timestamp to instance data
        output_data_of_ec2['creation_time'] = current_timestamp
        output_data_of_ec2['deletion_time'] = ''

        save_instance_data_to_s3(output_data_of_ec2, bucket_name, key_prefix)

        instance_data = get_instance_data_from_s3(bucket_name, key_prefix)
        # print("Instance data retrieved from S3:", instance_data)
        # Add the new entry to the deployment history for instance creation
       
        # refresh_page()
        return jsonify(instance_data), 200, {'message': 'Wordpress on EC2 is deployed successfully.'}
        # return render_template('index.html')

    except Exception as e:
        error_message = str(e)
        logging.error(f'Error occurred: {error_message}')  # Log the error
        return f'Error: {error_message}', 500 # Return an error response with status code 500
    finally:
        os.chdir(original_dir)


@app.route('/count-running-ec2-instances')
# @app.route(f'{mono_prefix}/count-running-ec2-instances')
def count_running_ec2_instances():
    try:
        # Create an EC2 client
        ec2_client = boto3.client('ec2')

        # Get all EC2 regions
        regions_response = ec2_client.describe_regions()

        # Check each region for permissions to run instances
        authorized_regions = []

        # Initialize count for running instances and access denied regions
        total_running_instance_count = 0
        access_denied_count = 0
        authorized_regions_count = 0

        # Iterate over each region
        for region in regions_response['Regions']:
            region_name = region['RegionName']

            # Create an EC2 client for the specific region
            ec2_client = boto3.client('ec2', region_name=region_name)

            try:
                # Get all EC2 instances in the current region
                instances_response = ec2_client.describe_instances()

                # Filter running instances
                running_instances = []

                # Iterate each reservation in the list of reservations
                for reservation in instances_response['Reservations']:
                    # Retrieve a list of instances within the current reservation
                    instance_in_reservation = reservation['Instances']
                    # Iterate over each instance in the list of instances
                    for instance in instance_in_reservation:
                        # Check if current instance is running
                        if instance['State']['Name'] == 'running':
                            running_instances.append(instance)

                # Count the number of running instances in the current region
                running_instance_count_in_region = len(running_instances)
                total_running_instance_count += running_instance_count_in_region

                # print(f"Region: {region_name}, Running EC2 Instance Count: {running_instance_count_in_region}")
                authorized_regions_count += 1
                authorized_regions.append(region_name)

            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'UnauthorizedOperation':
                    access_denied_count += 1

        print(f"Total number of running EC2 instances across all regions: {total_running_instance_count}")
        print(f"Total number of EC2 Instance UnauthorizedOperation errors: {access_denied_count}")
        print("EC2 Instance Authorized regions:", authorized_regions, "Number of EC2 Instance Authorized regions: ", authorized_regions_count)
        
        return jsonify({'running_instances': total_running_instance_count,
                        'Authorized regions': authorized_regions,
                        'Number of Authorized regions': authorized_regions_count })

    except Exception as e:
        return jsonify({'error': str(e)})
 

@app.route('/count-lightsail-instances')
def count_instances():

    # Create a Lightsail client
    lightsail_client = boto3.client('lightsail')

    # Get all Lightsail regions
    regions_response = lightsail_client.get_regions()

    # Initialize count for all instances
    total_instance_count = 0
    access_denied_count = 0
    # Iterate over each region
    for region in regions_response['regions']:
        region_name = region['name']
        
        # Create a Lightsail client for the specific region
        lightsail_client = boto3.client('lightsail', region_name=region_name)

        try: 

            # Get all Lightsail instances in the current region
            instances_response = lightsail_client.get_instances()

            # Count the number of instances in the current region
            instance_count_in_region = len(instances_response['instances'])
            total_instance_count += instance_count_in_region

            # print(f"Region: {region_name}, Lightsail Instance Count: {instance_count_in_region}")
        except botocore.exceptions.ClientError as e: 
            if e.response['Error']['Code'] == 'AccessDeniedException':
                # print(f"Lightsail Instance Access Denied in region {region_name}")
                access_denied_count += 1
            else :
                raise e

    print(f"Total number of Lightsail instances across all regions: {total_instance_count}")
    print(f"Total number of Lightsail instances Access Denied errors: {access_denied_count}")
    return jsonify({'running_instances': total_instance_count})

@app.route(f'{mono_prefix}/destroy-ec2')
def destroy_ec2():
    os.chdir('../terraform/monolithic')
    instance_id = request.args.get('instance_id')
    deployment_id = request.args.get('deployment_id')
    # print (f'deployment_id: {deployment_id}')

    deployment_id_tfstate = deployment_id + ".terraform.tfstate"
    print (f'deployment_id_tfstate:, {deployment_id_tfstate}')
    # Construct the path to the state_files folder
    state_files_folder = 'state_files'

    # Iterate through the files in the state_files directory
    for filename in os.listdir(state_files_folder):
        if filename.startswith(deployment_id_tfstate):
            state_file_path = os.path.abspath(os.path.join(state_files_folder, filename))
            print(f'Found state file for deployment ID {deployment_id_tfstate}: {state_file_path}')
            break
    else:
        return f'Error: State file not found for deployment ID {deployment_id_tfstate}'

    # Run Terraform Command to destroy EC2 instance
    try:
        subprocess.run(['terraform', 'destroy', '-auto-approve', f'-state={state_file_path}'], check=True)
        instance_data = get_instance_data_from_s3(bucket_name, key_prefix)
        print("Instance data retrieved from S3 when instance is being destroyed:", instance_data)

        # Get instance data from S3 instance_data.json
        for instance in instance_data:
            if instance['instance_id'] == instance_id:
                # Generate current timestamp
                current_timestamp = generate_timestamp()
                # Update deletion_time for destroying time
                instance['deletion_time'] = current_timestamp
                instance['instance_state'] = 'Destroyed'

                # Save the updated instance data back to S3
                print("Instance data retrieved from S3 when instance is being destroyed to be saved:", instance_data)
                unwrapped_list = {}
                for dictionary in instance_data:
                    unwrapped_list.update(dictionary)
                save_instance_data_to_s3(unwrapped_list, bucket_name, key_prefix_history)
        
        #delete instance details from S3
        delete_instance_details_from_s3(instance_id)
        # return instance_data
        return 'EC2 instance destroyed successfully'
    except subprocess.CalledProcessError as e:
        return f'Error destroying EC2 instance : {e}'
    finally:
        os.chdir(original_dir)

def delete_instance_details_from_s3(instance_id):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=key_prefix)
        instance_data = json.loads(response['Body'].read().decode('utf-8'))
    except Exception as e:
        print(f"Error retrieving instance data from s3: {e}")
        return
    
    #find and remove the instance with the provided instance ID
    for instance in instance_data:
        if instance['instance_id'] == instance_id:
            instance_data.remove(instance)
    # Update the instance_data.json file in S3 with the modified list
    try: 
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key_prefix,
            Body=json.dumps(instance_data).encode('utf-8')
        )
        print(f"Instance with Instance ID '{instance_id}' deleted from S3.")
    except Exception as e:
        print(f"Error updating instance data in S3: {e}")


@app.route('/get-deployment-history')
def deployment_history():
    
    deployment_history_data = get_instance_data_from_s3(bucket_name, key_prefix_history )
    # print('Deployment History Data: \n', deployment_history_data)
    sorted_deployment_history_data = sorted(deployment_history_data, key=itemgetter('creation_time'))
    # print (sorted_deployment_history_data)
    return sorted_deployment_history_data

@app.route('/send-email', methods=['POST'])
def send_email():
    try:
        # Get email addresses from request parameters
        email_addresses = request.json.get('emailAddresses')
        print('Received emaill address: ',email_addresses)
        # instance_id = request.args.get('instance_id')

        prepare_eamil(bucket_name, key_prefix_history, email_addresses)
        return jsonify({'message': 'Email sent successfully'})
    except Exception as e:
        return jsonify({'error sending email in handler function': str(e)}), 500

# Route to fetch Lightsail regions
@app.route('/lightsail-regions')
def get_lightsail_regions():
    lightsail = boto3.client('lightsail')
    try:
        # Call the AWS API to describe Lightsail regions
        response = lightsail.get_regions()
        # print(json.dumps(response, indent=4))
        # regions = [region['name'] for region in response['regions']]
        regions = [{'name': region['name'], 'displayName': region['displayName']} for region in response['regions']]
        print('Regions: ', regions)
        return jsonify({'regions':regions})
    except Exception as e:
        print('Error fetching Lightsail regions:', e)
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/lightsail-blueprints')
def get_lightsail_blueprints():
    lightsail = boto3.client('lightsail')
    region = request.args.get('region')
    platform = request.args.get('platform')
    try:
        response = lightsail.get_blueprints()
        filtered_blueprints = []
        # blueprints = [{'id': blueprint['blueprintId'], 'displayName': blueprint['name']} for blueprint in response['blueprints']]
        for blueprint in response['blueprints']:
            if blueprint['platform'] == platform:
                # Extract WordPress version from the blueprintId
                # wordpress_version = blueprint['blueprintId'].split('_')[2] if 'wordpress' in blueprint['blueprintId'] else None
                filtered_blueprints.append({'id': blueprint['blueprintId'], 'displayName': blueprint['name'], 'type': blueprint['type']})
        # print('filtered blueprints:\n', filtered_blueprints)
        return jsonify({'blueprints': filtered_blueprints})
    except Exception as e:
        print ('Error fetching Lightsail blueprints: ', e)
        return jsonify({'error': 'Internal server error '}), 500
    
@app.route('/lightsail-instance-plans')
def get_lightsail_bundles():
    platform = request.args.get('platform')
    region = request.args.get('region') 
    print('selected Platform in bundle', platform)
    print('selected Region in bundle', region)
    try:
        # Create a Lightsail client for the specified region
        lightsail = boto3.client('lightsail', region_name=region)
        response = lightsail.get_bundles()
        # response = lightsail.get_instance_metric_data()
        # print(json.dumps(response, indent=4))
        filtered_bundles = []
        # # blueprints = [{'id': blueprint['blueprintId'], 'displayName': blueprint['name']} for blueprint in response['blueprints']]
        for bundle in response['bundles']:
            # if bundle['supportedPlatforms'] == platform:
            #     filtered_bundles.append({'id': bundle['bundleId'], 'displayPrice': bundle['price']})
             if platform in bundle['supportedPlatforms']:
                 filtered_bundles.append({
                    'id': bundle['bundleId'],
                    'displayPrice': bundle['price'],
                    'cpuCount': bundle['cpuCount'],
                    'diskSizeInGb': bundle['diskSizeInGb'],
                    'ramSizeInGb': bundle['ramSizeInGb'],
                    'transferPerMonthInGb': bundle['transferPerMonthInGb']
                })
        # print('filtered bundles:\n', json.dumps(filtered_bundles, indent=4))
        return jsonify({'bundles': filtered_bundles})
        
    except Exception as e:
        print ('Error fetching Lightsail bundles: ', e)
        return jsonify({'error': 'Internal server error '}), 500
    
@app.route('/deploy-lightsail', methods=['POST'])
def submit_form_lightsail():
    os.chdir('../terraform/lightsail_bb')
    try: 
        project_name = request.json.get('project-name')
        aws_region = request.json.get('region')
        platform = request.json.get('platform')
        blueprint = request.json.get('lightsail-blueprint')
        bundle_id = request.json.get('lightsail-bundle')

         # Generate unique identifier for the deployment 
        deployment_id = generate_unique_id()
        print(f'deployment_id: {deployment_id}')

        # Print the received data
        print("Received data:")
        print("AWS Region:", aws_region)
        print("AWS Platform:", platform)
        print("BluePrint:", blueprint)
        print("Bundle_id or Instance plan:", bundle_id)

        # Get the absolute path to terraform.auto.tfvars for debugging
        tfvars_file = os.path.abspath('terraform.auto.tfvars')
        print("Absolute path to terraform.auto.tfvars:", tfvars_file)
       

        # Write the user-submitted values to a TFVars file
        # with open('./terraform/wordpress-ec2/terraform.auto.tfvars', 'w') as f:
        with open('terraform.auto.tfvars', 'w') as f:

            f.write(f'aws_region = "{aws_region}"\n')
            f.write(f'project_name = "{project_name}"\n')
            f.write(f'bundle_id = "{bundle_id}"\n')
            f.write(f'lightsail_blueprints = {{"wordpress": "{blueprint}"}}\n')
        
        #define directory path for the deployment's state file
        state_file_dir = f'state_files'
    
        # specify path to the Terraform state file
        state_file_path = f'{state_file_dir}/{deployment_id}.terraform.tfstate'
        subprocess.run(['terraform', 'init',], check=True)
        subprocess.run(['terraform', 'apply', '-auto-approve', f'-state={state_file_path}'], check=True)  
        
        output_data_of_ec2 = capture_ec2_and_lightsail_instance_output(state_file_path)
        print('incoming data from creation ec2 \n', output_data_of_ec2)

        # Add deployment type to instance data
        output_data_of_ec2['deployment_id'] = deployment_id
        output_data_of_ec2['deployment_type'] = 'Lightsail'
         # Generate current timestamp
        current_timestamp = generate_timestamp()
        output_data_of_ec2['creation_time'] = current_timestamp
        output_data_of_ec2['deletion_time'] = ''

        save_instance_data_to_s3(output_data_of_ec2, bucket_name, key_prefix)
        # save_instance_data_to_s3(output_data_of_ec2, bucket_name, key_prefix_history)

        instance_data = get_instance_data_from_s3(bucket_name, key_prefix)
        print("Instance data retrieved from S3:", instance_data)
        # Add the new entry to the deployment history for instance creation
       
        # refresh_page()
        return jsonify(instance_data) 

    except Exception as e:
        error_message = str(e)
        logging.error(f'Error occurred: {error_message}')  # Log the error
        return f'Error: {error_message}', 500 # Return an error response with status code 500
    finally:
        os.chdir(original_dir)

@app.route('/destroy-lightsail')
def destroy_lightsail():
    os.chdir('../terraform/lightsail_bb')
    instance_id = request.args.get('instance_id')
    deployment_id = request.args.get('deployment_id')
    # Run Terraform Command to destroy EC2 instance

    deployment_id_tfstate = deployment_id + ".terraform.tfstate"
    print (f'deployment_id_tfstate:, {deployment_id_tfstate}')
    # Construct the path to the state_files folder
    state_files_folder = 'state_files'

    # Iterate through the files in the state_files directory
    for filename in os.listdir(state_files_folder):
        if filename.startswith(deployment_id_tfstate):
            state_file_path = os.path.abspath(os.path.join(state_files_folder, filename))
            print(f'Found state file for deployment ID {deployment_id_tfstate}: {state_file_path}')
            break
    else:
        return f'Error: State file not found for deployment ID {deployment_id_tfstate}'
    
    try:
        subprocess.run(['terraform', 'destroy', '-auto-approve', f'-state={state_file_path}'], check=True)
        instance_data = get_instance_data_from_s3(bucket_name, key_prefix)
        print("Instance data retrieved from S3 when instance is being destroyed:", instance_data)
        
        # Get instance data from S3 instance_data.json
        for instance in instance_data:
            if instance['instance_id'] == instance_id:
                # Generate current timestamp
                current_timestamp = generate_timestamp()
                # Update deletion_time for destroying time
                instance['deletion_time'] = current_timestamp
                instance['instance_state'] = 'Destroyed'

                # Save the updated instance data back to S3
                print("Instance data retrieved from S3 when instance is being destroyed to be saved:", instance_data)
                unwrapped_list = {}
                for dictionary in instance_data:
                    unwrapped_list.update(dictionary)
                save_instance_data_to_s3(unwrapped_list, bucket_name, key_prefix_history)
        #delete instance details from S3
        delete_instance_details_from_s3(instance_id)
        return 'Lightsail instance destroyed successfully'
    except subprocess.CalledProcessError as e:
        return f'Error destroying Lightsail instance : {e}'
    finally:
        os.chdir(original_dir)



if __name__ == '__main__':
    # Save the original directory
    original_dir = os.getcwd()

    bucket_name = 'xmops-data-bucket-team2p'
    key_prefix = 'instance_record/instance_data.json' 
    key_prefix_history = 'instance_record/instance_data_history.json' 
    get_instance_data_from_s3(bucket_name, key_prefix)


    app.run(debug=True, port=5000)

