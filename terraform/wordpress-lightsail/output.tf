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

# output "instance_region" {
#   description = "Region of the Lightsail instance"
#   value       = aws_lightsail_instance.lightsail_instance.location.availability_zone.regionName
# }

# output "instance_state" {
#   description = "Lightsail Instance State"
#   value = aws_lightsail_instance.lightsail_instance.state.name
# }

# output "instance_type" {
#   description = "Lightsail Instance Type"
#   value = aws_lightsail_instance.lightsail_instance.instance_type
# }

output "key_name" {
    value = aws_lightsail_instance.lightsail_instance.key_pair_name
}

output "public_ip" {
  value = aws_lightsail_static_ip.static_ip.ip_address
}

output "project_id" {
  description = "Lightsail Instance ID"
  value       = "id=${aws_lightsail_instance.lightsail_instance.id}"
}

output "bundle_id" {
  description = "Lightsail Instance ID"
  value       = "${aws_lightsail_instance.lightsail_instance.bundle_id}"
}

output "blueprint_id" {
  description = "Lightsail Instance ID"
  value       = "${aws_lightsail_instance.lightsail_instance.blueprint_id}"
}

output "cpu_count" {
  description = "Lightsail Instance ID"
  value       = "${aws_lightsail_instance.lightsail_instance.cpu_count} cores"
}



output "lightsail_instance_attributes" {
  value = {
    # bundle_id        = aws_lightsail_instance.lightsail_instance.bundle_id
    # region           = "us-east-1"  # Adjust accordingly based on your region
    # availability_zone = "us-east-1a" # Adjust accordingly based on your availability zone
    instance_id      = aws_lightsail_instance.lightsail_instance.id
    project_name     = aws_lightsail_instance.lightsail_instance.name
    # state            = aws_lightsail_instance.gitlab_test.state.name
    # location         = aws_lightsail_instance.gitlab_test.location.availabilityZone
    bundle_id         = aws_lightsail_instance.lightsail_instance.bundle_id
    blueprint_id         = aws_lightsail_instance.lightsail_instance.blueprint_id
    availability_zone         = aws_lightsail_instance.lightsail_instance.availability_zone
    key_pair_name         = aws_lightsail_instance.lightsail_instance.key_pair_name
    user_data         = aws_lightsail_instance.lightsail_instance.user_data
    cpu_count= aws_lightsail_instance.lightsail_instance.cpu_count
    lightsail_id= aws_lightsail_instance.lightsail_instance.id
    lightsail_arn= aws_lightsail_instance.lightsail_instance.arn
    lightsail_created_at= aws_lightsail_instance.lightsail_instance.created_at
    # lightsail_add_on= aws_lightsail_instance.gitlab_test.add_on
    # lightsail_add_on_type= aws_lightsail_instance.gitlab_test.add_on.type

    # lightsail_type= aws_lightsail_instance.gitlab_test.type
    # Add more attributes as needed
  }
}