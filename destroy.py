import os
import subprocess
from pathlib import Path


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

def main():
    cloud = prompt("Choose cloud provider (aws/gcp)", "aws").lower()
    if cloud not in {"aws", "gcp"}:
        print("❌ Invalid cloud provider. Must be 'aws' or 'gcp'.")
        exit(1)

    os.chdir(Path(__file__).parent / cloud)

    run_command('terraform destroy -var-file="terraform.tfvars"')

    print("✅ Terraform destroy completed")

if __name__ == "__main__":
    main()
