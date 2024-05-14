import boto3

name = "pavel-api"


def API(aws):
    print("((( --- API")

    with open("./Y3A/Examples/API/API.yaml", 'r') as file: yaml = file.read()
    aws.CloudFormation_Stack.create(name, yaml) # , {'Name': name}

    print("--- )))")

    update(aws)


def uploadfile(aws):
    bucket_name = name + ".cctstudents.com"
    file_path = './Y3A/Examples/API/index.html'
    s3_key = 'index.html'

    aws.S3_Bucket.Class.upload_file(bucket_name, s3_key, file_path)
    aws.S3_Bucket.Class.put_object_acl(bucket_name, s3_key, 'public-read')


def update(aws):
    print("((( --- update")

    with open("./Y3A/Examples/API/lambda.py", 'r') as file: Code = file.read()
    aws.Lambda_Function.Class.update_code(name, Code)

    uploadfile(aws)

    print("--- )))")


def clean(aws):
    print("((( --- clean")

    aws.S3_Bucket.Class.clear_bucket(f"{name}.cctstudents.com")
    aws.CloudFormation_Stack.delete(name)

    print("--- )))")
