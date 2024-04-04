import csv
from datetime import datetime
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
import json
# from msilib import Table
import os
import ssl
import smtplib
import subprocess
import tempfile
import boto3
from flask import app, flash, jsonify, request
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask_mail import Mail, Message
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors


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
        'public_ip': output_json.get('public_ip', {}).get('value', 'N/A'),
        # 'bundle_id': output_json.get('lightsail_instance_attributes.bundle_id', {}).get('value', 'N/A'),
        # 'bundle_blueprint_id': output_json.get('lightsail_instance_attributes.bundle_blueprint_id', {}).get('value', 'N/A'),
        # 'cpu_count': output_json.get('lightsail_instance_attributes.cpu_count', {}).get('value', 'N/A')
        'project_id': output_json.get('project_id', {}).get('value', 'N/A'),
        'bundle_id': output_json.get('bundle_id', {}).get('value', 'N/A'),
        'blueprint_id': output_json.get('blueprint_id', {}).get('value', 'N/A'),
        'cpu_count': output_json.get('cpu_count', {}).get('value', 'N/A')
    }
    # formatted_received_data = json.dumps(received_data, indent=4)
    return (received_data)

def generate_timestamp():
    """Generate and return the current timestamp."""
    d1 = datetime.now()
    print ("it is generating Datetime.now() ", d1)
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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
        
    except Exception as e: 
        print(f"Error retriving instance json datta from S3: {e} ")
        return[]
    

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

def generate_pdf(data):
    # Create a PDF document
    pdf_filename = "deployment_hist.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)

    # Create a table from the data
    table_data = [list(data[0].keys())] + [[str(value) for value in row.values()] for row in data]
    table = Table(table_data)

    # Add style to the table
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    table.setStyle(style)

    # Add the table to the PDF document
    doc.build([table])

    return pdf_filename

