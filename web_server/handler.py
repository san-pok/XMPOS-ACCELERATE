from cmath import e
import csv
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib
import sqlite3
import subprocess
import json
import time
import uuid
import boto3
from flask import Flask, jsonify


def capture_ec2_and_lightsail_instance_output(state_file_path):
    output = subprocess.check_output(['terraform', 'output', '-json', f'-state={state_file_path}']).decode('utf-8')
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
        'public_ip': output_json.get('public_ip', {}).get('value', 'N/A'),
        # 'bundle_id': output_json.get('lightsail_instance_attributes.bundle_id', {}).get('value', 'N/A'),
        # 'bundle_blueprint_id': output_json.get('lightsail_instance_attributes.bundle_blueprint_id', {}).get('value', 'N/A'),
        # 'cpu_count': output_json.get('lightsail_instance_attributes.cpu_count', {}).get('value', 'N/A')
        'project_id': output_json.get('project_id', {}).get('value', 'N/A'),
        'bundle_id': output_json.get('bundle_id', {}).get('value', 'N/A'),
        'blueprint_id': output_json.get('blueprint_id', {}).get('value', 'N/A'),
        'cpu_count': output_json.get('cpu_count', {}).get('value', 'N/A')
    }

    # # Determine the deployment tyope based on the instance type
    # instance_type = received_data.get('instance_type')
    # if instance_type.startwith

    # formatted_received_data = json.dumps(received_data, indent=4)
    return (received_data)


def save_instance_data_to_s3(new_data, bucket_name, key):
    # Initialize an S3 client
    s3 = boto3.client('s3')
  
    try:
        # Retrieve existing data from S3 or initialize as empty list if not found
        try:
            response = s3.get_object(Bucket=bucket_name, Key=key)
            # print("Response data : \n", response)
            existing_data = response['Body'].read().decode('utf-8')
            # print("Existing data: \n", existing_data)
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
        # print("Data saved to S3 successfully. Updated data:", updated_data)
        print("Key for the new JSON file:", key)
        
    except Exception as e:
        print(f"Error saving data to S3: {e}")

def generate_timestamp():
    """Generate and return the current timestamp."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def update_deployment_history():
    # Define the new deployment history entry
    new_entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'type': 'EC2',
        'status': 'Destroyed'
    }
    deployment_history = [
        {
            'timestamp': '2024-02-28 10:00:00',
            'type': 'Lightsail',
            'status': 'Completed'
        },
        {
            'timestamp': '2024-02-28 11:00:00',
            'type': 'EC2',
            'status': 'Destroyed'
        },
    # More deployment entries can be added here
    ]
    # Load existing deployment history from a file or database
    # Update the deployment history with the new entry
    # Save the updated deployment history back to the file or database
    # For demonstration purposes, let's assume deployment history is stored in a list
    deployment_history.append(new_entry)

    # Optionally, you can save the updated deployment history to S3 bucket

    # Return the updated deployment history
    return deployment_history
    

def get_instance_data_from_s3(bucket_name, key):
    # Initialize an S3 client
    s3 = boto3.client('s3')
    try:
        # print("In the get instance data from s3 function IN TRY: \n")
        # Retrieve the Json data from S3
        response = s3.get_object(Bucket=bucket_name, Key=key)
        instance_data = json.loads(response['Body'].read().decode('utf-8'))
        # print("instance data from s3 bucket get_instance_data_from_s3 Function: \n",instance_data)
        return instance_data
        
    except:
        print(f"Error retriving instance json datta from S3: {e} ")
        return[]
    
def get_instance_data_from_s3_hist(bucket_name, key_prefix_history):
    # Initialize an S3 client
    s3 = boto3.client('s3')
    try:
        print("In the get instance data from s3 function IN TRY: \n")
        # Retrieve the Json data from S3
        response = s3.get_object(Bucket=bucket_name, Key=key_prefix_history)
        instance_data = json.loads(response['Body'].read().decode('utf-8'))
        print("instance data from s3 bucket it is in get_instance_data_from_s3:\n",instance_data)
        return instance_data
        
    except:
        print(f"Error retriving instance json datta from S3: {e} ")
        return[]
    
    

def create_sqlite_database(database_name):
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        print("Database name::::: from handler.py ", database_name)
        # Create table for instances
        cursor.execute('''CREATE TABLE IF NOT EXISTS instances (
                            id INTEGER PRIMARY KEY,
                            ami_id TEXT,
                            availability_zone TEXT,
                            instance_id TEXT,
                            instance_region TEXT,
                            instance_state TEXT,
                            instance_type TEXT,
                            key_name TEXT,
                            public_ip TEXT
                        )''')

        # Commit changes and close connection
        conn.commit()
        conn.close()
        print("Database and table created successfully.")
        list_tables(database_name)
    except sqlite3.Error as e:
        print("Error creating database and table:", e)

   

def display_database_data(database_name):
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    try: 
        # Execute a SELECT query to fetch all rows from the instances table
        cursor.execute("SELECT * FROM instances")
        rows = cursor.fetchall()
        # Construct a list of dictionaries representing each row
        data = []
        for row in rows:
            record = {
                "id": row[0],
                "ami_id": row[1],
                "availability_zone": row[2],
                "instance_id": row[3],
                "instance_region": row[4],
                "instance_state": row[5],
                "instance_type": row[6],
                "key_name": row[7],
                "public_ip": row[8]
            }
            data.append(record)
            
        json_data = json.dumps(data)
        print("Json data",data)
        return (json_data)
        # Close the connection
    except sqlite3.Error as e:
        print ("Error Fetching data from display data", e)
        return None
    finally:
        conn.close()

    
def insert_instance_data_to_sqlite(database_name, data):
    # Connect to SQLite database
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    # Check if the table 'instances' exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='instances'")
    table_exists = cursor.fetchone()
    print("exisiting table: ", table_exists )
    print("In the insert_instance_data_to_sqlite, the data is :\n", data)

    if not table_exists:
            # Table does not exist, create it
            print ("Instance table is not existed:\n")
            create_sqlite_database(database_name)

    print(data['instance_id'], data['instance_type'], data['ami_id'],
                    data['availability_zone'], data['instance_region'],
                    data['instance_state'], data['key_name'], data['public_ip'])
    # Insert data into the instances table
    try:
        # Insert data into the instances table
        cursor.execute("INSERT INTO instances (ami_id, availability_zone, instance_id, instance_region, instance_state, instance_type, key_name, public_ip) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (data['ami_id'], data['availability_zone'], data['instance_id'],
                        data['instance_region'], data['instance_state'],
                        data['instance_type'], data['key_name'], data['public_ip']))
        
      
        print("try dotor baina")   
        conn.commit()
        return jsonify({})
    except Exception as e:
        print(f"Error inserting data: {e}")
        # return False
    finally:
        conn.close()

def list_tables(database_name):
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in the database:")
    for table in tables:
        print(table[0])
    conn.close() 

def generate_unique_id():
    # Get current timestamp
    timestamp_ms = int(time.time() * 100)
    # Convert timestamp to a string and return its as the unique ID
    return str(timestamp_ms)



def prepare_eamil(bucket_name, key_prefix_history, emailInput):
    smtp_port = 587
    smtp_server = "smtp.gmail.com"

    sender_email = "btbyambadorj@gmail.com"
    sender_password = 'uezzvoajklvxrksi'

    # receiver_email = ["herosteelfixing@gmail.com, 103133909@student.swin.edu.au, adiyabaatarmiigaa976@gmail.com "]
    receiver_email = [emailInput ]
    # name the email subject
    subject = "XMOPTS USAGE REPORT with attachments!!"

    print(f'receiver_email: {receiver_email}')
    print(f'bucket_name: {bucket_name}')
    print(f'key_prefix_history: {key_prefix_history}')


    deployment_history_data = get_instance_data_from_s3(bucket_name, key_prefix_history)
    # print(f'deployment_history_data: {deployment_history_data}')
    # Generate CSV
    csv_filename = generate_csv(deployment_history_data )

    # # Generate CSV
    # pdf_data = generate_pdf(deployment_history_data,)
    # print (pdf_data)
    
    for person in receiver_email:

        # Make the body of the email
        body = f"""
        Hello Customer, 
        XMOPS Team 2 are sending your deployment history. 
        Please find the attached

        Best regards 
        Team 2
        """

        # make a MIME object to define parts of the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = person
        msg['Subject'] = subject

        # Attach the body of the message
        msg.attach(MIMEText(body, 'plain'))

        # Define the file to attach
        filename = csv_filename

        # Open the file in python as a binary
        attachment= open(filename, 'rb')  # r for read and b for binary

        # Encode as base 64
        attachment_package = MIMEBase('application', 'octet-stream')
        attachment_package.set_payload((attachment).read())
        encoders.encode_base64(attachment_package)
        attachment_package.add_header('Content-Disposition', "attachment; filename= " + filename)
        msg.attach(attachment_package)

        # Cast as string
        text = msg.as_string()

        # Connect with the server
        print("Connecting to server...")
        TIE_server = smtplib.SMTP(smtp_server, smtp_port)
        TIE_server.starttls()
        TIE_server.login(sender_email, sender_password)
        print("Succesfully connected to server")
        print()

        # Send emails to "person" as list is iterated
        print(f"Sending email to: {person}...")
        TIE_server.sendmail(sender_email, person, text)
        print(f"Email sent to: {person}")
        print()

    # Close the port
    TIE_server.quit()
    os.remove(filename)

def generate_csv(data):
    # Get all unique keys across all dictionaries in `data`
    all_keys = set().union(*(d.keys() for d in data))

    # Fill in missing keys with None
    for d in data:
        for key in all_keys:
            d.setdefault(key, None)
    
    filename = "deployment_hist.csv "       
    with open(filename, 'w', encoding='utf8', newline='') as output_file:
        fc = csv.DictWriter(output_file, 
                        fieldnames=data[0].keys(),

                        )
        fc.writeheader()
        fc.writerows(data)

    return filename



