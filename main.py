import json
import os
import subprocess
import time
from pathlib import Path
import yaml


def write_tfvars_file(values: dict):
    with open("terraform.tfvars", "w") as f:
        for key, value in values.items():
            if isinstance(value, str):
                f.write(f'{key} = "{value}"\n')
            else:
                f.write(f"{key} = {value}\n")

def prompt(message, default=None):
    val = input(f"{message} (default: {default}): ").strip()
    return val or default

def run_command(command, capture_output=False):
    print(f"▶️ Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=capture_output, text=True)
    if result.returncode != 0:
        print(f"❌ Command failed: {command}")
        print(result.stderr)
        exit(1)
    return result.stdout if capture_output else None


def create_ssh_keypair(key_name="elk_cluster_key"):
    private_key = f"./{key_name}"
    public_key = f"{private_key}.pub"

    if os.path.exists(private_key):
        print(f"⚠️ SSH private key already exists: {private_key}")
        return private_key, public_key

    # Generate the RSA key pair (no passphrase)
    run_command(f'ssh-keygen -t rsa -b 4096 -f "{private_key}" -N ""')

    # Restrict permissions on private key
    run_command(f'chmod 400 "{private_key}"')

    print(f"✅ SSH key pair created:")
    print(f"  🔐 Private key: {private_key}")
    print(f"  🔓 Public key: {public_key}")

    return private_key, public_key

def generate_inventory(private_key_path):
    with open("terraform_output.json") as f:
        data = json.load(f)

    inventory = {
        'all': {
            'vars': {
                'ansible_user': 'ubuntu',
                'ansible_ssh_private_key_file': f'{private_key_path}',
                'ansible_ssh_common_args': '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
            },
            'children': {
                'elasticsearch': {
                    'children': {
                        'elasticsearch_master': {
                            'hosts': {
                                'master-node-1': {'ansible_host': data['master_ip']['value']}
                            }
                        },
                        'elasticsearch_kibana': {
                            'hosts': {
                                'kibana-node-1': {'ansible_host': data['kibana_ip']['value']}
                            }
                        },
                        'elasticsearch_data': {
                            'hosts': {
                                f'data-node-{i+1}': {'ansible_host': ip}
                                for i, ip in enumerate(data['data_ips']['value'])
                            }
                        },
                        'elasticsearch_master_eligible': {
                            'hosts': {
                                f'master-eligible-{i+1}': {'ansible_host': ip}
                                for i, ip in enumerate(data['ingest_ips']['value'])
                            }
                        }
                    }
                }
            }
        }
    }

    with open("inventory.yaml", "w") as f:
        yaml.dump(inventory, f, sort_keys=False)

def get_extra_variables():
    with open("terraform_output.json") as f:
        data = json.load(f)

    ips = []

    # Append all IPs from the respective fields
    ips += data.get("data_ips", {}).get("value", [])
    ips += data.get("master_ip", {}).get("value")

    master_ip = data.get("master_ip", {}).get("value")
    if master_ip:
        ips.append(master_ip)

    return json.dumps({"es_seed_hosts": ips})



def main():
    cloud = prompt("Choose cloud provider (aws/gcp)", "aws").lower()
    if cloud not in {"aws", "gcp"}:
        print("❌ Invalid cloud provider. Must be 'aws' or 'gcp'.")
        exit(1)

    os.chdir(Path(__file__).parent / cloud)

    cluster_name = prompt("Enter Elastic cluster name", "my-es-cluster")
    key_name = f"{cluster_name}-ssh-key"
    private_key, public_key = create_ssh_keypair(key_name=key_name)

    tfvars = {
        "cluster_name": cluster_name,
        "key_pub_path": public_key,
    }

    if cloud == "aws":
        tfvars.update({
            "region": prompt("Enter AWS region", "us-east-1"),
            "key_name": key_name,
            "instance_type": prompt("Enter instance type", "t2.medium"),
            "master_eligible": int(prompt("Enter number of master eligible nodes", "1")),
            "data_count": int(prompt("Enter number of data nodes", "2")),
        })

    elif cloud == "gcp":
        tfvars.update({
            "gcp_project_id": prompt("Enter GCP project ID"),
            "gcp_region": prompt("Enter GCP region", "us-central1"),
            "gcp_zone": prompt("Enter GCP zone", "us-central1-a"),
            "instance_type": prompt("Enter GCP machine type", "e2-medium"),
            "master_eligible": int(prompt("Enter number of master eligible nodes", "1")),
            "data_count": int(prompt("Enter number of data nodes", "2")),
            "gcp_credentials_file": prompt("Enter GCP JSON Credential file path")
        })

    write_tfvars_file(tfvars)

    run_command("terraform init")
    run_command('terraform apply -auto-approve -var-file="terraform.tfvars"')

    output = run_command("terraform output -json", capture_output=True)
    with open("terraform_output.json", "w") as f:
        f.write(output)

    print("✅ Terraform apply completed and outputs saved to terraform_output.json")

    generate_inventory(private_key_path=private_key)
    extra_variables = get_extra_variables()

    time.sleep(30)  # wait for SSH to be ready

    run_command(f"ansible-playbook -i inventory.yaml --extra-vars '{extra_variables}' ../ansible-role/playbook.yaml")

if __name__ == "__main__":
    main()

