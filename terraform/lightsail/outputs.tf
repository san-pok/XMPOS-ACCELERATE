output "instance_public_ip" {
  value       = aws_lightsail_instance.wordpress_instance.public_ip_address
  description = "The public IP address of the deployed Lightsail instance."
}

output "wordpress_setup_url" {
  value       = "http://${aws_lightsail_instance.wordpress_instance.public_ip_address}/wp-admin/install.php"
  description = "URL to set up the WordPress instance."
}
