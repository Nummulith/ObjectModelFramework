def DynamoDB(aws):
    aws.DynamoDB.fetch()

    id = "DB-Pavel"
    aws.DynamoDB.create(id)

    aws.draw()

    aws.DynamoDB.delete(id)
