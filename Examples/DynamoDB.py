def DynamoDB(aws):
    aws.DynamoDB.Fetch()

    id = "DB-Pavel"
    aws.DynamoDB.Create(id)

    aws.Draw()

    aws.DynamoDB.Delete(id)
