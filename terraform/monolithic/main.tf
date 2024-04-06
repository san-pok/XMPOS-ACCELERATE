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
      ""}

    ${var.database_type == "mariadb" && var.web_server == "nginx" ? data.local_file.mariadb_nginx_template_file.content : ""}

    sudo apt update -y
                sudo apt upgrade -y
                sudo apt install nginx mariadb-server php-fpm php-mysql -y

                # Secure MariaDB installation
                sudo mysql_secure_installation <<EOL
                n
                y
                y
                y
                y
                EOL

                # Create MySQL database and user for WordPress
                sudo mysql <<EOL
                CREATE DATABASE example_db;
                CREATE USER 'example_user'@'localhost' IDENTIFIED BY 'example_pw';
                GRANT ALL PRIVILEGES ON example_db.* TO 'example_user'@'localhost';
                FLUSH PRIVILEGES;
                EOL

                cd /var/www/html
                sudo wget -q https://wordpress.org/latest.tar.gz
                sudo tar -xzf latest.tar.gz
                sudo chown -R www-data:www-data wordpress
                sudo chmod -R 755 wordpress
                sudo rm latest.tar.gz

                # Configure WordPress
                sudo cp wordpress/wp-config-sample.php wordpress/wp-config.php
                sudo sed -i "s/database_name_here/example_db/g" wordpress/wp-config.php
                sudo sed -i "s/username_here/example_user/g" wordpress/wp-config.php
                sudo sed -i "s/password_here/example_pw/g" wordpress/wp-config.php

                # Create Nginx configuration file for example.com
                sudo tee /etc/nginx/sites-available/example.conf <<EOL
                server {
                    listen 80 default_server;
                    listen [::]:80 default_server;

                    root /var/www/html/wordpress;
                    index index.php index.html index.htm;

                    server_name _;

                    location / {
                        try_files \$uri \$uri/ /index.php?\$args;
                    }

                    location ~ \.php$ {
                        include snippets/fastcgi-php.conf;
                        fastcgi_pass unix:/run/php/php7.4-fpm.sock;
                        fastcgi_param SCRIPT_FILENAME \$document_root\$fastcgi_script_name;
                        include fastcgi_params;
                    }

                    location ~ /\.ht {
                        deny all;
                    }
                }
                EOL

                # Remove the default Nginx configuration
                sudo rm /etc/nginx/sites-enabled/default

                # Enable the Nginx configuration file
                sudo ln -s /etc/nginx/sites-available/example.conf /etc/nginx/sites-enabled/

                # Test Nginx configuration and restart Nginx
                sudo nginx -t && sudo systemctl restart nginx

                # Display the content of cloud-init-output.log and follow it in real-time
                tail -f /var/log/cloud-init-output.log

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
