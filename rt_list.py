import boto3

# Create EC2 client
ec2 = boto3.client('ec2')

# List route tables
response = ec2.describe_route_tables()

# Print route table details
print("List of Route Tables:")
for route_table in response['RouteTables']:
    print(f"Route Table ID: {route_table['RouteTableId']}")
    print(f"VPC ID: {route_table['VpcId']}")
    print("Routes:")
    for route in route_table['Routes']:
        print(f"- Destination CIDR: {route.get('DestinationCidrBlock', 'N/A')}")
        print(f"  Target: {route.get('GatewayId', 'N/A')} | {route.get('InstanceId', 'N/A')} | {route.get('NatGatewayId', 'N/A')} | {route.get('NetworkInterfaceId', 'N/A')}")
    print("------------------------------")
