from cmath import e
import subprocess
import json
import uuid
import boto3

def capture_ec2_and_lightsail_instance_output():
    output = subprocess.check_output(['terraform', 'output', '-json']).decode('utf-8')
    output_json = json.loads(output)

    # Extracting values with graceful handling of missing keys
    received_data = {
        'ami_id': output_json.get('ami_id', {}).get('value', 'N/A'),
        'availability_zone': output_json.get('availability_zone', {}).get('value', 'N/A'),
        'instance_id': output_json.get('instance_id', {}).get('value', 'N/A'),
        'instance_region': output_json.get('instance_region', {}).get('value', 'N/A'),
        'instance_state': output_json.get('instance_state', {}).get('value', 'N/A'),
        'instance_type': output_json.get('instance_type', {}).get('value', 'N/A'),
        'key_name': output_json.get('key_name', {}).get('value', 'N/A'),
        'public_ip': output_json.get('public_ip', {}).get('value', 'N/A')
    }

    # formatted_received_data = json.dumps(received_data, indent=4)
    return (received_data)



def save_instance_data_to_s3(new_data, bucket_name, key):
    # Initialize an S3 client
    s3 = boto3.client('s3')
  
    try:
        # Retrieve existing data from S3 or initialize as empty list if not found
        try:
            response = s3.get_object(Bucket=bucket_name, Key=key)
            existing_data = response['Body'].read().decode('utf-8')
            print("Existing data: \n", existing_data)
            existing_data_list = json.loads(existing_data)
        except s3.exceptions.NoSuchKey:
            # Key doesn't exist yet, initialize as empty list
            existing_data_list = []

        # Append new data to the existing list
        existing_data_list.append(new_data)
        print("New data:\n", new_data)

        # Upload the updated JSON data to the specified S3 bucket and key
        updated_data = json.dumps(existing_data_list, indent=4)
        s3.put_object(Bucket=bucket_name, Key=key, Body=updated_data.encode('utf-8'))
        print("Data saved to S3 successfully. Updated data:", updated_data)
        print("Key for the new JSON file:", key)
        
    except Exception as e:
        print(f"Error saving data to S3: {e}")
    



def get_instance_data_from_s3(bucket_name, key):
    # Initialize an S3 client
    s3 = boto3.client('s3')
    try:
        print("In the get instance data from s3 function IN TRY: \n")
        # Retrieve the Json data from S3
        response = s3.get_object(Bucket=bucket_name, Key=key)
        instance_data = json.loads(response['Body'].read().decode('utf-8'))
        print("instance data from s3 bucket: \n",instance_data)
        return instance_data
        
    except:
        print(f"Error retriving instance json datta from S3: {e} ")
        return[]