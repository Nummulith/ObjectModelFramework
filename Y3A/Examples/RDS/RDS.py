def RDS(aws):
    aws.EC2_VPC.fetch()
    aws.EC2_Subnet.fetch()
    aws.RDS_DBSubnetGroup.fetch()
    aws.RDS_DBInstance.fetch()

    dbsgname = "default-vpc-0525cb89b520dc144"
    aws.RDS_DBSubnetGroup.create( 
        dbsgname,
        "dbsg Description",
        ["subnet-0a0e70b2c10a4c152","subnet-01c500e6d13f52a29"]
    )

    dbi = "dbinstance-pavel-1"
    aws.RDS_DBInstance.create(
        dbi,
        dbsgname,
        "DBAdmin",
        "DBPass123!"
    )

    aws.draw()

    aws.RDS_DBInstance.delete(dbi)
