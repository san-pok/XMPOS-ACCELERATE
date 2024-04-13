resource "aws_lb" "wordpress_lb" {
  name               = "${var.namespace}-hwordpress-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.xmop_wordpress_sg.id]
  subnets            = [
    aws_subnet.xmop_subnet_1.id,
    aws_subnet.xmop_subnet_2.id
  ]

  tags = {
    Name = "wordpress-lb"
  }
}

resource "aws_lb_target_group" "wordpress_target_group" {
  name     = "${var.namespace}-hwordpress-target-group"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.xmop_vpc.id

  health_check {
    path                = "/"
    protocol            = "HTTP"
  }
}

resource "aws_lb_listener" "wordpress_listener" {
  load_balancer_arn = aws_lb.wordpress_lb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.wordpress_target_group.arn
  }
}
