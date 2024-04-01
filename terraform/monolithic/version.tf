terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.43.0"  # Use the version you need
    }
    # template = {
    #   source  = "hashicorp/template"
    #   version = ">= 2.2.0"  # Use a version that supports darwin_arm64
    # }
  }
}
