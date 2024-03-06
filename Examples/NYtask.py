def NYTask(aws):
    Name = "Pavel"

    vpc = aws.Vpc.create(Name, '10.3.0.0/16')
    
    sg  = aws.SecurityGroup.create(Name, f"Security group for {Name}", vpc)
    aws.SecurityGroupRule.create(sg, 'tcp', 22, '0.0.0.0/0') # SSH (22)
    aws.SecurityGroupRule.create(sg, 'tcp', 80, '0.0.0.0/0') # HTTP (80)

    key = aws.KeyPair.create(Name)


    # Private subnet
    Name0 = Name + "-Private"
    snPublic = aws.Subnet.create(Name0, vpc, '10.3.0.0/24')

    igw = aws.InternetGateway.create(Name)
    aws.InternetGatewayAttachment.create(igw, vpc)

    rtbPublic = aws.RouteTable.create(Name0, vpc)
    aws.RouteTableAssociation.create(rtbPublic, snPublic)
    aws.Route.create(rtbPublic, "0.0.0.0/0", igw)

    ec20 = aws.EC2.create(Name0,
        aws.Const["EC2.ImageId.Linux"], aws.Const["EC2.InstanceType"],
        key, snPublic, [sg], "10.3.0.10", aws.Const["EC2.UserData.Apache"],
    )


    # Public subnet
    Name1 = Name + "-Public"
    snPrivate = aws.Subnet.create(Name1, vpc, '10.3.1.0/24')

    eip = aws.ElasticIP.create(Name1)
    nat = aws.NATGateway.create(Name1, snPrivate, eip)

    rtbPrivate  = aws.RouteTable.create(Name1, vpc)
    aws.RouteTableAssociation.create(rtbPrivate, snPrivate)
    aws.Route.create(rtbPrivate, "0.0.0.0/0", None, nat)

    ec21 = aws.EC2.create(Name1,
        aws.Const["EC2.ImageId.Linux"], aws.Const["EC2.InstanceType"],
        key, snPrivate, [sg], "10.3.1.10", aws.Const["EC2.UserData.Apache"],
    )


    aws.draw()
