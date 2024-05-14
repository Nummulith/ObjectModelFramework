def API(aws):
    print("((( ---")

    name = "pavel-api"

    with open("./Y3A/Examples/API/API.yaml", 'r') as file: yaml = file.read()
    aws.CloudFormation_Stack.create(name, yaml) # , {'Name': name}

    with open("./Y3A/Examples/API/lambda.py", 'r') as file: Code = file.read()
    aws.Lambda_Function.Class.update_code(name, Code)

    print("--- )))")
