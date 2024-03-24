provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "team2_s3" {
  bucket = var.bucket_name

  tags = {
    Name        = "Team2 XMOPs Instance Data"
    Environment = "Dev"
  }
  provisioner "local-exec" {
    command = <<EOT
      if [ "$?" -eq "0"]; then
        echo "S3 Bucket ${var.bucket_name} created successfully."
      else
        echo "S3 Bucket ${var.bucket_name} already exists."
      fi
    EOT
  }
}

variable "aws_region" {
  default     = "ap-southeast-2"
  description = "Team2 XMOPS storage for instance details"
}

variable "bucket_name" {
  description = "Team2's S3 bucket"
  type        = string
  default     = "xmops-data-bucket-team2"
}

variable "create_bucket" {
  description = "Flag to indicate whether to create the S3 bucket"
  type        = bool
  default     = true
}

# output "bucket_name" {
#   value = aws_s3_bucket.team2_s3[*].bucket
# }
