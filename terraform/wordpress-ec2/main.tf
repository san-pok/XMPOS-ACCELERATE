provider "aws" {
  region = var.aws_region
}
data "aws_region" "current" {}


resource "aws_instance" "EC2-create-from-button" {
  ami           = var.ami_id
  instance_type = var.instance_type

  key_name      = "wordpress_server"
  vpc_security_group_ids = [aws_security_group.wordpress_sg.id]  # Associate the security group

  tags = {
    Name = "EC2-FROM-WEBSITE TAP"
  }
  user_data = <<-EOF
              #!/bin/bash
              # Update package lists
              sudo apt-get update

              # Install Apache2, MySQL, PHP, and other necessary packages
              sudo apt-get install -y apache2 mysql-server php libapache2-mod-php php-mysql

              # Enable Apache2 and MySQL services
              sudo systemctl enable apache2
              sudo systemctl enable mysql

              # Start Apache2 and MySQL services
              sudo systemctl start apache2
              sudo systemctl start mysql

              # Set up MySQL database and user for WordPress
              sudo mysql -u root -e "CREATE DATABASE wordpress;"
              sudo mysql -u root -e "CREATE USER 'wpadmin'@'localhost' IDENTIFIED BY 'wpadminpass';"
              sudo mysql -u root -e "GRANT ALL PRIVILEGES ON wordpress.* TO 'wpadmin'@'localhost';"
              sudo mysql -u root -e "FLUSH PRIVILEGES;"

              # Install WordPress
              cd /var/www/html
              sudo wget https://wordpress.org/latest.tar.gz
              sudo tar -xzf latest.tar.gz --strip-components=1
              sudo rm -f latest.tar.gz
              sudo chown -R www-data:www-data /var/www/html
              sudo cp wp-config-sample.php wp-config.php
              sudo sed -i "s/database_name_here/wordpress/" wp-config.php
              sudo sed -i "s/username_here/wpadmin/" wp-config.php
              sudo sed -i "s/password_here/wpadminpass/" wp-config.php
              sudo rm /var/www/html/index.html
              sudo systemctl restart apache2
              echo "Wordpress installation script has completed. "
              
              EOF

}

resource "aws_security_group" "wordpress_sg" {
  name        = "wordpress_sg"
  description = "Allow inbound traffic to WordPress"
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
