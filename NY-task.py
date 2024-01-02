from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt

import boto3

from xml.dom import minidom
import xml.etree.ElementTree as ET

import json
from datetime import datetime

import re

def prettify(elem):
    rough_string = ET.tostring(elem, "utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")

def Prefix(field):
    match = re.match(r'^([^_]+)_?', field)
    return match.group(1) if match else field

class MyWidget(QWidget):

    def fullresponse(self):
        # Custom JSON serializer for datetime objects
        def json_serial(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f'Type {type(obj)} not serializable')

        # Create an EC2 client
        ec2 = boto3.client('ec2')

        # List all instances
        response = ec2.describe_instances()

        # Print the entire response as JSON
        print(json.dumps(response, default=json_serial, indent=2))

    def CreateInput(self, field):
        pref = Prefix(field)

        edit = True
        check = False
        buttons = True
        if pref == "Region":
            buttons = False
        elif pref == "VPCIGW" or pref == "RTBSN" or pref == "RT":
            edit = False
            check = True
        elif pref == "CIDR":
            buttons = False

        self.Fields.append(field)

        #field = layout.objectName().replace("_Layout", "")
        layout = getattr(self, field + "_Layout")

        if edit:
            label = QtWidgets.QLabel(field, self)
            label.setFixedWidth(64)
            layout.addWidget(label)

            line_edit = QtWidgets.QLineEdit(self)
            line_edit.setObjectName(field + "_Id")
            layout.addWidget(line_edit)

        if check:
            check_box = QtWidgets.QCheckBox(field, self)
            check_box.setObjectName(field + "_Flag")
            layout.addWidget(check_box)

        if buttons:
            add_button = QtWidgets.QPushButton("+", self)
            add_button.setObjectName(field + "_Add")
            add_button.setFixedWidth(32)
            add_button.clicked.connect(lambda: self.Add_Clicked(field))
            layout.addWidget(add_button)

            del_button = QtWidgets.QPushButton("-", self)
            del_button.setObjectName(field + "_Del")
            del_button.setFixedWidth(32)
            del_button.clicked.connect(lambda: self.Del_Clicked(field))
            layout.addWidget(del_button)

    def Val(self, field, setval = None):
        line_edit = self.findChild(QtWidgets.QLineEdit, field + "_Id")
        if line_edit != None:
            if setval != None:
                line_edit.setText(setval)

            return line_edit.text()

        check_box = self.findChild(QtWidgets.QCheckBox, field + "_Flag")
        if check_box != None:
            if setval != None:
                if type(setval) == str:
                    setval = setval == "True"
                check_box.setChecked(setval)

            return check_box.isChecked()
        

    def addTag(self, resource_id, name, value):
        self.boto3ec2.create_tags(
            Resources=[resource_id],
            Tags=[
                {
                    'Key': name,
                    'Value': value
                },
            ]
        )


    def Add_Clicked(self, field):
        pref = Prefix(field)

        try:
            if pref == "VPC":
                response = self.boto3ec2.create_vpc(CidrBlock='10.3.0.0/16')
                vpc_id = response['Vpc']['VpcId']

                self.addTag(vpc_id, "Name", "vpc-Pavel-Eresko")

                self.Val(field, vpc_id)

            elif pref == "IGW":
                response = self.boto3ec2.create_internet_gateway()
                internet_gateway_id = response['InternetGateway']['InternetGatewayId']

                self.addTag(internet_gateway_id, "Name", "igw-Pavel-Eresko")

                self.Val(field, internet_gateway_id)

            elif pref == "VPCIGW":
                response = self.boto3ec2.attach_internet_gateway(
                    InternetGatewayId=self.Val("IGW"),
                    VpcId = self.Val("VPC")
                )

                self.Val(field, True)

            elif pref == "SN":
                response = self.boto3ec2.create_subnet(
                    VpcId = self.Val("VPC"),
                    CidrBlock = self.Val(field.replace("SN_", "CIDR_")),
    #                AvailabilityZone='us-east-1a'
                )

                subnet_id = response["Subnet"]["SubnetId"]

                self.addTag(subnet_id, "Name", "subnet-Pavel-Eresko-" + field.replace("SN_", ""))

                self.Val(field, subnet_id)

            elif pref == "RTB":

                response = self.boto3ec2.create_route_table(
                    VpcId = self.Val("VPC")
                )

                route_table_id = response['RouteTable']['RouteTableId']

                self.addTag(route_table_id, "Name", "rtb-Pavel-Eresko-" + field.replace("RTB_", ""))

                self.Val(field, route_table_id)


            elif pref == "RTBSN":

                response = self.boto3ec2.associate_route_table(
                    SubnetId = self.Val(field.replace("RTBSN_", "SN_")),
                    RouteTableId = self.Val(field.replace("RTBSN_", "RTB_"))
                )
                
                self.Val(field, True)


            elif pref == "RT":
                if field == "RT_Public":
                    GatewayId = self.Val("IGW")

                    response = self.boto3ec2.create_route(
                        RouteTableId = self.Val(field.replace("RT_", "RTB_")),
                        DestinationCidrBlock = "0.0.0.0/0",
                        GatewayId = GatewayId
                    )

                else:
                    NATId = self.Val("NAT")

                    response = self.boto3ec2.create_route(
                        RouteTableId = self.Val(field.replace("RT_", "RTB_")),
                        DestinationCidrBlock = "0.0.0.0/0",
                        NatGatewayId = NATId
                    )

                self.Val(field, True)

            elif pref == "EIP":
                response = self.boto3ec2.allocate_address(
                    Domain='vpc'
                )
                eip_allocation_id = response['AllocationId']
                self.addTag(eip_allocation_id, "Name", "eipassoc-Pavel-Eresko-NAT")
                self.Val(field, eip_allocation_id)


            elif pref == "NAT":
                response = self.boto3ec2.create_nat_gateway(
                    SubnetId = self.Val("SN_Public"),
                    AllocationId = self.Val("EIP")
                )

                nat_gateway_id = response['NatGateway']['NatGatewayId']

                self.addTag(nat_gateway_id, "Name", "nat-Pavel-Eresko")

                self.Val(field, nat_gateway_id)


            elif pref == "KEY":
                key_name = self.Val(field)

                response = self.boto3ec2.create_key_pair(KeyName=key_name)
                private_key = response['KeyMaterial']
                    
                with open(f'{key_name}.pem', 'w') as key_file:
                    key_file.write(private_key)


            elif pref == "EC2":

                user_data = ""\
                    + "#!/bin/bash\n"\
                    + "yum update -y\n"\
                    + "yum install httpd -y\n"\
                    + "systemctl start httpd\n"\
                    + "systemctl enable httpd\n"
                

                response = self.boto3ec2.run_instances(
                    ImageId = 'ami-0669b163befffbdfc',
                    InstanceType = 't2.micro',
#                    SubnetId = self.Val(field.replace("EC2_", "SN_")),
                    KeyName  = self.Val("KEY"),
                    NetworkInterfaces=[
                        {
                            'SubnetId': self.Val(field.replace("EC2_", "SN_")),
                            'DeviceIndex': 0,
                            'AssociatePublicIpAddress': True,
                            'PrivateIpAddress': ("10.3.0.10" if field == "EC2_Public" else "10.3.1.10"),
                            'Groups': [self.Val("SG")]  # Идентификаторы Security Group
                        }
                    ],
                    UserData=user_data,
                    MinCount = 1,
                    MaxCount = 1
                )
                instance_id = response['Instances'][0]['InstanceId']

                self.addTag(instance_id, "Name", "i-Pavel-Eresko-" + field.replace("EC2_", ""))

                self.Val(field, instance_id)


            elif pref == "SG":

                response = self.boto3ec2.create_security_group(
                    GroupName = "SSH-HTTP",
                    Description = "security group by Pavel Eresko",
                    VpcId = self.Val("VPC")
                )
                security_group_id = response['GroupId']

                self.addTag(security_group_id, "Name", "sg-Pavel-Eresko-" + field.replace("SG_", ""))

                self.Val(field, security_group_id)

                response = self.boto3ec2.authorize_security_group_ingress( # SSH (22)
                    GroupId=security_group_id,
                    IpPermissions=[
                        {
                            'IpProtocol': 'tcp',
                            'FromPort': 22,
                            'ToPort': 22,
                            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                        }
                    ]
                )
                SRId = response["SecurityGroupRules"][0]["SecurityGroupRuleId"]

                response = self.boto3ec2.authorize_security_group_ingress( # HTTP (80)
                    GroupId=security_group_id,
                    IpPermissions=[
                        {
                            'IpProtocol': 'tcp',
                            'FromPort': 80,
                            'ToPort': 80,
                            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                        }
                    ]
                )



        except Exception as e:
            print(f"{e}")


    def Del_Clicked(self, field):
        pref = Prefix(field)

        try:
            if pref == "VPC":
                response = self.boto3ec2.delete_vpc(VpcId = self.Val(field))
                self.Val(field, "")

            elif pref == "IGW":
                response = self.boto3ec2.delete_internet_gateway(InternetGatewayId = self.Val(field))
                self.Val(field, "")

            elif pref == "VPCIGW":
                response = self.boto3ec2.detach_internet_gateway(
                        InternetGatewayId=self.Val("IGW"),
                        VpcId = self.Val("VPC")
                    )
                self.Val(field, False)

            elif pref == "SN":
                response = self.boto3ec2.delete_subnet(
                    SubnetId = self.Val(field)
                )
                self.Val(field, "")

            elif pref == "RTB":
                response = self.boto3ec2.delete_route_table(
                    RouteTableId = self.Val(field)
                )                
                self.Val(field, "")

            elif pref == "RTBSN":

                response = self.boto3ec2.describe_route_tables(
                    RouteTableIds=[self.Val(field.replace("RTBSN_", "RTB_"))]
                )
                associations = response['RouteTables'][0].get('Associations', [])

                association_id = ""
                for assoc in associations:
                    if 'SubnetId' in assoc and assoc['SubnetId'] == self.Val(field.replace("RTBSN_", "SN_")):
                        association_id = assoc['RouteTableAssociationId']
                        break

                response = self.boto3ec2.disassociate_route_table(
                    AssociationId=association_id
                )
                self.Val(field, False)

            elif pref == "RT":
                response = self.boto3ec2.delete_route(
                    RouteTableId = self.Val(field.replace("RT_", "RTB_")),
                    DestinationCidrBlock = "0.0.0.0/0"
                )
                self.Val(field, False)

            elif pref == "KEY":
                response = self.boto3ec2.delete_key_pair(
                    KeyName = self.Val(field)
                )

            elif pref == "EC2":
                response = self.boto3ec2.terminate_instances(
                    InstanceIds=[self.Val(field)]
                )
                self.Val(field, "")

            elif pref == "SG":
                response = self.boto3ec2.delete_security_group(
                    GroupId=self.Val(field)
                )
                self.Val(field, "")


        except Exception as e:
            print(f"{e}")


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        self.Save()
        event.accept()

    def Save(self):
        xml = ET.Element("Fields")
        for field in self.Fields:
            val = self.Val(field)
            if type(val) == bool:
                val = "True" if val else "False"
            xml.set(field, val)

        with open("NY-task.cfg", "w") as xml_file:
            xml_file.write(prettify(xml))


    def Load(self):
        try:
            xml = ET.parse("NY-task.cfg").getroot()
        except FileNotFoundError:
            return
        
        for field in self.Fields:
            if field in xml.attrib:
                val = xml.attrib[field]
                self.Val(field, val)


    def __init__(self):
        super(MyWidget, self).__init__()
        loadUi('NY-task.ui', self)


        self.Fields = []
        for layout in self.findChildren(QtWidgets.QHBoxLayout):
            self.CreateInput(layout.objectName().replace("_Layout", ""))

        # self.CreateInput("Region")
        # self.CreateInput("VPC")
        # self.CreateInput("IGW" )
        # self.CreateInput("VPCIGW", False, True)
        # self.CreateInput("Subnet_A")
        # self.CreateInput("Subnet_B")
        # self.CreateInput("EC2")


        self.Val("Region", 'eu-central-1')

        self.boto3ec2 = boto3.client('ec2', region_name = self.Val("Region"))

        self.Load()


if __name__ == '__main__':
    app = QApplication([])
    widget = MyWidget()
    widget.show()
    app.exec_()
