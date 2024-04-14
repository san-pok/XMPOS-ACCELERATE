provider "aws" {
  region = var.region
}

resource "aws_cognito_user_pool" "main" {
  name = "${var.project_name}-user-pool"

  mfa_configuration = "OPTIONAL" # or "ON" if you require MFA for all users

  software_token_mfa_configuration {
    enabled = true
  }

  sms_authentication_message = "Your authentication code is {####}."
  sms_verification_message = "Your verification code is {####}."

  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

 
}

 

//client settings
resource "aws_cognito_user_pool_client" "app_client" {
  name                                 = "${var.project_name}-app-client"
  user_pool_id                         = aws_cognito_user_pool.main.id
  generate_secret                      = false
  explicit_auth_flows                  = ["ADMIN_NO_SRP_AUTH", "USER_PASSWORD_AUTH"]
  allowed_oauth_flows                  = ["code", "implicit"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes                 = ["phone", "email", "openid", "profile", "aws.cognito.signin.user.admin"]
  callback_urls                        = ["https://www.example.com/callback"]
  logout_urls                          = ["https://www.example.com/logout"]

 
}
