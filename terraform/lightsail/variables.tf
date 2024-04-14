

variable "instance_name" {
  description = "The name of the Lightsail instance"
  type        = string
}

variable "key_pair_name" {
  description = "Base name for the Lightsail Key Pair, a unique suffix will be appended"
  type        = string
  default     = "XMOPSTeamTwo"
}

variable "ssh_key" {
  description = "The public SSH key to access the instance"
  type        = string
}

variable "bundle_id" {
  description = "The ID of the Lightsail bundle"
  type        = string
  default     = "nano_3_2"
}

variable "blueprint" {
  description = "The ID of the blueprint (e.g., wordpress)"
  type        = string
  default     = "wordpress"
}
