def clean(aws):
    Lambda = "demo0"
    aws.Lambda_Function.delete(Lambda)
