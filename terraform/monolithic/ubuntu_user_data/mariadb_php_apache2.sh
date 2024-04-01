#!/bin/bash

# Log message indicating script execution
echo "MariaDB, PHP, and Apache2 installation script executed."

# Update and upgrade packages
sudo apt update && sudo apt upgrade -y

# Install Apache2
sudo apt install -y apache2
sudo systemctl status apache2

# Install MariaDB
sudo apt install -y mariadb-server mariadb-client

# Secure MariaDB installation
echo "y" | sudo mysql_secure_installation <<EOL
enter
n
Y
Y
Y
Y
EOL

# Install PHP and PHP MySQL extension
sudo apt install -y php php-mysql

# Create info.php file
echo '<?php phpinfo(); ?>' | sudo tee /var/www/html/info.php

# Create MySQL database and user for WordPress
sudo mysql -u root -p -e "CREATE DATABASE wordpress_db;"
sudo mysql -u root -p -e "CREATE USER 'wp_user'@'localhost' IDENTIFIED BY 'password';"
sudo mysql -u root -p -e "GRANT ALL ON wordpress_db.* TO 'wp_user'@'localhost' IDENTIFIED BY 'password';"
sudo mysql -u root -p -e "FLUSH PRIVILEGES;"
sudo mysql -u root -p -e "Exit;"

# Download and install WordPress
cd /tmp && sudo wget https://wordpress.org/latest.tar.gz
sudo tar -xvf latest.tar.gz
sudo cp -R wordpress/* /var/www/html/
sudo chown -R www-data:www-data /var/www/html/wordpress/
sudo chmod -R 755 /var/www/html/wordpress/
sudo mkdir /var/www/html/wordpress/wp-content/uploads
sudo chown -R www-data:www-data /var/www/html/wordpress/wp-content/uploads/

sudo rm /var/www/html/index.html

# Restart Apache2 service
sudo systemctl restart apache2

echo "Wordpress installation script has completed. "

# Output a message indicating the script has completed
echo "MariaDB script execution completed."