import boto3

# Create EC2 client
ec2 = boto3.client('ec2')

# List Network ACLs
response = ec2.describe_network_acls()

# Print Network ACL details
print("List of Network ACLs:")
for acl in response['NetworkAcls']:
    print(f"ACL ID: {acl['NetworkAclId']}")
    print(f"VPC ID: {acl['VpcId']}")
    print("Inbound Rules:")
    for entry in acl['Entries']:
        print(f"- Rule Number: {entry['RuleNumber']}")
        print(f"  Protocol: {entry['Protocol']}")
        print(f"  Port Range: {entry.get('PortRange', 'N/A')}")
        print(f"  Rule Action: {entry['RuleAction']}")
        print(f"  Cidr Block: {entry['CidrBlock']}")
    print("------------------------------")
