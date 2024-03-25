variable "instance_name" {
  description = "The name of the Lightsail instance"
  type        = string
}

variable "instance_location" {
  description = "The AWS region and availability zone for the Lightsail instance"
  type        = string
}

variable "key_pair_name" {
  description = "Name for the Lightsail Key Pair"
  type        = string
}

variable "ssh_key" {
  description = "The public SSH key to access the instance"
  type        = string
}

variable "bundle_id" {
  description = "The ID of the Lightsail bundle"
  type        = string
  default     = "nano_3_2"  # Ensure this default value matches your frontend options.
}

variable "blueprint" {
  description = "The ID of the blueprint (e.g., wordpress)"
  type        = string
  default     = "wordpress"
}
