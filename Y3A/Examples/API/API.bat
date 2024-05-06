@echo off
rem Base64 encode lambda.py content
rem for /f %%i in ('powershell -Command "[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((Get-Content -Raw lambda.py)))"') do set encodedFileContent=%%i

rem Create CloudFormation stack
rem aws cloudformation create-stack --stack-name PavelAPIStack --template-body file://API//API.yaml --parameters ParameterKey=LambdaCode,ParameterValue=%encodedFileContent%

aws cloudformation create-stack --stack-name PavelAPIStack --template-body file://API//API.yaml
