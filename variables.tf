variable "region" {
  default = "us-east-1"
}

variable "key_name" {
  default = "hpf-key-name"
}

variable "key_pub_path" {
}

variable "instance_type" {
  default = "t2.small"
}

variable "ami_id_map" {
  type = map(string)
  default = {
    "us-east-1"  = "ami-020cba7c55df1f615"    # Ubuntu 22.04 LTS
    "us-west-2"  = "ami-05f991c49d264708f"    # Ubuntu 22.04 LTS
    "ap-south-1" = "ami-0f918f7e67a3323f0"    # Ubuntu 22.04 LTS
  }
}
variable "data_count" {
  type    = number
  default = 1
}

variable "master_eligible" {
  type    = number
  default = 0
}

variable "cluster_name" {
  type    = string
  default = "my-es-cluster"
}
