variable "gcp_project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "gcp_region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "gcp_zone" {
  description = "GCP zone"
  type        = string
  default     = "us-central1-a"
}

variable "gcp_credentials_file" {
  description = "Path to GCP credentials JSON file"
  type        = string
}

variable "key_pub_path" {
  description = "Path to public SSH key"
  type        = string
}

variable "instance_type" {
  description = "GCP machine type"
  type        = string
  default     = "e2-medium"
}

variable "gcp_image" {
  description = "Ubuntu image for GCP VM"
  type        = string
  default     = "ubuntu-os-cloud/ubuntu-2204-lts"
}

variable "data_count" {
  description = "Number of Elasticsearch data nodes"
  type        = number
  default     = 2
}

variable "master_eligible" {
  description = "Number of master-eligible nodes"
  type        = number
  default     = 1
}

variable "cluster_name" {
  description = "Elastic cluster name"
  type        = string
  default     = "my-es-cluster"
}
