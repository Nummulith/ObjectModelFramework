def RDS(aws):
    aws.Vpc.fetch()
    aws.Subnet.fetch()
    aws.DBSubnetGroup.fetch()
    aws.DBInstance.fetch()

    dbsgname = "default-vpc-0525cb89b520dc144"
    # dbsgname = aws.DBSubnetGroup.create( 
    #     dbsgname,
    #     "dbsg Description",
    #     ["subnet-0a0e70b2c10a4c152","subnet-01c500e6d13f52a29"]
    # )
    # print(dbsgname)


    dbi = "dbinstance-pavel-1"
    dbi = aws.DBInstance.create(
        dbi,
        dbsgname,
        "DBAdmin",
        "DBPass123!"
    )

    aws.draw()

    aws.DBInstance.delete(dbi)
