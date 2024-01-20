from AWSscript import AWS, awsConst

Name = "Pavel-Eresko"

aws = AWS("AWSscript.xml")
aws.Clear()

# vpc = aws.Vpc.Create(Name, '10.3.0.0/16')
# subnet = aws.Subnet.Create(Name, vpc, '10.3.0.0/24')

# sg  = aws.SecurityGroup.Create(Name, f"Security group for {Name}", vpc)
# aws.SecurityGroupRule.Create(sg, 'tcp', 22, '0.0.0.0/0') # SSH (22)
# aws.SecurityGroupRule.Create(sg, 'tcp', 80, '0.0.0.0/0') # HTTP (80)

# key = aws.KeyPair.Create(Name)

# ec2 = aws.EC2.Create(
#     Name,
#     awsConst["EC2.ImageId.Linux"], awsConst["EC2.InstanceType.t2.micro"],
#     key, subnet, [sg],
#     "10.3.0.10",
#     awsConst["EC2.UserData.Apache"],
# )

igw = aws.InternetGateway.Create(Name)

aws.Print()
aws.Clear()
