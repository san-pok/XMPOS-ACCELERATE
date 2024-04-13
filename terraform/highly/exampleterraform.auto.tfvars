aws_region = "ap-southeast-2"
#Singapore ap-southeast-1 ,Australia ap-southeast-2 ,North California us-west-1

vpc_cidr_block = "10.0.0.0/16"


ami_id = "ami-04f5097681773b989"
#singapore ami-0eb4694aa6f249c52 ,  Australia ami-04f5097681773b989

instance_type = "t2.micro"
key_pair_name = "tap"
storage_size = 8
storage_type = "gp3"

min_instances = 1
max_instances = 4
desired_instances = 2