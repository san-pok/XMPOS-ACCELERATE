provider "aws" {
  region = "ap-southeast-2"  # Manually setting the region
}

resource "aws_lightsail_key_pair" "my_key" {
  name       = var.key_pair_name
  public_key = var.ssh_key
}

resource "aws_lightsail_instance" "wordpress_instance" {
  name              = var.instance_name
  availability_zone = "ap-southeast-2a"  # Ensure this matches your provider region
  blueprint_id      = var.blueprint
  bundle_id         = var.bundle_id
  key_pair_name     = aws_lightsail_key_pair.my_key.name

  tags = {
    Name = "WordPressInstance"
  }
}

