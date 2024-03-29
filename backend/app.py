# from flask import Flask, request, jsonify
# import boto3
# from flask_cors import CORS  # Make sure you have flask-cors installed

# # # Initialize Flask app
# # app = Flask(__name__)
# # CORS(app)  # Enable CORS for all routes
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import boto3

# app = Flask(__name__)
# CORS(app, resources={r"/*": \{"origins": "*"}}, supports_credentials=True)

# # Your existing Flask app setup and routes


# # AWS Cognito settings (Replace these with your actual values)
# AWS_REGION = "us-east-1"
# COGNITO_USER_POOL_ID = "<YourUserPoolId>"
# COGNITO_APP_CLIENT_ID = "<YourAppClientId>"
# COGNITO_APP_CLIENT_SECRET = "<YourAppClientSecret>"  # If you have a client secret

# # Initialize Boto3 Cognito Identity Provider client
# cognito_client = boto3.client('cognito-idp', region_name=AWS_REGION)


from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
from dotenv import load_dotenv
import os
import logging
from dotenv import load_dotenv
load_dotenv()


load_dotenv()

# app = Flask(__name__)
# # CORS(app)
# CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app = Flask(__name__)
# Apply CORS to all routes and origins
CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

AWS_REGION = os.getenv('AWS_REGION')
COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
COGNITO_APP_CLIENT_ID = os.getenv('COGNITO_APP_CLIENT_ID')

cognito_client = boto3.client('cognito-idp', region_name=AWS_REGION)

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

if __name__ == '__main__':
    app.run(debug=True)
