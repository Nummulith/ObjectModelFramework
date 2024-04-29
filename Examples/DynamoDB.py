def DynamoDB_Table(aws):
    aws.DynamoDB_Table.fetch()

    id = "DB-Pavel"
    aws.DynamoDB_Table.create(id)

    aws.draw()

    aws.DynamoDB_Table.delete(id)
