def CloudFormation(aws):
    Stack = "demo0"
    yaml = "APIGW_Lambda" # APIGateWay # APIGW_Lambda # Lambda

    with open(f"./Y3A/Examples/CloudFormation/{yaml}.yaml", 'r') as file: yaml = file.read()

#    params = {'KeyName': 'your-key-name', 'InstanceType': 't2.micro'}
    cf = aws.CloudFormation_Stack.create(Stack, yaml)

def clean(aws):
    Lambda = "demo0"
    aws.CloudFormation_Stack.delete(Lambda)
