data "aws_caller_identity" "current" {}

data "aws_vpc" "selected_vpc" {
  filter {
    name   = "tag:Name"
    values = ["fiap-hackathon-vpc"]
  }
}

data "aws_subnets" "private_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.selected_vpc.id]
  }

  filter {
    name   = "tag:Environment"
    values = ["private"]
  }

  depends_on = [data.aws_vpc.selected_vpc]
}

data "aws_subnet" "selected_subnets" {
  for_each = toset(data.aws_subnets.private_subnets.ids)
  id       = each.value

  depends_on = [data.aws_subnets.private_subnets]
}

data "aws_ip_ranges" "api_gateway" {
  services = ["API_GATEWAY"]
  regions  = [var.aws_region]
}

data "aws_iam_role" "lab_role" {
  name = "LabRole"
}

data "aws_lb" "nlb" {
  name = "fiap-hackathon-nlb"
}

data "aws_ssm_parameter" "video_file_store_bucket_name" {
  name = "/fiap-hackathon/video-file-store-bucket"
}

data "aws_s3_bucket" "video_file_store_bucket" {
  bucket = data.aws_ssm_parameter.video_file_store_bucket_name.value
}

data "aws_sqs_queue" "video-create-queue" {
  name = "video-create-queue"
}
