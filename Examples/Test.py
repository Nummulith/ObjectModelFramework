from awsClasses import PAR

def Test(aws):
    print("(---")

    key_pair_name = "Pavel"

    # objs = aws.KeyPair.fetch(
    #     filter = {"KeyNames" : (["key-" + key_pair_name], PAR.PAR)},
    #     create_par = {"name": key_pair_name}
    # )
    objs = aws.KeyPair.objects()

    for obj in objs:
        print(f"{obj.KeyPairId} - {obj.KeyName}")


    # objs = aws.EC2.fetch(
    #     {"instance-state-name" : (['running'], PAR.FILTER)}
    # )
    # objs = aws.EC2.fetch({"key-name" : ([key_pair_name], PAR.FILTER)})
    objs = aws.EC2.objects()

    for obj in objs:
        cur_key_pair_name = obj.KeyPairId.KeyName if hasattr(obj, "KeyPairId") else "-"
        print(f"{obj.Tag_Name} : {cur_key_pair_name} - {obj.PublicIpAddress}")

    print("---)")
