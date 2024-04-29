def NYTask(aws):
    Name = "Pavel"

    vpc = aws.EC2_VPC.create(Name, '10.3.0.0/16')
    
    sg  = aws.EC2_SecurityGroup.create(Name, f"Security group for {Name}", vpc)
    aws.EC2_SecurityGroup_Rule.create(sg, 'tcp', 22, '0.0.0.0/0') # SSH (22)
    aws.EC2_SecurityGroup_Rule.create(sg, 'tcp', 80, '0.0.0.0/0') # HTTP (80)

    key = aws.EC2_KeyPair.create(Name)


    # Private subnet
    Name0 = Name + "-Private"
    snPublic = aws.EC2_Subnet.create(Name0, vpc, '10.3.0.0/24')

    igw = aws.EC2_InternetGateway.create(Name)
    aws.EC2_VPCGatewayAttachment.create(igw, vpc)

    rtbPublic = aws.EC2_RouteTable.create(Name0, vpc)
    aws.EC2_RouteTable_Association.create(rtbPublic, snPublic)
    aws.EC2_Route.create(rtbPublic, "0.0.0.0/0", igw)

    ec20 = aws.EC2_Instance.create(Name0,
        aws.Const["EC2.ImageId.Linux"], aws.Const["EC2.InstanceType"],
        key, snPublic, [sg], "10.3.0.10", aws.Const["EC2.UserData.Apache"],
    )


    # Public subnet
    Name1 = Name + "-Public"
    snPrivate = aws.EC2_Subnet.create(Name1, vpc, '10.3.1.0/24')

    eip = aws.EC2_EIP.create(Name1)
    nat = aws.EC2_NatGateway.create(Name1, snPrivate, eip)

    rtbPrivate  = aws.EC2_RouteTable.create(Name1, vpc)
    aws.EC2_RouteTable_Association.create(rtbPrivate, snPrivate)
    aws.EC2_Route.create(rtbPrivate, "0.0.0.0/0", None, nat)

    ec21 = aws.EC2_Instance.create(Name1,
        aws.Const["EC2.ImageId.Linux"], aws.Const["EC2.InstanceType"],
        key, snPrivate, [sg], "10.3.1.10", aws.Const["EC2.UserData.Apache"],
    )


    aws.draw()
