import boto3

# Create EC2 client
ec2 = boto3.client('ec2')

# List NAT Gateways
response = ec2.describe_nat_gateways()

# Print NAT Gateway details
print("List of NAT Gateways:")
for nat_gateway in response['NatGateways']:
    print(f"NAT Gateway ID: {nat_gateway['NatGatewayId']}")
    print(f"Subnet ID: {nat_gateway['SubnetId']}")
    print(f"State: {nat_gateway['State']}")
    print("------------------------------")
