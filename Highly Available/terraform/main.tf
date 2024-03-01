resource "aws_vpc" "xmop_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = {
    Name = var.vpc_name
  }
}

resource "aws_internet_gateway" "xmop_internet_gateway" {
  vpc_id = aws_vpc.xmop_vpc.id

  tags = {
    Name = var.internet_gateway_name
  }
}

resource "aws_subnet" "xmop_subnet_1" {
  vpc_id            = aws_vpc.xmop_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${var.aws_region}a"
  map_public_ip_on_launch = true
}

resource "aws_subnet" "xmop_subnet_2" {
  vpc_id            = aws_vpc.xmop_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.aws_region}b"
  map_public_ip_on_launch = true
}

resource "aws_route_table" "xmop_route_table" {
  vpc_id = aws_vpc.xmop_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.xmop_internet_gateway.id
  }
}

resource "aws_route_table_association" "xmop_route_association_1" {
  subnet_id      = aws_subnet.xmop_subnet_1.id
  route_table_id = aws_route_table.xmop_route_table.id
}

resource "aws_route_table_association" "xmop_route_association_2" {
  subnet_id      = aws_subnet.xmop_subnet_2.id
  route_table_id = aws_route_table.xmop_route_table.id
}

resource "aws_security_group" "xmop_wordpress_sg" {
  name        = "wordpress_sg"
  description = "Allow inbound traffic to WordPress"
  vpc_id      = aws_vpc.xmop_vpc.id

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

resource "aws_instance" "xmop_instance" {
  ami           = var.ami_id
  instance_type = var.instance_type
  key_name      = var.key_pair_name
  subnet_id     = aws_subnet.xmop_subnet_1.id
  vpc_security_group_ids = [aws_security_group.xmop_wordpress_sg.id]

  root_block_device {
    volume_size = var.storage_size
    volume_type = var.storage_type
  }

  tags = {
    Name = var.instance_name
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
