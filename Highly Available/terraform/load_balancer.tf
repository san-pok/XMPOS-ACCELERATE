#resource "aws_security_group" "wordpress_lb_sg" {
#  name        = "wordpress_lb_sg"
#  description = "Security group for the WordPress load balancer"
#  vpc_id      = aws_vpc.xmop_vpc.id
#
#  ingress {
#    from_port   = 80
#    to_port     = 80
#    protocol    = "tcp"
#    cidr_blocks = ["0.0.0.0/0"]
#  }
#
#  ingress {
#    from_port   = 443
#    to_port     = 443
#    protocol    = "tcp"
#    cidr_blocks = ["0.0.0.0/0"]
#  }
#}
#
#resource "aws_lb" "wordpress_lb" {
#  name               = "wordpress-lb"
#  internal           = false
#  load_balancer_type = "application"
#  security_groups    = [aws_security_group.wordpress_lb_sg.id]
#  subnets            = [
#    aws_subnet.xmop_subnet_1.id,
#    aws_subnet.xmop_subnet_2.id
#  ]
#
#  tags = {
#    Name = "wordpress-lb"
#  }
#}
#
#
#resource "aws_lb_target_group" "wordpress_target_group" {
#  name     = "wordpress-target-group"
#  port     = 80
#  protocol = "HTTP"
#  vpc_id   = aws_vpc.xmop_vpc.id
#
#  health_check {
#    path = "/"
#  }
#}
#
#resource "aws_lb_listener" "wordpress_listener" {
#  load_balancer_arn = aws_lb.wordpress_lb.arn
#  port              = 80
#  protocol          = "HTTP"
#
#  default_action {
#    type             = "forward"
#    target_group_arn = aws_lb_target_group.wordpress_target_group.arn
#  }
#}
