from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
import subprocess
import os

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
            if key.endswith('_cpu') or key.endswith('_memory'):
                if not value.isdigit():
                    errors[key] = 'Please enter a numeric value'

        if errors:
            return jsonify({'error': 'Form validation failed', 'errors': errors}), 400
        else:
            # write the data to terraform.auto.tfvars file
            with open('terraform.auto.tfvars', 'w') as f:
                for key, value in data.items():
                    # Exclude double quotations for numeric fields
                    if key.endswith('_cpu') or key.endswith('_memory'):
                        f.write(f"{key} = {value}\n")
                    else:
                        f.write(f"{key} = \"{value}\"\n")

            # Trigger infrastructure deployment
            response = deploy_infrastructure()

            if response[1] == 200:  # Check the status code
                return jsonify({'message': 'Form validation successful and infrastructure deployment triggered'}), 200
            else:
                return jsonify({'error': 'Failed to trigger infrastructure deployment after form validation'}), 500

    except Exception as e:
        error_message = f'Error validating form data: {str(e)}'
        return jsonify({'error': error_message}), 500
if __name__ == '__main__':
    app.run(debug=True)
