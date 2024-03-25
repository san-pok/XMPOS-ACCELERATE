from datetime import datetime
import json
import boto3
import botocore
import logging
import os
import time
from flask import jsonify, request
import subprocess
from flask import Flask, render_template
from handler import capture_ec2_and_lightsail_instance_output, generate_timestamp, get_instance_data_from_s3, get_instance_data_from_s3_hist, save_instance_data_to_s3, create_sqlite_database,insert_instance_data_to_sqlite, display_database_data, update_deployment_history


app = Flask(__name__, template_folder='templates')

lightsail = boto3.client('lightsail')

count = 1

# Initialize a global variable to store the total running instances
total_running_instances = 0
message = ''
@app.route('/')
def index():
    message = ''
    instance_data = get_instance_data_from_s3(bucket_name, key_prefix)
    # print("Instance data retrieved from S3 instance_data.json:\n", instance_data)
    deployment_history_data = get_instance_data_from_s3(bucket_name, key_prefix_history )
    
    # # Render template with instance data
    return render_template('index.html', instance_data=instance_data, deployment_history=deployment_history_data, message=message)

# Create S3bucket for storing information of instances
def create_s3_bucket():
    os.chdir('./terraform/s3-bucket')
    # Run terraform to deploy s3
    try:
        # Run Terraform commands to initialize and apply changes
        subprocess.run(['terraform', 'init'], check=True)
        subprocess.run(['terraform', 'apply', '-auto-approve'], check=True)
        return 'S3 bucket created successfully'
    except subprocess.CalledProcessError as e:
        error_message = str(e)
        if "BucketAlreadyOwnedByYou:" in error_message:
            return 'S3 bucket already exists and is owned by you'
        else:
            return f'Error creating S3 bucket: {error_message}'
    finally:
        os.chdir(original_dir)

# User Data is coming from submission button clicked 
@app.route('/deploy-monolith', methods=['POST'])
def submit_form_monolith():
    data = request.data
    print("dummy dummy", data)
    global count
    os.chdir('./terraform/wordpress-ec2')
    try: 
        aws_region = request.json.get('aws-region')
        ami_id = request.json.get('aws-ami')
        instance_type = request.json.get('instance-type')
        key_pair = request.json.get('key_pair')

        # Print the received data
        print("Received data:")
        print("AWS Region:", aws_region)
        print("AMI ID:", ami_id)
        print("Instance Type:", instance_type)
        print("Key Pair:", key_pair)

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

        # #Trigger Terraform deployment
            
        subprocess.run(['terraform', 'init',], check=True)
        subprocess.run(['terraform', 'apply', '-auto-approve'], check=True)  
        # subprocess.run(['terraform', 'plan',f'-state={count}.tfstate'], check=True)
        # # subprocess.run(['terraform', 'init -state={count}.tfstate'], check=True)
        # subprocess.run(['terraform', 'apply', f'-state={count}.tfstate', '-auto-approve'], check=True) 
        # count += 1 
        # terraform_process = subprocess.run(['terraform', 'apply', '-auto-approve'], check=True, capture_output=True, text=True)  
        # # terraform_process = subprocess.run(['terraform', 'apply', '-auto-approve'], check=True, capture_output=True)  
        # terraform_output = terraform_process.stdout

        # # Check if Terraform detected no changes
        # if "No changes" in terraform_output:
        #     print("EC2 instance is already deployed. Skipping saving instance data to S3.")
        #     # return jsonify({'message': 'EC2 instance is already deployed'}), 200
        #     return render_template('index.html', message='EC2 instance is already deployed')
        # else: 
        output_data_of_ec2 = capture_ec2_and_lightsail_instance_output()
        print('incoming data from creation ec2 \n', output_data_of_ec2)
        # Generate current timestamp
        current_timestamp = generate_timestamp()
        # Add deployment type to instance data
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

        # Return instance data and total running instances count
        # return jsonify({'instance_data': instance_data, 'total_running_instances': total_running_instances})
    
        # # Run Terraform apply command with subprocess.Popen
        # terraform_process = subprocess.Popen(['terraform', 'apply', '-auto-approve'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        # # Print output of the command in real-time
        # for line in iter(terraform_process.stdout.readline, b''):
        #     print(line, end='')

        # # Wait for the command to finish and get the return code
        # return_code = terraform_process.wait()

        # # Check if Terraform detected no changes
        # if return_code == 0:
        #     print("Terraform apply succeeded!")

        #     # Retrieve instance data from S3
        #     instance_data = get_instance_data_from_s3(bucket_name, key_prefix)
        #     print("Instance data retrieved from S3:", instance_data)
            
        #     return render_template('index.html', message='Wordpress on EC2 is deployed successfully.')
        # else:
        #     print("Terraform apply failed!")
        #     return render_template('index.html', message='Terraform apply failed!')
    except Exception as e:
        error_message = str(e)
        logging.error(f'Error occurred: {error_message}')  # Log the error
        return f'Error: {error_message}', 500 # Return an error response with status code 500
    finally:
        os.chdir(original_dir)

def get_instance_id():
    try:
        # Run the Terraform apply command and capture the output
        terraform_output = subprocess.run(['terraform', 'apply', '-auto-approve'], capture_output=True, text=True, check=True).stdout
        
        # Split the output by newlines to iterate over each line
        for line in terraform_output.split('\n'):
            # Check if the line contains the instance ID
            if 'instance_id' in line:
                # Extract the instance ID
                instance_id = line.split(':')[-1].strip()
                print('instance ID in get_instance_id(): ', instance_id)
                return instance_id
        
        # If the instance ID is not found, return None
        return None
    except subprocess.CalledProcessError as e:
        # Handle any errors that occur during the Terraform command
        print("Error running Terraform command:", e)
        return None
    
@app.route('/destroy-ec2')
def destroy_ec2():
    os.chdir('./terraform/wordpress-ec2')
    instance_id = request.args.get('instance_id')

    # Run Terraform Command to destroy EC2 instance
    try:
        subprocess.run(['terraform', 'destroy', '-auto-approve'], check=True)
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

@app.route('/deploy-lightsail', methods=['POST'])
def submit_form_lightsail():
    os.chdir('./terraform/wordpress-lightsail')
    try: 
        project_name = request.json.get('project-name')
        aws_region = request.json.get('region')
        platform = request.json.get('platform')
        blueprint = request.json.get('lightsail-blueprint')
        bundle_id = request.json.get('lightsail-bundle')

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

        #Trigger Terraform deployment
        subprocess.run(['terraform', 'init'], check=True)
        subprocess.run(['terraform', 'apply', '-auto-approve'], check=True)  

        output_data_of_ec2 = capture_ec2_and_lightsail_instance_output()
        print('incoming data from creation ec2 \n', output_data_of_ec2)

        # Add deployment type to instance data
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
    os.chdir('./terraform/wordpress-lightsail')
    instance_id = request.args.get('instance_id')
    # Run Terraform Command to destroy EC2 instance
    try:
        subprocess.run(['terraform', 'destroy', '-auto-approve'], check=True)
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

@app.route('/count-instances')
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

            print(f"Region: {region_name}, Lightsail Instance Count: {instance_count_in_region}")
        except botocore.exceptions.ClientError as e: 
            if e.response['Error']['Code'] == 'AccessDeniedException':
                # print(f"Lightsail Instance Access Denied in region {region_name}")
                access_denied_count += 1
            else :
                raise e

    print(f"Total number of Lightsail instances across all regions: {total_instance_count}")
    print(f"Total number of Lightsail instances Access Denied errors: {access_denied_count}")
    return jsonify({'running_instances': total_instance_count})



def refresh_page():
    time.sleep(1)
    return jsonify({'message': 'Page refreshed'})

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

# Route to fetch Lightsail regions
@app.route('/lightsail-regions')
def get_lightsail_regions():
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
    
#route to fetch aws regions 
@app.route('/get-regions', methods=['GET'])
def get_all_regions():
    # Create an EC2 client
    ec2_client = boto3.client('ec2')

    # try:
    #     # Describe all regions
    #     response = ec2_client.describe_regions()

    #     # Extract region names from the response
    #     # all_regions = [region['RegionName'] for region in response['Regions']]
    #     all_regions = [{'DisplayName': region['RegionName'], 'Endpoint': region['Endpoint'], 'RegionName': region['RegionName']} for region in response['Regions']]
    #     print('Regions: ', all_regions)

    #     return jsonify({'regions': all_regions})
    # except Exception as e:
    #     print(f"Error retrieving regions: {e}")
    #     return []
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

        return jsonify({'regions': all_regions})
    except Exception as e:
        print(f"Error retrieving regions: {e}")
        return []

    
@app.route('/amis', methods=['GET'])
def get_amis():
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

@app.route('/instance-types', methods=['GET'])
def get_instance_types():
    try:
        region = request.args.get('region')
        # region = 'ap-southeast-2'
        ec2 = boto3.client('ec2', region_name=region)
        # ec2 = boto3.client('ec2')
        # Retrieve instance types for the specified region
        # instance_types = ec2.describe_instance_types()
        instance_types = ec2.describe_instance_type_offerings()
        # Retrieve instance types for the specified region
        # instance_types = ec2.describe_instance_types()['InstanceTypes']

        # Extract instance type names from the response
        instance_type_names = [instance['InstanceType'] for instance in instance_types['InstanceTypeOfferings']]

        # instance_details = []
        # for instance_type in instance_types:
        #     details = {
        #         'InstanceType': instance_type['InstanceType'],
        #         'VCpus': instance_type['VCpuInfo']['DefaultVCpus'],
        #         'MemoryInfo': instance_type['MemoryInfo']['SizeInMiB'],
        #         'GpuInfo': instance_type.get('GpuInfo', {}),
        #         'StorageInfo': instance_type['InstanceStorageSupported']
        #     }
        #     instance_details.append(details)

        # Sort instance types in ascending order
        sorted_instance_types = sorted(instance_type_names)

        # Filter instance types based on FreeTierEligible attribute
        # free_tier_instance_types = [instance_type for instance_type in instance_types if instance_type.get('FreeTierEligible', True)]

        # return jsonify({'instance_types': instance_type_names, 'Free_instance_types': free_tier_instance_types} )
        return jsonify({'instance_types': sorted_instance_types})
    except Exception as e:
        return jsonify({'error': str(e)})
    
@app.route('/count-running-ec2-instances')
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

                print(f"Region: {region_name}, Running EC2 Instance Count: {running_instance_count_in_region}")
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
    
@app.route('/existing_key_pairs', methods=['GET'])
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
    
@app.route('/generate_key_pair', methods=['POST'])
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

    
    
if __name__ == '__main__':

    # Save the original directory
    original_dir = os.getcwd()
    # database_name = 'team2.db'

    bucket_name = 'xmops-data-bucket-team2'
    key_prefix = 'instance_record/instance_data.json' 
    key_prefix_history = 'instance_record/instance_data_history.json' 

    # Creating S3 Bucket when
    create_s3_bucket()
    # create_sqlite_database(database_name)
    # display_database_data(database_name)
    get_instance_data_from_s3(bucket_name, key_prefix)
    # get_instance_data_from_s3_hist(bucket_name, key_prefix_history)

    app.run(debug=True, port=4000)
    # refresh_page()