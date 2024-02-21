def Lambda(aws):
    # aws.SNS.create(Name)

    aws.Function.fetch()

    # Lambda = "demo0"
    #
    # with open("./Lambda.py", 'r') as file: Code = file.read()
    # aws.Function.create(Lambda, Code)
    #
    # payload = {
    #     "key1": "value1",
    #     "key2": "value2"
    # }
    # res = aws.Function.Class.Invoke(Lambda, payload)
    # print(res)

    #res = aws.Role.Class.query('list_item/AssumeRolePolicyDocument/Statement/list_item/Principal/Service')
    # res = aws.Subnet.Class.query('list_item')
    # for key, dict in res.items():
    #     print(f"{key}: {dict}")

    # csv = ""
    # firstkey = None
    # for key in res:
    #     csv += key + ", "
    #     if firstkey is None: firstkey = key
    # csv += "\n"

    # if firstkeyis not None:
    #     for idx in range(0, len(res[firstkey])):
    #         line = ""
    #         for key in res:
    #             line += str(res[key][idx]) + ", "
    #         csv += line + "\n"

    # with open("query.csv", "w", encoding="utf-8") as file: file.write(csv)
