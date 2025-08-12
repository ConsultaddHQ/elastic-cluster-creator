output "master_ip" {
  value = google_compute_instance.es_master.network_interface[0].access_config[0].nat_ip
}

output "master_private_ip" {
  value = google_compute_instance.es_master.network_interface[0].network_ip
}

# === Kibana Node ===
output "kibana_ip" {
  value = google_compute_instance.es_kibana.network_interface[0].access_config[0].nat_ip
}

output "kibana_private_ip" {
  value = google_compute_instance.es_kibana.network_interface[0].network_ip
}

# === Data Nodes ===
output "data_ips" {
  value = [for inst in google_compute_instance.es_data : inst.network_interface[0].access_config[0].nat_ip]
}

output "data_private_ips" {
  value = [for inst in google_compute_instance.es_data : inst.network_interface[0].network_ip]
}

# === Master-Eligible Nodes ===
output "master_eligible_ips" {
  value = [for inst in google_compute_instance.es_master_eligible : inst.network_interface[0].access_config[0].nat_ip]
}

output "master_eligible_private_ips" {
  value = [for inst in google_compute_instance.es_master_eligible : inst.network_interface[0].network_ip]
}