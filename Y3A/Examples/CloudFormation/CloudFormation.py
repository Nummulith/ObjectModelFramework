def CloudFormation(aws):
    Stack = "demo0"
    with open("./Y3A/Examples/CloudFormation/Lambda.yaml", 'r') as file: yaml = file.read()
#    params = {'KeyName': 'your-key-name', 'InstanceType': 't2.micro'}

    resp = aws.CloudFormation_Stack.create(Stack, yaml)
    print(resp)
