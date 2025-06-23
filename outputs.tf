output "master_ip" {
  value = aws_instance.es_master.public_ip
}

output "kibana_ip" {
  value = aws_instance.es_kibana.public_ip
}

output "data_ips" {
  value = [for instance in aws_instance.es_data : instance.public_ip]
}

output "ingest_ips" {
  value = [for instance in aws_instance.es_master_eligible : instance.public_ip]
}
