output "cognito_user_pool_id" {
  value = aws_cognito_user_pool.main.id
}

output "cognito_user_pool_client_id" {
  value = aws_cognito_user_pool_client.app_client.id
}

# If you're outputting the region, it might look something like this:
output "region" {
  value = "ap-southeast-2" 
}
