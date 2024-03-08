output "EIP" {
  description = "Lightsail EIP"
  value = aws_lightsail_static_ip.static_ip.ip_address
}

output "ssh_private_key" {
  description = "SSH Private Key"
  value       = tls_private_key.ssh_key.private_key_pem
  sensitive = true
}


## Output the WordPress admin username and password
# output "wordpress_credentials" {
#   description = "WordPress Admin Credentials"
#   //value       = file("wordpress_credentials")
#   value       = aws_lightsail_instance.lightsail_instance.public_ip_address
# }

output "ami_id" {
  value = aws_lightsail_instance.lightsail_instance.id
}

output "availability_zone" {
  value = aws_lightsail_instance.lightsail_instance.availability_zone
}

# output "instance_id" {
#   value = aws_lightsail_instance.lightsail_instance.id
# }

# output "instance_region" {
#   value = data.aws_region.current.name
# }

# output "instance_state" {
#   value = aws_lightsail_instance.lightsail_instance.instance_state
# }

# output "instance_type" {
#   value = aws_lightsail_instance.lightsail_instance.instance_type
# }

output "key_name" {
    value = aws_lightsail_instance.lightsail_instance.key_pair_name
}

output "public_ip" {
  value = aws_lightsail_static_ip.static_ip.ip_address
}

output "instance_id" {
  description = "Lightsail Instance ID"
  value       = "id=${aws_lightsail_instance.lightsail_instance.id}"
}

