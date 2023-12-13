import boto3

# Create EC2 client
ec2 = boto3.client('ec2')  # Replace 'your_region' with your desired AWS region

# List all subnets
response = ec2.describe_subnets()

# Print subnet details
print("List of Subnets:")
for subnet in response['Subnets']:
    print(f"Subnet ID: {subnet['SubnetId']}")
    print(f"VPC ID: {subnet['VpcId']}")
    print(f"CIDR Block: {subnet['CidrBlock']}")
    print(f"Availability Zone: {subnet['AvailabilityZone']}")
    print("------------------------------")
