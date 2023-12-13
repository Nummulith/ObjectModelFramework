import boto3

# Create EC2 client
ec2 = boto3.client('ec2')

# List Internet Gateways
response = ec2.describe_internet_gateways()

# Print Internet Gateway details
print("List of Internet Gateways:")
for gateway in response['InternetGateways']:
    print(f"Internet Gateway ID: {gateway['InternetGatewayId']}")
    print(f"Attached VPCs:")
    for attachment in gateway.get('Attachments', []):
        print(f"- VPC ID: {attachment['VpcId']}")
    print("------------------------------")
