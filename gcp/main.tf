provider "google" {
  project     = var.gcp_project_id
  region      = var.gcp_region
  credentials = file(var.gcp_credentials_file)
}

resource "google_compute_firewall" "elastic_fw" {
  name    = "elastic-cluster-fw"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22", "9200", "5601","9300"]
  }

  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_instance" "es_master" {
  name         = "${var.cluster_name}-master-node"
  machine_type = var.instance_type
  zone         = var.gcp_zone

  boot_disk {
    initialize_params {
      image = var.gcp_image
    }
  }

  network_interface {
    network       = "default"
    access_config {}
  }

  metadata = {
    ssh-keys = "ubuntu:${file(var.key_pub_path)}"
  }

  tags = ["elasticsearch"]
}

resource "google_compute_instance" "es_kibana" {
  name         = "${var.cluster_name}-kibana-node"
  machine_type = var.instance_type
  zone         = var.gcp_zone

  boot_disk {
    initialize_params {
      image = var.gcp_image
    }
  }

  network_interface {
    network       = "default"
    access_config {}
  }

  metadata = {
    ssh-keys = "ubuntu:${file(var.key_pub_path)}"
  }

  tags = ["elasticsearch"]
}

resource "google_compute_instance" "es_data" {
  count        = var.data_count
  name         = "${var.cluster_name}-data-node-${count.index + 1}"
  machine_type = var.instance_type
  zone         = var.gcp_zone

  boot_disk {
    initialize_params {
      image = var.gcp_image
    }
  }

  network_interface {
    network       = "default"
    access_config {}
  }

  metadata = {
    ssh-keys = "ubuntu:${file(var.key_pub_path)}"
  }

  tags = ["elasticsearch"]
}

resource "google_compute_instance" "es_master_eligible" {
  count        = var.master_eligible
  name         = "${var.cluster_name}-master-eligible-node-${count.index + 1}"
  machine_type = var.instance_type
  zone         = var.gcp_zone

  boot_disk {
    initialize_params {
      image = var.gcp_image
    }
  }

  network_interface {
    network       = "default"
    access_config {}
  }

  metadata = {
    ssh-keys = "ubuntu:${file(var.key_pub_path)}"
  }

  tags = ["elasticsearch"]
}

