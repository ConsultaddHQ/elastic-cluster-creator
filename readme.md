# 🔧 ELK Cluster Provisioning Tool
This tool automates the provisioning and setup of an Elasticsearch cluster with configurable node roles on your choice of cloud provider—AWS EC2 or GCP Compute Engine.

🚀 Features
* Spin up a complete ELK cluster with:

  * Configurable number of data, ingest, and master nodes

  * Optional Kibana setup

* Deploy infrastructure on AWS or GCP

* Automated installation and configuration of Elasticsearch and Kibana

* Built-in support for X-Pack Security

* Generates a dynamic Ansible inventory from cloud resources

* Simplifies cluster management for developers, testers, and SREs

💡 Ideal For
* Quick local or cloud-based ELK cluster setups

* Testing ELK performance with different node configurations

## Prerequisites

Make sure the following tools are installed before proceeding:

* [Terraform](https://www.terraform.io/downloads.html)
* [Python 3.x](https://www.python.org/downloads/)
* [Ansible Playbook](https://docs.ansible.com/ansible/latest/getting_started/index.html)

### For AWS Cloud

* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
* AWS credentials configured using:

  ```bash
  aws configure
  ```

### For GCP Cloud

* GCP service account JSON key file

---

## Local Setup

### 1. Create & Activate Virtual Environment

```bash
python3 -m venv venv
```

This creates a folder named `venv/` containing the virtual environment.

Activate the virtual environment:

* On **macOS/Linux**:

  ```bash
  source venv/bin/activate
  ```

* On **Windows (CMD)**:

  ```cmd
  venv\Scripts\activate.bat
  ```

* On **Windows (PowerShell)**:

  ```powershell
  venv\Scripts\Activate.ps1
  ```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Create ELK Cluster

```bash
python main.py
```

---

## Destroy Cluster

```bash
python destroy.py
```
