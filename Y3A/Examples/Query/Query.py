    #res = aws.IAM_Role.Class.query('list_item/AssumeRolePolicyDocument/Statement/list_item/Principal/Service')
    # res = aws.EC2_Subnet.Class.query('list_item')
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
