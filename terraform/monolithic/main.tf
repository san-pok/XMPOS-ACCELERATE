provider "aws" {
  region = var.aws_region
}
data "aws_region" "current" {}


data "aws_security_groups" "existing_sg" {
  filter {
    name   = "group-name"
    values = [var.security_group_name]
  }
}

# For mysql_php_apache2.sh
data "local_file" "mysql_template_file" {
  filename = "${path.module}/ubuntu_user_data/mysql_php_apache2.sh"
}

# For mariadb_php_apache2.sh
data "local_file" "mariadb_template_file" {
  filename = "${path.module}/ubuntu_user_data/mariadb_php_apache2.sh"
}

# For mariadb_php_nginx.sh
data "local_file" "mariadb_nginx_template_file" {
  filename = "${path.module}/ubuntu_user_data/mariadb_php_nginx.sh"
}

locals {
  mysql_content_available = var.database_type == "mysql" && var.web_server == "apache2" ? length(data.local_file.mysql_template_file.content) : 0
  mariadb_content_available = var.database_type == "mariadb" && var.web_server == "apache2" ? length(data.local_file.mariadb_template_file.content) : 0
  mariadb_nginx_content_available = var.database_type == "mariadb" && var.web_server == "nginx" ? length(data.local_file.mariadb_nginx_template_file.content) : 0
}
  

resource "aws_instance" "EC2-create-from-button" {
  ami           = var.ami_id
  instance_type = var.instance_type
  key_name      = var.key_name  # Use the variable here
  # vpc_security_group_ids = [for sg in aws_security_group.sg_name : sg.id]  # Accessing specific instances of the security group
  # vpc_security_group_ids = length(data.aws_security_groups.existing_sg.ids) > 0 ? data.aws_security_groups.existing_sg.ids : [aws_security_group.sg_name.id]
  
  # Use the storage_size_gb variable here
  ebs_block_device {
    device_name           = "/dev/sdf"
    volume_size           = var.storage_size_gb
    encrypted             = true
    delete_on_termination = true
  }

  tags = { 
    Name = "bimba.ec2instance"
  }
  vpc_security_group_ids = [aws_security_group.sg_name.id]
  user_data = <<-EOF
    #!/bin/bash
    echo "Executing ${var.database_type} setup script..."
    
    ${var.database_type == "mysql" && var.web_server == "apache2" ? data.local_file.mysql_template_file.content :
      var.database_type == "mariadb" && var.web_server == "apache2" ? data.local_file.mariadb_template_file.content :
      var.database_type == "mariadb" && var.web_server == "nginx" ? data.local_file.mariadb_nginx_template_file.content :
      ""}

    echo "${var.database_type} setup script has been executed successfully..."

  EOF
}
# Define aws_security_group.sg_name as per your requirement
# This resource will be used only if the user doesn't choose an existing security group
resource "aws_security_group" "sg_name" {
  # count = length(data.aws_security_groups.existing_sg.ids) > 0 ? 0 : 1  # Conditionally create the security group based on a variable
  name        = var.security_group_name
  # description = "Allow inbound traffic to WordPress"
  description = var.security_group_description

  # SSH rule
  dynamic "ingress" {
    for_each = var.allow_ssh ? [1] : []
    content {
      from_port = 22
      to_port = 22
      protocol = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  # HTTP rule
  dynamic "ingress" {
    for_each = var.allow_http ? [1] : []
    content {
      from_port = 80
      to_port = 80
      protocol = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
  
  # ingress {
  #   from_port   = 80
  #   to_port     = 80
  #   protocol    = "tcp"
  #   cidr_blocks = ["0.0.0.0/0"]
  # }
  
  # ingress {
  #   from_port   = 443
  #   to_port     = 443
  #   protocol    = "tcp"
  #   cidr_blocks = ["0.0.0.0/0"]
  # }

  # ingress {
  #   from_port = 22
  #   to_port = 22
  #   protocol = "tcp"
  #   cidr_blocks = ["0.0.0.0/0"]
  # }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
