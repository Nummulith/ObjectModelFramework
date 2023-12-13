import boto3

# Initialize the EC2 client
ec2 = boto3.client('ec2', region_name='eu-central-1')  # AWS region

# Set the parameters for creating the instance
instance_params = {
    'ImageId': 'ami-0669b163befffbdfc',  # desired AMI ID
    'InstanceType': 't2.micro',  # instance type
    'KeyName': 'ts',  # EC2 key pair
    'MinCount': 1,
    'MaxCount': 1
}

# Create the EC2 instance
response = ec2.run_instances(**instance_params)

# Get the instance ID from the response
instance_id = response['Instances'][0]['InstanceId']
print(f"Instance ID: {instance_id}")
