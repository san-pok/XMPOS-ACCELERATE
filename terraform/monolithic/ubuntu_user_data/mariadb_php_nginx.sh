#!/bin/bash

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
        fastcgi_pass unix:/run/php/php-fpm.sock;
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

# # Display the content of cloud-init-output.log and follow it in real-time
# tail -f /var/log/cloud-init-output.log
echo "MariaDB and Nginx script execution completed."