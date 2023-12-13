import boto3
import json
from datetime import datetime

# Custom JSON serializer for datetime objects
def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f'Type {type(obj)} not serializable')

# Create an EC2 client
ec2 = boto3.client('ec2')

# List all instances
response = ec2.describe_instances()

# Print the entire response as JSON
print(json.dumps(response, default=json_serial, indent=2))
