import os
import subprocess
import json
import yaml


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

def main():
    region = prompt("Enter AWS region", "us-east-1")
    instance_type = prompt("Enter instance type", "t2.medium")
    cluster_name = prompt("Enter Elastic cluster name", "my-es-cluster")
    master_eligible = prompt("Enter number of master eligible nodes", "1")
    data_count = prompt("Enter number of data nodes", "2")
    key_name = f"{cluster_name}-ssh-key"
    private_key, public_key = create_ssh_keypair(key_name=key_name)

    # Terraform init
    run_command("terraform init")

    # Build apply command with vars
    apply_cmd = (
        f'terraform apply -auto-approve '
        f'-var="region={region}" '
        f'-var="key_name={key_name}" '
        f'-var="key_pub_path={public_key}" '
        f'-var="instance_type={instance_type}" '
        f'-var="data_count={data_count}" '
        f'-var="master_eligible={master_eligible}" '
        f'-var="cluster_name={cluster_name}"'
    )

    run_command(apply_cmd)

    # Save output as JSON
    output = run_command("terraform output -json", capture_output=True)
    with open("terraform_output.json", "w") as f:
        f.write(output)
    generate_inventory(private_key_path=private_key)

    print("✅ Terraform apply completed and outputs saved to terraform_output.json")

if __name__ == "__main__":
    main()
