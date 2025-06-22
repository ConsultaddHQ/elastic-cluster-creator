import boto3
import botocore
import os
import time

AMI_ID_MAP = {
    "us-east-1": "ami-0c02fb55956c7d316",
    "us-west-2": "ami-0885b1f6bd170450c",
    "ap-south-1": "ami-0a0ad6b70e61be944"
}

T2_SMALL = "t2.small"

def get_ami_id(region):
    return AMI_ID_MAP.get(region, None)

def get_input():
    print("Enter number of nodes:")
    # master = int(input("Master nodes: "))
    data = int(input("Data nodes: "))
    ingest = int(input("Ingest nodes: "))
    kibana = int(input("Kibana nodes: "))
    return  data, ingest, kibana

class InfraManager:
    def __init__(self, region="us-east-1", key_name = "hpf-key-name"):
        self.region = region
        self.ec2 = boto3.resource("ec2", region_name=region)
        self.client = boto3.client("ec2", region_name=region)
        self.key_name = key_name
        self.create_key_pair(
            key_name=self.key_name,
            save_path=f"{self.key_name}.pem"
        )
        self.security_group_id = self.create_security_group()

    def create_security_group(self,name="elastic-cluster-sg", description="Allow SSH, 9200, 5601", vpc_id=None):
        ec2 = boto3.client("ec2", region_name=self.region)

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

    def create_key_pair(self,key_name: str, save_path: str):
        ec2 = boto3.client("ec2", region_name=self.region)

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
        self,
        instance_type: str,
        tag_name: str = "elastic-node"
    ):
        ec2 = boto3.resource("ec2", region_name=self.region)

        ami_id = get_ami_id(self.region)
        print(f"⏳ Launching EC2 instance...{ami_id}")
        instances = ec2.create_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            KeyName=self.key_name,
            SecurityGroupIds=[self.security_group_id],
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
    data, ingest, kibana = get_input()
    print(f"Data nodes: {data}, Ingest nodes: {ingest}, Kibana nodes: {kibana}")

    infra_manager = InfraManager(region="us-east-1", key_name = "hpf-key-name")

    print("Creating infrastructure...")
    es_master_node_public_ip = infra_manager.create_ec2_instance(
        instance_type=T2_SMALL,
        tag_name="es-master-node"
    )
    
    es_data_node_public_ips = []
    for i in range(data):
        public_ip = infra_manager.create_ec2_instance(
            instance_type=T2_SMALL,
            tag_name=f"es-data-node-{i+1}"
        )
        es_data_node_public_ips.append(public_ip)
    
    es_ingest_node_public_ips = []
    for i in range(ingest):
        public_ip = infra_manager.create_ec2_instance(
            instance_type=T2_SMALL,
            tag_name=f"es-ingest-node-{i+1}"
        )
        es_ingest_node_public_ips.append(public_ip)
        
    es_kibana_node_public_ips = []
    for i in range(kibana):
        public_ip = infra_manager.create_ec2_instance(
            instance_type=T2_SMALL,
            tag_name=f"es-kibana-node-{i+1}"
        )
        es_kibana_node_public_ips.append(public_ip)
    
    print("\nInfrastructure created successfully!")
    
    
    # Install elasticsearch and Kibana on the nodes
    
    
    
    
if __name__ == "__main__":
    main()
