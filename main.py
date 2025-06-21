import boto3
import botocore
import os
import time

AMI_ID_MAP = {
    "us-east-1": "ami-0c02fb55956c7d316",
    "us-west-2": "ami-0885b1f6bd170450c",
    "ap-south-1": "ami-0a0ad6b70e61be944"
}

def get_ami_id(region):
    return AMI_ID_MAP.get(region, None)

def get_input():
    print("Enter number of nodes:")
    master = int(input("Master nodes: "))
    data = int(input("Data nodes: "))
    ingest = int(input("Ingest nodes: "))
    kibana = int(input("Kibana nodes: "))
    return master, data, ingest, kibana


def create_security_group(name="elastic-cluster-sg", description="Allow SSH, 9200, 5601", vpc_id=None, region="us-east-1"):
    ec2 = boto3.client("ec2", region_name=region)

    # Get default VPC if not provided
    if not vpc_id:
        vpcs = ec2.describe_vpcs(Filters=[{"Name": "isDefault", "Values": ["true"]}])
        vpc_id = vpcs["Vpcs"][0]["VpcId"]

    try:
        # Create security group
        response = ec2.create_security_group(
            GroupName=name,
            Description=description,
            VpcId=vpc_id
        )
        sg_id = response["GroupId"]

        # Authorize inbound rules
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22,
                    "ToPort": 22,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
                },
                {
                    "IpProtocol": "tcp",
                    "FromPort": 9200,
                    "ToPort": 9200,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
                },
                {
                    "IpProtocol": "tcp",
                    "FromPort": 5601,
                    "ToPort": 5601,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
                }
            ]
        )

        print(f"✅ Created security group '{name}' with ID: {sg_id}")
        return sg_id

    except botocore.exceptions.ClientError as e:
        if "InvalidGroup.Duplicate" in str(e):
            print(f"⚠️ Security group '{name}' already exists.")
            existing = ec2.describe_security_groups(
                Filters=[{"Name": "group-name", "Values": [name]}]
            )
            return existing["SecurityGroups"][0]["GroupId"]
        else:
            raise

def create_key_pair(key_name: str, save_path: str, region: str = "us-east-1"):
    ec2 = boto3.client("ec2", region_name=region)

    # Check if key already exists
    existing_keys = ec2.describe_key_pairs()["KeyPairs"]
    if any(k["KeyName"] == key_name for k in existing_keys):
        print(f"Key pair '{key_name}' already exists in AWS.")
        return

    # Create key pair
    response = ec2.create_key_pair(KeyName=key_name)
    private_key = response["KeyMaterial"]

    # Save the private key locally
    with open(save_path, "w") as f:
        f.write(private_key)
    os.chmod(save_path, 0o400)

    print(f"✅ Key pair '{key_name}' created and saved to '{save_path}'")



def create_ec2_instance(
    key_name: str,
    instance_type: str,
    security_group_id: str,
    region: str = "us-east-1",
    tag_name: str = "elastic-node"
):
    ec2 = boto3.resource("ec2", region_name=region)

    ami_id = get_ami_id(region)
    print(f"⏳ Launching EC2 instance...{ami_id}")
    instances = ec2.create_instances(
        ImageId=ami_id,
        InstanceType=instance_type,
        KeyName=key_name,
        SecurityGroupIds=[security_group_id],
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name', 'Value': tag_name}]
        }]
    )

    instance = instances[0]

    print(f"📦 Instance ID: {instance.id}. Waiting for it to run...")
    instance.wait_until_running()
    instance.reload()

    print(f"✅ Instance is running. Public IP: {instance.public_ip_address}")
    return instance.public_ip_address

def main():
    master, data, ingest, kibana = get_input()
    print(f"Master nodes: {master}, Data nodes: {data}, Ingest nodes: {ingest}, Kibana nodes: {kibana}")

    key_name = "hpf-key-name" # Replace with your desired key name
    create_key_pair(key_name, "hpf-key.pem")

    print("Creating security group...")
    security_group_id = create_security_group()
    
    public_ip = create_ec2_instance(
        key_name=key_name,
        instance_type="t2.small",  # Replace with your desired instance type
        security_group_id=security_group_id  # Replace with your security group ID
    )

if __name__ == "__main__":
    main()
