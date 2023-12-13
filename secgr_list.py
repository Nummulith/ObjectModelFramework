import boto3

# Create EC2 client
ec2 = boto3.client('ec2')

# List security groups
response = ec2.describe_security_groups()

# Print security group details
print("List of Security Groups:")
for group in response['SecurityGroups']:
    print(f"Group Name: {group['GroupName']}")
    print(f"Group ID: {group['GroupId']}")
    print(f"VPC ID: {group['VpcId']}")
    print("IP Permissions:")
    for permission in group['IpPermissions']:
        print(f"- From Port: {permission.get('FromPort', 'N/A')}")
        print(f"  To Port: {permission.get('ToPort', 'N/A')}")
        print(f"  Protocol: {permission.get('IpProtocol', 'N/A')}")
        print("  IP Ranges:")
        for ip_range in permission.get('IpRanges', []):
            print(f"  - {ip_range.get('CidrIp', 'N/A')}")
    print("------------------------------")
