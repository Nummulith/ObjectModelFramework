<table style="width: 100%">
  <thead>
    <tr>
        <th>
            <h1>Yet Another AWS Analyser</h1>
        </th>
        <th>
            <img src="../img/Yet_Another_AWS_Analyser.png" width="100" height="100">
        </th>
    </tr>
  </thead>
</table>

## Overview
The AWS Object Model Integration project extends the functionality of the previously mentioned Object Model Framework by incorporating a comprehensive set of AWS (Amazon Web Services) objects. This integration enables users to seamlessly manage, visualize, and interact with various AWS resources within the same framework, leveraging the capabilities provided by both projects.

AWS Object Model Integration: Managing AWS Resources as Code
This project introduces the concept of managing AWS resources as code within the framework of the Object Model. With the AWS Object Model Integration, you can seamlessly handle VPCs, subnets, RDS instances, AMIs, and more, treating your AWS infrastructure as code for automated and efficient management.



## Key Features
AWS Object Representation:

The project introduces a set of AWS objects organized into categories such as VPC, SUBNET, RDS, AMI, and OTHER.
Each category includes specific AWS resource types, encapsulated as classes using the Object Model Framework.
Unified Management:

Users can create, retrieve, and delete AWS objects using the same principles established in the Object Model Framework.
The integration allows for consistent interaction with AWS resources alongside user-defined classes.
Graph Visualization Enhancement:

The graph visualization feature of the Object Model Framework is extended to support AWS objects.
Relationships between AWS objects are visualized, providing a clear representation of the AWS infrastructure.
Example Use Case:

Users can, for example, create VPCs, subnets, security groups, and other AWS resources using the same dynamic instantiation and deletion methods.

Integration with the Object Model Framework
This project builds upon the Object Model Framework, combining its flexibility and object-oriented principles with the vast array of AWS resources, resulting in a powerful and unified tool for managing diverse infrastructures.

## Supported AWS Resource Categories
VPC Resources:

boto3.ec2.Vpc
boto3.ec2.KeyPairInfo
boto3.ec2.SecurityGroup
boto3.ec2.SecurityGroupRule
boto3.ec2.InternetGateway
boto3.ec2.InternetGatewayAttachment
boto3.ec2.NetworkAcl
boto3.ec2.NetworkAclEntry
SUBNET Resources:
boto3.ec2.Subnet
boto3.ec2.RouteTable
boto3.ec2.Route
boto3.ec2.RouteTableAssociation
boto3.ec2.ElasticIP
boto3.ec2.NATGateway
boto3.ec2.ElasticIPAssociation
RDS Resources:
boto3.rds.DBSubnetGroup
boto3.rds.DBSubnetGroupSubnet
boto3.rds.DBInstance
boto3.dynamodb.DynamoDB
AMI Resources:
boto3.iam.User
boto3.iam.Group
boto3.iam.Role
OTHER Resources:
boto3.ec2.Reservation
boto3.ec2.Instance
boto3.ec2.NetworkInterface
boto3.s3.S3
boto3.sns.SNS
boto3.lambda_.Function

## Key Features
Unified Management:

Users can create, retrieve, and delete AWS objects using the same principles established in the Object Model Framework.
The integration allows for consistent interaction with AWS resources alongside user-defined classes.
Graph Visualization Enhancement:

The graph visualization feature of the Object Model Framework is extended to support AWS objects.
Relationships between AWS objects are visualized, providing a clear representation of the AWS infrastructure.
Example Use Case:

Users can, for example, create VPCs, subnets, security groups, and other AWS resources using the same dynamic instantiation and deletion methods.
Integration with the Object Model Framework
This project builds upon the Object Model Framework, combining its flexibility and object-oriented principles with the vast array of AWS resources, resulting in a powerful and unified tool for managing diverse infrastructures.

## Example

[Source code](../Examples/NYTask.py)

<img src="../img/Y3A-Demo.png">

| Read Me       | Yet Another AWS Analyser | Object Model Framework | Graph Drawing Utility |
| ------------- | ------------------------ | ---------------------- | --------------------- |
| [<img src="../img/Obj.png" width="100" height="100">](../ReadMe.md) | [<img src="../img/Yet_Another_AWS_Analyser.png" width="100" height="100">](../docs/Yet_Another_AWS_Analyser.md) | [<img src="../img/Object_Model_Framework.png" width="100" height="100">](../docs/Object_Model_Framework.md) | [<img src="../img/Graph_Drawing_Utility.png" width="100" height="100">](../docs/Graph_Drawing_Utility.md) |