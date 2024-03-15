from datetime import datetime
import json
import boto3
import logging
import os
import time
from flask import jsonify, request
import subprocess
from flask import Flask, render_template
from handler import capture_ec2_and_lightsail_instance_output, generate_timestamp, get_instance_data_from_s3, get_instance_data_from_s3_hist, save_instance_data_to_s3, create_sqlite_database,insert_instance_data_to_sqlite, display_database_data, update_deployment_history


app = Flask(__name__, template_folder='templates')

lightsail = boto3.client('lightsail')
# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG)
# Initialize an empty list to store deployment history
# deployment_history = []
# # Save the original directory
# original_dir = os.getcwd()

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
    os.chdir('./terraform/wordpress-ec2')
    try: 
        aws_region = request.json.get('region')
        ami_id = request.json.get('image')
        instance_type = request.json.get('instance-type')

        # Print the received data
        print("Received data:")
        print("AWS Region:", aws_region)
        print("AMI ID:", ami_id)
        print("Instance Type:", instance_type)

        # Get the absolute path to terraform.auto.tfvars for debugging
        tfvars_file = os.path.abspath('terraform.auto.tfvars')
        print("Absolute path to terraform.auto.tfvars:", tfvars_file)

        # Write the user-submitted values to a TFVars file
        # with open('./terraform/wordpress-ec2/terraform.auto.tfvars', 'w') as f:
        with open('terraform.auto.tfvars', 'w') as f:

            f.write(f'aws_region = "{aws_region}"\n')
            f.write(f'ami_id = "{ami_id}"\n')
            f.write(f'instance_type = "{instance_type}"\n')

        #Trigger Terraform deployment
        subprocess.run(['terraform', 'init'], check=True)
        terraform_process = subprocess.run(['terraform', 'apply', '-auto-approve'], check=True, capture_output=True, text=True)  
        # terraform_process = subprocess.run(['terraform', 'apply', '-auto-approve'], check=True, capture_output=True)  
        terraform_output = terraform_process.stdout

        # Check if Terraform detected no changes
        if "No changes" in terraform_output:
            print("EC2 instance is already deployed. Skipping saving instance data to S3.")
            # return jsonify({'message': 'EC2 instance is already deployed'}), 200
            return render_template('index.html', message='EC2 instance is already deployed')
        else: 
            output_data_of_ec2 = capture_ec2_and_lightsail_instance_output()
            print('incoming data from creation ec2 \n', output_data_of_ec2)
            # Generate current timestamp
            current_timestamp = generate_timestamp()
            # Add deployment type to instance data
            output_data_of_ec2['deployment_type'] = 'Monolith'
            # Add timestamp to instance data
            output_data_of_ec2['creation_time'] = current_timestamp
            output_data_of_ec2['deletion_time'] = ''

            # Update the total running instances counter
            # total_running_instances += 1
            save_instance_data_to_s3(output_data_of_ec2, bucket_name, key_prefix)
            # save_instance_data_to_s3(output_data_of_ec2, bucket_name, key_prefix_history)
            # Update the total running instances counter
            # total_running_instances += 1
            

        instance_data = get_instance_data_from_s3(bucket_name, key_prefix)
        # print("Instance data retrieved from S3:", instance_data)
        # Add the new entry to the deployment history for instance creation
       
        # refresh_page()
        return jsonify(instance_data), 200, {'message': 'Wordpress on EC2 is deployed successfully.'}

        # Return instance data and total running instances count
        # return jsonify({'instance_data': instance_data, 'total_running_instances': total_running_instances})
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
    print('selected Platform in bundle', platform)
    try:
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
    


    
if __name__ == '__main__':

    # Save the original directory
    original_dir = os.getcwd()
    database_name = 'team2.db'

    

    bucket_name = 'xmops-data-bucket-team2'
    key_prefix = 'instance_record/instance_data.json' 
    key_prefix_history = 'instance_record/instance_data_history.json' 

    # Creating S3 Bucket when
    create_s3_bucket()
    create_sqlite_database(database_name)
    # display_database_data(database_name)
    get_instance_data_from_s3(bucket_name, key_prefix)
    # get_instance_data_from_s3_hist(bucket_name, key_prefix_history)

    app.run(debug=True, port=4000)
    # refresh_page()