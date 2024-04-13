variable "aws_region" {
  type = string
  default = "ap_southeast-2"
  description = "Sydney region for Wordpress-Lightsail"
}

variable "project_name" {
  description = "Wordpress-Lightsail-Terraform"
  type = string
}

variable "bundle_id" {
  type = string
  default = "nano_3_2"
  description = "3.5 priced instance size"
}

variable "lightsail_blueprints" {
  type = map(string)
  description = "blueprintId - wordpress"
}