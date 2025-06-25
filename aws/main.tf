provider "aws" {
  region = var.region
}

resource "aws_key_pair" "elastic_key" {
  key_name   = var.key_name
  public_key = file(var.key_pub_path)
}

resource "aws_security_group" "elastic_sg" {
  name        = "elastic-cluster-sg"
  description = "Allow SSH, 9200, 5601"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 9200
    to_port     = 9200
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 5601
    to_port     = 5601
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 9300
    to_port     = 9300
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

locals {
  ami_id = var.ami_id_map[var.region]
}

resource "aws_instance" "es_master" {
  ami                    = local.ami_id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.elastic_sg.id]
  tags = {
    Name = "${var.cluster_name}-master-node"
  }
}

resource "aws_instance" "es_kibana" {
  ami                    = local.ami_id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.elastic_sg.id]
  tags = {
    Name = "${var.cluster_name}-kibana-node"
  }
}

resource "aws_instance" "es_data" {
  count                  = var.data_count
  ami                    = local.ami_id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.elastic_sg.id]
  tags = {
    Name = "${var.cluster_name}-data-node-${count.index + 1}"
  }
}

resource "aws_instance" "es_master_eligible" {
  count                  = var.master_eligible
  ami                    = local.ami_id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.elastic_sg.id]
  tags = {
    Name = "${var.cluster_name}-master-eligible-node-${count.index + 1}"
  }
}
