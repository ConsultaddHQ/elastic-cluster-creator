variable "region" {
  default = "us-east-1"
}

variable "key_name" {
  default = "hpf-key-name"
}

variable "key_pub_path" {
  default = "/Users/vijay/.ssh/id_rsa.pub"
}

variable "instance_type" {
  default = "t2.small"
}

variable "ami_id_map" {
  type = map(string)
  default = {
    "us-east-1"    = "ami-0c02fb55956c7d316"
    "us-west-2"    = "ami-0885b1f6bd170450c"
    "ap-south-1"   = "ami-0a0ad6b70e61be944"
  }
}

variable "data_count" {
  type    = number
  default = 1
}

variable "ingest_count" {
  type    = number
  default = 0
}

variable "cluster_name" {
  type    = string
  default = "my-es-cluster"
}
