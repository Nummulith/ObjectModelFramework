def NYTask(aws):
    Name = "Pavel-Eresko"

    key = aws.KeyPair.Create(Name)

    vpc = aws.Vpc.Create(Name, '10.3.0.0/16')
    
    sg  = aws.SecurityGroup.Create(Name, f"Security group for {Name}", vpc)
    aws.SecurityGroupRule.Create(sg, 'tcp', 22, '0.0.0.0/0') # SSH (22)
    aws.SecurityGroupRule.Create(sg, 'tcp', 80, '0.0.0.0/0') # HTTP (80)

    igw = aws.InternetGateway.Create(Name)
    aws.InternetGatewayAttachment.Create(igw, vpc)


    # Private subnet
    Name0 = Name + "-Private"
    snPublic = aws.Subnet.Create(Name0, vpc, '10.3.0.0/24')

    rtbPublic  = aws.RouteTable.Create(Name0, vpc)
    aws.RouteTableAssociation.Create(rtbPublic, snPublic)
    aws.Route.Create(rtbPublic, "0.0.0.0/0", igw)

    ec20 = aws.EC2.Create(
        Name0,
        aws.Const["EC2.ImageId.Linux"], aws.Const["EC2.InstanceType"],
        key, snPublic, [sg],
        "10.3.0.10",
        aws.Const["EC2.UserData.Apache"],
    )


    # Public subnet
    Name1 = Name + "-Public"
    snPrivate = aws.Subnet.Create(Name1, vpc, '10.3.1.0/24')

    eip = aws.ElasticIP.Create(Name1)
    nat = aws.NATGateway.Create(Name1, snPrivate, eip)

    rtbPrivate  = aws.RouteTable.Create(Name1, vpc)
    aws.RouteTableAssociation.Create(rtbPrivate, snPrivate)
    aws.Route.Create(rtbPrivate, "0.0.0.0/0", None, nat)

    ec21 = aws.EC2.Create(
        Name1,
        aws.Const["EC2.ImageId.Linux"], aws.Const["EC2.InstanceType"],
        key, snPrivate, [sg],
        "10.3.1.10",
        aws.Const["EC2.UserData.Apache"],
    )
