## Creates an AWS lightsail instance
resource "aws_lightsail_instance" "lightsail_instance" {
  name = var.project_name
  availability_zone = "${var.aws_region}a"
  blueprint_id = var.lightsail_blueprints["wordpress"]
  bundle_id = var.bundle_id

  ## Provisioner to retrieve Wordpress admin user and password
# provisioner "remote-exec" {
#     inline = [
#         "echo 'Username: $(cat ~/bitnami_credentials | grep 'Username:' | cut -d ' -f2)'",
#         "echo 'Password: $(cat ~/bitnami_credentials | grep 'Password:' | cut -d ' -f2)'"
#     ]

#     connection {
#         type = "ssh"
#         host = aws_lightsail_instance.lightsail_instance.public_ip_address
#         user = "bitnami"
#         private_key = tls_private_key.ssh_key.private_key_pem
#     }

# }
}

## Create static public IP on Lightsail
resource "aws_lightsail_static_ip" "static_ip" {
  name = "${var.project_name}_static_ip" ## Name of static IP in AWS
}

## Attaches static IP address to Lightsail Instance
resource "aws_lightsail_static_ip_attachment" "static_ip_attach" {
  static_ip_name = aws_lightsail_static_ip.static_ip.id
  instance_name = aws_lightsail_instance.lightsail_instance.id
}

## Generate ssh key pair
resource "tls_private_key" "ssh_key" {
  algorithm = "RSA"
  rsa_bits = 2048
}





