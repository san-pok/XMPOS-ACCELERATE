from cmath import e
import subprocess
import json
import boto3

def capture_ec2_and_lightsail_instance_output():
    output = subprocess.check_output(['terraform', 'output', '-json']).decode('utf-8')
    output_json = json.loads(output)

    # # Filter and transform the received data to align with proposed data
    # received_data = {
    #     'ami_id': output_json['ami_id']['value'],
    #     'availability_zone': output_json['availability_zone']['value'],
    #     'instance_id': output_json['instance_id']['value'],
    #     'instance_region': output_json['instance_region']['value'],
    #     'instance_state': output_json['instance_state']['value'],
    #     'instance_type': output_json['instance_type']['value'],
    #     'key_name': output_json['key_name']['value'],
    #     'public_ip': output_json['public_ip']['value']
    # }

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

    formatted_received_data = json.dumps(received_data, indent=4)
    return (formatted_received_data)



def save_instance_data_to_s3(data, bucket_name, key):
    # Initialize an S3 client
    s3 = boto3.client('s3')
    
    try:
        # Upload the JSON data to the specified S3 bucket and key
        s3.put_object(Bucket=bucket_name, Key=key, Body=data)
        print("Key is this: .", key)
        print("Data saved to S3 successfully.", data)
    except Exception as e:
        print(f"Error saving data to S3: {e}")


def get_instance_data_from_s3(bucket_name, key):
    # Initialize an S3 client
    s3 = boto3.client('s3')

    try:
        # Retrieve the Json data from S3
        response = s3.get_object(Bucket=bucket_name, Key=key)
        data = response['Body'].read().decode('utf-8')
        instance_data = json.loads(data)
        return instance_data
    except:
        print(f"Error retriving instance json datta from S3: {e} ")
        return[]