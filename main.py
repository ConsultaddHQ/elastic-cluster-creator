import subprocess


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
import json
import yaml

def generate_inventory():
    with open("terraform_output.json") as f:
        data = json.load(f)

    inventory = {
        'all': {
            'vars': {
                'ansible_user': 'ubuntu',
                'ansible_ssh_private_key_file': './hpf-key-name.pem',
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
                        'elasticsearch_ingest': {
                            'hosts': {
                                f'ingest-node-{i+1}': {'ansible_host': ip}
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
    key_name = prompt("Enter EC2 key pair name", "hpf-key-name")
    key_pub_path = prompt("Enter path to your public key", "/Users/vijay/.ssh/id_rsa.pub")
    instance_type = prompt("Enter instance type", "t2.small")
    data_count = prompt("Enter number of data nodes", "2")
    ingest_count = prompt("Enter number of ingest nodes", "1")
    cluster_name = prompt("Enter Elastic cluster name", "my-es-cluster")

    # Terraform init
    run_command("terraform init")

    # Build apply command with vars
    apply_cmd = (
        f'terraform apply -auto-approve '
        f'-var="region={region}" '
        f'-var="key_name={key_name}" '
        f'-var="key_pub_path={key_pub_path}" '
        f'-var="instance_type={instance_type}" '
        f'-var="data_count={data_count}" '
        f'-var="ingest_count={ingest_count}" '
        f'-var="cluster_name={cluster_name}"'
    )

    run_command(apply_cmd)

    # Save output as JSON
    output = run_command("terraform output -json", capture_output=True)
    with open("terraform_output.json", "w") as f:
        f.write(output)
    generate_inventory()

    print("✅ Terraform apply completed and outputs saved to terraform_output.json")

if __name__ == "__main__":
    main()
