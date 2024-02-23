def RDS(aws):
    aws.Vpc.fetch()
    aws.Subnet.fetch()
    aws.DBSubnetGroup.fetch()
    aws.DBInstance.fetch()

    dbsgname = "default-vpc-0525cb89b520dc144"
    aws.DBSubnetGroup.create( 
        dbsgname,
        "dbsg Description",
        ["subnet-0a0e70b2c10a4c152","subnet-01c500e6d13f52a29"]
    )

    dbi = "dbinstance-pavel-1"
    aws.DBInstance.create(
        dbi,
        dbsgname,
        "DBAdmin",
        "DBPass123!"
    )

    aws.draw()

    aws.DBInstance.delete(dbi)
