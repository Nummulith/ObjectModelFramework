def RDS(aws):
    aws.Vpc.Fetch()
    aws.Subnet.Fetch()
    aws.DBSubnetGroup.Fetch()
    aws.DBInstance.Fetch()

    dbsgname = "default-vpc-0525cb89b520dc144"
    # dbsgname = aws.DBSubnetGroup.Create( 
    #     dbsgname,
    #     "dbsg Description",
    #     ["subnet-0a0e70b2c10a4c152","subnet-01c500e6d13f52a29"]
    # )
    # print(dbsgname)


    dbi = "dbinstance-pavel-1"
    # dbi = aws.DBInstance.Create(
    #     dbi,
    #     dbsgname,
    #     "DBAdmin",
    #     "DBPass123!"
    # )
    # print(dbi)

    aws.DBInstance.Delete(dbi)
