# === Master Node ===
output "master_ip" {
  value = aws_instance.es_master.public_ip
}

output "master_private_ip" {
  value = aws_instance.es_master.private_ip
}

# === Kibana Node ===
output "kibana_ip" {
  value = aws_instance.es_kibana.public_ip
}

output "kibana_private_ip" {
  value = aws_instance.es_kibana.private_ip
}

# === Data Nodes ===
output "data_ips" {
  value = [for instance in aws_instance.es_data : instance.public_ip]
}

output "data_private_ips" {
  value = [for instance in aws_instance.es_data : instance.private_ip]
}

# === Master-Eligible Nodes ===
output "master_eligible_ips" {
  value = [for instance in aws_instance.es_master_eligible : instance.public_ip]
}

output "master_eligible_private_ips" {
  value = [for instance in aws_instance.es_master_eligible : instance.private_ip]
}