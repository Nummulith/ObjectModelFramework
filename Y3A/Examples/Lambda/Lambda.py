def Lambda(aws):
    # aws.Lambda_Function.fetch()

    Lambda = "demo0"
    Role = "arn:aws:iam::047989593255:role/service-role/tomasz-api-hello-world-role-53pra235"
    payload = {
        "key1": "value1",
        "key2": "value2"
    }
    
    with open("./Y3A/Examples/Lambda/initial.py", 'r') as file: Code = file.read()
    aws.Lambda_Function.create(Lambda, Code, Role)
    
    res = aws.Lambda_Function.Class.invoke(Lambda, payload)
    print(f"First call: {res}")

    with open("./Y3A/Examples/Lambda/modified.py", 'r') as file: Code = file.read()
    aws.Lambda_Function.Class.update_code(Lambda, Code)

    res = aws.Lambda_Function.Class.invoke(Lambda, payload)
    print(f"Second call: {res}")
