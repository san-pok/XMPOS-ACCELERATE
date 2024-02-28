import json
import os
import time
from flask import jsonify
import subprocess
from flask import Flask, render_template
from handler import capture_ec2_and_lightsail_instance_output, get_instance_data_from_s3, save_instance_data_to_s3

app = Flask(__name__)

# # Save the original directory
# original_dir = os.getcwd()

@app.route('/')
def index():
    
    instance_data = get_instance_data_from_s3(bucket_name, key_prefix)
    # instance_data = json.dumps(instance_data, indent=4)
    print("Instance data retrieved from S3:", instance_data)
    # Render template with instance data
    return render_template('index.html', instance_data=instance_data)
    # return render_template('index.html',)
    # return render_template('index.html')

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
        return f'Error creating S3 bucket: {e}'
    finally:
        os.chdir(original_dir)


@app.route('/worpress-install-ec2')
def create_ec2():
    os.chdir('./terraform/wordpress-ec2')

    #Run Terraform Command
    try:
        subprocess.run(['terraform', 'init'], check=True)
        subprocess.run(['terraform', 'apply', '-auto-approve'], check=True)

        output_data_of_ec2 = capture_ec2_and_lightsail_instance_output()
        print(output_data_of_ec2)
        # save_instance_data_to_s3(output_data)

        # Save captured data to S3 bucket
        # bucket_name = 'xmops-data-bucket-team2'
        # key = 'instance_data.json'
        save_instance_data_to_s3(output_data_of_ec2, bucket_name, key_prefix)

        instance_data = get_instance_data_from_s3(bucket_name, key_prefix)
        print("Instance data retrieved from S3:", instance_data)
        refresh_page()
        return jsonify(instance_data)  # Return instance data as JSON response

        # Render template with instance data
        # return render_template('index.html', instance_data=instance_data)

        # return 'Wordpress installed on EC2 instance successfully.'
    except subprocess.CalledProcessError as e:
        return f'Error Installing Wordpress on EC2 instance : {e}'
    finally:
        os.chdir(original_dir)
    
    
@app.route('/destroy-ec2')
def destroy_ec2():
    os.chdir('./terraform/wordpress-ec2')

    # Run Terraform Command to destroy EC2 instance
    try:
        subprocess.run(['terraform', 'destroy', '-auto-approve'], check=True)
        return 'EC2 instance destroyed successfully'
    except subprocess.CalledProcessError as e:
        return f'Error destroying EC2 instance : {e}'
    finally:
        os.chdir(original_dir)
    

@app.route('/wordpress-install-lightsail')
def create_lightsail():
    os.chdir('./terraform/wordpress-lightsail')

    # Run Terraform Command
    try:
        subprocess.run(['terraform', 'init'], check=True)
        subprocess.run(['terraform', 'apply', '-auto-approve'], check=True)

        output_data_of_ec2 = capture_ec2_and_lightsail_instance_output()
        print(output_data_of_ec2)
        # save_instance_data_to_s3(output_data)

        # Save captured data to S3 bucket
        # bucket_name = 'xmops-data-bucket-team2'
        # key = 'instance_data.json'
        save_instance_data_to_s3(output_data_of_ec2, bucket_name, key_prefix)

        instance_data = get_instance_data_from_s3(bucket_name, key_prefix)
        print("Instance data retrieved from S3:", instance_data)
        refresh_page()
        return jsonify(instance_data)  # Return instance data as JSON response

    except subprocess.CalledProcessError as e:
        return f'Error Installing Wordpress on Lightsail instance : {e}'
    
    except FileNotFoundError as e:
        return f'File not found error: {e}'

    except Exception as e:
        return f'Error: {e}'
    finally:
        os.chdir(original_dir)
    
@app.route('/destroy-lightsail')
def destroy_lightsail():
    os.chdir('./terraform/wordpress-lightsail')
    # Run Terraform Command to destroy EC2 instance
    try:
        subprocess.run(['terraform', 'destroy', '-auto-approve'], check=True)
        return 'Lightsail instance destroyed successfully'
    except subprocess.CalledProcessError as e:
        return f'Error destroying Lightsail instance : {e}'
    finally:
        os.chdir(original_dir)


def refresh_page():
    time.sleep(1)
    return jsonify({'message': 'Page refreshed'})


# @app.route('/get-instance-data')
# def get_instance_data_from_s3():
#     #initialize
    
if __name__ == '__main__':

    # Save the original directory
    original_dir = os.getcwd()

    bucket_name = 'xmops-data-bucket-team2'
    key_prefix = 'instance_record/instance_data.json' 

    # Creating S3 Bucket when
    create_s3_bucket()
    # get_instance_data_from_s3(bucket_name, key_prefix)

    app.run(debug=True, port=4000)
    # refresh_page()