import boto3

vpcs = boto3.client('ec2').describe_vpcs()['Vpcs']

# Выведите информацию о каждой VPC
for vpc in vpcs:
    vpc_id = vpc['VpcId']
    cidr_block = vpc['CidrBlock']
    print(f"VPC ID: {vpc_id}, CIDR Block: {cidr_block}")
