[ReadMe.md](../ReadMe.md) \ [Yet Another AWS Analyser](Yet_Another_AWS_Analyser.md)

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
The Yet Another AWS Analyser project extends the functionality of the [Object Model Framework](Object_Model_Framework.md) by incorporating a comprehensive set of AWS (Amazon Web Services) objects. This integration enables users to seamlessly manage, visualize, and interact with various AWS resources within the same framework.

## Key Features
- AWS Object Representation
    - The project introduces a set of AWS resource types, encapsulated as classes using the Object Model Framework.
- Unified Management
    - Users can create, retrieve, and delete AWS objects using the same principles established in the Object Model Framework. The integration allows for consistent interaction with AWS resources alongside user-defined classes.
- Graph Visualization Enhancement
    - The graph visualization feature of the Object Model Framework is extended to support AWS objects. Relationships between AWS objects are visualized, providing a clear representation of the AWS infrastructure.

## Supported AWS Resources

VPC Resources:
```
EC2_VPC, KeyPairInfo
EC2_SecurityGroup, EC2_SecurityGroup_Rule
EC2_InternetGateway, EC2_VPCGatewayAttachment
EC2_NetworkAcl, EC2_NetworkAclEntry
```

SUBNET Resources:
```
EC2_Subnet
EC2_RouteTable, EC2_Route, EC2_RouteTable_Association
EC2_EIP
EC2_NatGateway, EC2_EIPAssociation
```

RDS Resources:
```
RDS_DBSubnetGroup, RDS_DBSubnetGroup_Subnet,
RDS_DBInstance,
DynamoDB_Table
```

AWS_AMI Resources:
```
IAM_User, IAM_Group, IAM_Role
```

OTHER Resources:
```
EC2_Reservation
Instance
EC2_NetworkInterface
S3_Bucket
SNS_Topic
Lambda_Function (Lambda)
```

## Example

[Source code](../Examples/NYtask.py)

<img src="../img/Y3A-Demo.png">

| Read Me       | Yet Another AWS Analyser | Object Model Framework | Graph Drawing Utility |
| ------------- | ------------------------ | ---------------------- | --------------------- |
| [<img src="../img/Home.png" width="100" height="100">](../ReadMe.md) | [<img src="../img/Yet_Another_AWS_Analyser.png" width="100" height="100">](../docs/Yet_Another_AWS_Analyser.md) | [<img src="../img/Object_Model_Framework.png" width="100" height="100">](../docs/Object_Model_Framework.md) | [<img src="../img/Graph_Drawing_Utility.png" width="100" height="100">](../docs/Graph_Drawing_Utility.md) |