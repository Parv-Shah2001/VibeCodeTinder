# Terraform for 50M users scale production infra
# Provisions: VPC, RDS Postgres, ElastiCache Redis, S3 buckets, ALB, ECS/EKS, CloudFront, etc.
# For brevity simplified.

terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region = var.region
}

variable "region" { default = "us-east-1" }
variable "env" { default = "prod" }
variable "project" { default = "vibecodetinder" }

# S3 buckets for 10M media/day -> 20TB/day ingress
resource "aws_s3_bucket" "media" {
  bucket = "${var.project}-media-${var.env}"
}
resource "aws_s3_bucket" "message_media" {
  bucket = "${var.project}-message-media-${var.env}"
}
resource "aws_s3_bucket_versioning" "media" {
  bucket = aws_s3_bucket.media.id
  versioning_configuration { status = "Enabled" }
}
resource "aws_s3_bucket_lifecycle_configuration" "media" {
  bucket = aws_s3_bucket.media.id
  rule {
    id = "intelligent-tiering"
    status = "Enabled"
    transition { days = 90, storage_class = "INTELLIGENT_TIERING" }
    transition { days = 180, storage_class = "GLACIER" }
  }
}

# RDS Postgres for 50M users – db.r6g.4xlarge, 500GB GP3, read replica
resource "aws_db_instance" "postgres" {
  identifier = "${var.project}-${var.env}"
  engine = "postgres"
  engine_version = "15"
  instance_class = "db.r6g.2xlarge"
  allocated_storage = 500
  storage_type = "gp3"
  db_name = "vibecodetinder"
  username = "vibe"
  password = var.db_password
  multi_az = true
  backup_retention_period = 7
  performance_insights_enabled = true
  # For Citus sharding at 50M: use aws_rds_cluster with custom parameter group
}

# ElastiCache Redis for 32GB cluster 3 shards – dedup, feed cache, PubSub
resource "aws_elasticache_replication_group" "redis" {
  replication_group_id = "${var.project}-${var.env}"
  description = "Redis for swipe dedup, feed cache, WS PubSub"
  node_type = "cache.r6g.large"
  num_cache_clusters = 3
  engine = "redis"
  engine_version = "7.0"
  parameter_group_name = "default.redis7"
  automatic_failover_enabled = true
}

# CloudFront CDN for media – 80% hit reduces origin
resource "aws_cloudfront_distribution" "media_cdn" {
  origin {
    domain_name = aws_s3_bucket.media.bucket_regional_domain_name
    origin_id = "S3-${aws_s3_bucket.media.bucket}"
    s3_origin_config { origin_access_identity = aws_cloudfront_origin_access_identity.oai.cloudfront_access_identity_path }
  }
  enabled = true
  default_cache_behavior {
    allowed_methods = ["GET", "HEAD"]
    cached_methods = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.media.bucket}"
    viewer_protocol_policy = "redirect-to-https"
    forwarded_values { query_string = false, cookies { forward = "none" } }
    min_ttl = 0
    default_ttl = 86400
    max_ttl = 31536000
  }
  restrictions { geo_restriction { restriction_type = "none" } }
  viewer_certificate { cloudfront_default_certificate = true }
}

resource "aws_cloudfront_origin_access_identity" "oai" {}

# EKS Cluster for API + WS nodes
resource "aws_eks_cluster" "main" {
  name = "${var.project}-${var.env}"
  role_arn = aws_iam_role.eks.arn
  vpc_config { subnet_ids = var.subnet_ids }
}

variable "subnet_ids" { type = list(string) default = [] }
variable "db_password" { sensitive = true }

# Outputs for k8s secrets
output "rds_endpoint" { value = aws_db_instance.postgres.endpoint }
output "redis_endpoint" { value = aws_elasticache_replication_group.redis.primary_endpoint_address }
output "cloudfront_domain" { value = aws_cloudfront_distribution.media_cdn.domain_name }

resource "aws_iam_role" "eks" {
  name = "${var.project}-eks-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{ Action = "sts:AssumeRole", Effect = "Allow", Principal = { Service = "eks.amazonaws.com" } }]
  })
}
