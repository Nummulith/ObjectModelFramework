name = "pavel-api"

def API(aws):
    print("((( --- API")

    with open("./Y3A/Examples/API/API.yaml", 'r') as file: yaml = file.read()
    aws.CloudFormation_Stack.create(name, yaml) # , {'Name': name}

    print("--- )))")

    update(aws)

def update(aws):
    print("((( --- update")

    with open("./Y3A/Examples/API/lambda.py", 'r') as file: Code = file.read()
    aws.Lambda_Function.Class.update_code(name, Code)

    print("--- )))")

def clean(aws):
    print("((( --- clean")

    Lambda = "pavel-api"
    aws.CloudFormation_Stack.delete(Lambda)

    print("--- )))")
