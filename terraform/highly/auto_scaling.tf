resource "aws_launch_configuration" "xmop_launch_configuration" {
  name                        = "xmop-launch-configuration"
  image_id                    = var.ami_id
  instance_type               = var.instance_type
  key_name                    = var.key_pair_name
  security_groups             = [aws_security_group.xmop_wordpress_sg.id]
  iam_instance_profile = aws_iam_instance_profile.ec2_profile.name

  root_block_device {
    volume_size               = var.storage_size
    volume_type               = var.storage_type
  }

  user_data = <<-EOF
    #!/bin/bash
    # Update package lists
    sudo apt-get update

    # Install Apache2, PHP, MySQL extension, and other necessary packages
    sudo apt-get install -y apache2 php libapache2-mod-php php-mysql

    # Enable Apache2 service
    sudo systemctl enable apache2

    # Install WordPress
    cd /var/www/html
    sudo wget https://wordpress.org/latest.tar.gz
    sudo tar -xzf latest.tar.gz --strip-components=1
    sudo rm -f latest.tar.gz
    sudo chown -R www-data:www-data /var/www/html
    sudo cp wp-config-sample.php wp-config.php

    # Update WordPress configuration to use RDS
    sudo sed -i "s/database_name_here/${aws_db_instance.example_rds.db_name}/" wp-config.php
    sudo sed -i "s/username_here/${aws_db_instance.example_rds.username}/" wp-config.php
    sudo sed -i "s/password_here/${aws_db_instance.example_rds.password}/" wp-config.php
    sudo sed -i "s/localhost/${aws_db_instance.example_rds.endpoint}/" wp-config.php
    # Remove the index.html file if present
    sudo rm /var/www/html/index.html

    # Restart Apache2
    sudo systemctl restart apache2

    echo "WordPress installation script has completed."
  EOF
}


resource "aws_autoscaling_group" "xmop_autoscaling_group" {
  name                        = "xmop-autoscaling-group"
  max_size                    = var.max_instances
  min_size                    = var.min_instances
  desired_capacity            = var.desired_instances
  launch_configuration        = aws_launch_configuration.xmop_launch_configuration.name
  vpc_zone_identifier         = [
    aws_subnet.xmop_subnet_1.id,
    aws_subnet.xmop_subnet_2.id
  ]
  tag {
    key                       = "Name"
    value                     = var.instance_name
    propagate_at_launch      = true
  }

  target_group_arns           = [aws_lb_target_group.wordpress_target_group.arn]
}

resource "aws_cloudwatch_metric_alarm" "cpu_alarm_subnet_1" {
  alarm_name          = "CPUUtilizationHigh_Subnet1"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description  = "Alarm when CPU utilization is greater than or equal to 80% for 10 minutes"
  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.xmop_autoscaling_group.name
  }

  alarm_actions      = [aws_autoscaling_policy.scale_out_policy_subnet_1.arn]
}

resource "aws_autoscaling_policy" "scale_out_policy_subnet_1" {
  name                   = "ScaleOutPolicy_Subnet1"
  scaling_adjustment     = 1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.xmop_autoscaling_group.name
}

resource "aws_cloudwatch_metric_alarm" "cpu_alarm_subnet_2" {
  alarm_name          = "CPUUtilizationHigh_Subnet2"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 10
  statistic           = "Average"
  threshold           = 80
  alarm_description  = "Alarm when CPU utilization is greater than or equal to 80% for 10 minutes"
  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.xmop_autoscaling_group.name
  }

  alarm_actions      = [aws_autoscaling_policy.scale_out_policy_subnet_2.arn]
}

resource "aws_autoscaling_policy" "scale_out_policy_subnet_2" {
  name                   = "ScaleOutPolicy_Subnet2"
  scaling_adjustment     = 1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.xmop_autoscaling_group.name
}

