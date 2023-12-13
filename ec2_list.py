import boto3

# Create an EC2 client
ec2 = boto3.client('ec2')

# List all instances
response = ec2.describe_instances()

# Print instance details
print("List of EC2 Instances:")
for reservation in response['Reservations']:
    #print(f"reservation ID: {reservation['Instances']}")
    for instance in reservation['Instances']:
        print(f"Instance ID: {instance['InstanceId']}")
        print(f"Instance Type: {instance['InstanceType']}")
        print(f"Public IP Address: {instance.get('PublicIpAddress', 'N/A')}")
        print(f"Private IP Address: {instance.get('PrivateIpAddress', 'N/A')}")
        print("------------------------------")
