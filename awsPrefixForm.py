from PyQt5.QtWidgets import QApplication, QWidget, QDialog
from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt

import boto3

from xml.dom import minidom
import xml.etree.ElementTree as ET

import json
from datetime import datetime

import re

import subprocess

from awsClasses import *
from ObjectModel import AWS

def prettify(elem):
    rough_string = ET.tostring(elem, "utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")

def Prefix(field):
    match = re.match(r'^([^_]+)_?', field)
    return match.group(1) if match else field

class AWS_Window(QDialog):
    def __init__(self, parent, clss, id, AddParams, DelParams):
        super(AWS_Window, self).__init__(parent)
        loadUi('awsFormClass.ui', self)
        self.MainWindow = parent

        self.Class  = clss
        self.Id.setText(id)
        self.AddParams = AddParams
        self.DelParams = DelParams

        self.pyAdd.clicked.connect(self.pyAddCall)
        self.pyDel.clicked.connect(self.pyDelCall)

        self.cliAdd.clicked.connect(self.cliAddCall)
        self.cliDel.clicked.connect(self.cliDelCall)

        self.cliAddLine.setText(clss.cli_add(self.AddParams))
        self.cliDelLine.setText(clss.cli_del(self.DelParams))

        self.Close.clicked.connect(self.accept)

    def pyAddCall(self, args):
        try:
            AddId = self.Class.create(self.AddParams)
            self.Id.setText(AddId)
        except Exception as e:
            print(f"Error: {str(e)}")        

    def pyDelCall(self, args):
        try:
            self.Class.Del(self.DelParams)
            self.Id.setText("")
        except Exception as e:
            print(f"Error: {str(e)}")        

    def psRun(self, ps_command):
        try:
            result = subprocess.run(["powershell", "-Command", ps_command], capture_output=True, text=True)
        except Exception as e:
            print(f"Error: {str(e)}")        
            return

        if result.returncode != 0:
            print("stderr:", result.stderr)            

        #print("Exit Code:", result.returncode)
        #print("stdout:", result.stdout)
        #print("stderr:", result.stderr)

    def cliAddCall(self):
        self.psRun(self.cliAddLine.toPlainText())

    def cliDelCall(self):
        self.psRun(self.cliDelLine.toPlainText())

class MyWidget(QWidget):
    prefix_map = {
        "VPC"   : (Vpc, lambda self: None, lambda self: None),
        "IGW"   : (InternetGateway, lambda self: None, lambda self: None),
        "VPCIGW": (InternetGatewayAttachment, lambda self: None, lambda self: None),
        "SN"    : (Subnet, lambda self: None, lambda self: None),
        "SG"    : (SecurityGroup, lambda self: None, lambda self: None),
        "RTB"   : (RouteTable, lambda self: None, lambda self: None),
        "RTBSN" : (RouteTableAssociation, lambda self: None, lambda self: None),
        "RT"    : (Route, lambda self: None, lambda self: None),
        "EIP"   : (ElasticIP, lambda self: None, lambda self: None),
        "NAT"   : (NATGateway, lambda self: None, lambda self: None),
        "KEY"   : (KeyPair, lambda self: self.Val("KEY"), lambda self: self.Val("KEY")),
    }

    def fullresponse(self):
        # Custom JSON serializer for datetime objects
        def json_serial(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f'Type {type(obj)} not serializable')

        # create an EC2 client
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

        self.FIELD.append(field)

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

            cls_button = QtWidgets.QPushButton("c", self)
            cls_button.setObjectName(field + "_Class")
            cls_button.setFixedWidth(32)
            cls_button.clicked.connect(lambda: self.Cls_Clicked(field))
            layout.addWidget(cls_button)

    def Val(self, field, setval = None):
        line_edit = self.findChild(QtWidgets.QLineEdit, field + "_Id")
        if line_edit is not None:
            if setval is not None:
                line_edit.setText(setval)

            return line_edit.text()

        check_box = self.findChild(QtWidgets.QCheckBox, field + "_Flag")
        if check_box is not None:
            if setval is not None:
                if isinstance(setval, str):
                    setval = setval == "True"
                check_box.setChecked(setval)

            return check_box.isChecked()
        

    # def addTag(self, resource_id, name, value):
    #     self.boto3ec2.create_tags(
    #         Resources=[resource_id],
    #         Tags=[
    #             {
    #                 'Key': name,
    #                 'Value': value
    #             },
    #         ]
    #     )


    def Cls_Clicked(self, field):
        clss, addlambda, dellambda = self.prefix_map[Prefix(field)]

        new_window = AWS_Window(self, clss, self.Val(field), addlambda(self), dellambda(self))
        new_window.exec_()

        self.Val(field, new_window.Id.text())


    def Add_Clicked(self, field):
        pref = Prefix(field)

        try:
            if pref == "VPC":
                #response = self.boto3ec2.create_vpc(CidrBlock='10.3.0.0/16')
                #vpc_id = response['Vpc']['VpcId']
                #self.addTag(vpc_id, "Name", "vpc-Pavel-Eresko")

                vpc_id = Vpc.create("vpc-Pavel-Eresko", '10.3.0.0/16')

                self.Val(field, vpc_id)

            elif pref == "IGW":
                internet_gateway_id = InternetGateway.create("Pavel-Eresko")

                #response = self.boto3ec2.create_internet_gateway()
                #internet_gateway_id = response['InternetGateway']['InternetGatewayId']

                #self.addTag(internet_gateway_id, "Name", "igw-Pavel-Eresko")

                self.Val(field, internet_gateway_id)

            elif pref == "VPCIGW":
                InternetGatewayAttachment.create(self.Val("IGW"), self.Val("VPC"))
                #response = self.boto3ec2.attach_internet_gateway(
                #    InternetGatewayId=self.Val("IGW"),
                #    VpcId = self.Val("VPC")
                #)

                self.Val(field, True)

            elif pref == "SN":
                subnet_id = Subnet.create(
                    "Pavel-Eresko-" + field.replace("SN_", ""),
                    self.Val("VPC"),
                    self.Val(field.replace("SN_", "CIDR_"))
                )
                self.Val(field, subnet_id)

            elif pref == "RTB":
                route_table_id = RouteTable.create("Pavel-Eresko-" + field.replace("RTB_", ""), self.Val("VPC"))

                # response = self.boto3ec2.create_route_table(
                #     VpcId = self.Val("VPC")
                # )

                # route_table_id = response['RouteTable']['RouteTableId']

                # self.addTag(route_table_id, "Name", "rtb-Pavel-Eresko-" + field.replace("RTB_", ""))

                self.Val(field, route_table_id)

            elif pref == "RTBSN":
                RouteTableAssociation.create(self.Val(field.replace("RTBSN_", "SN_")), self.Val(field.replace("RTBSN_", "RTB_")))
#                response = self.boto3ec2.associate_route_table(
#                    SubnetId = self.Val(field.replace("RTBSN_", "SN_")),
#                    RouteTableId = self.Val(field.replace("RTBSN_", "RTB_"))
#                )
                
                self.Val(field, True)

            elif pref == "RT":
                GatewayId    = self.Val("IGW") if field == "RT_Public" else None
                NatGatewayId = self.Val("NAT") if field != "RT_Public" else None
                Route.create(self.Val(field.replace("RT_", "RTB_")), "0.0.0.0/0", GatewayId, NatGatewayId)

                #args = {
                #    "RouteTableId": self.Val(field.replace("RT_", "RTB_")),
                #    "DestinationCidrBlock": "0.0.0.0/0",
                #}
                #if field == "RT_Public":
                #    args["GatewayId"] = self.Val("IGW")
                #else:
                #    args["NatGatewayId"] = self.Val("NAT")

                #self.boto3ec2.create_route(**args)

                self.Val(field, True)

            elif pref == "EIP":
                id = ElasticIP.create("Pavel-Eresko-NAT")
                #response = self.boto3ec2.allocate_address(Domain='vpc')
                #eip_allocation_id = response['AllocationId']
                #self.addTag(eip_allocation_id, "Name", "eipassoc-Pavel-Eresko-NAT")
                self.Val(field, id)

            elif pref == "NAT":
                id = NATGateway("Pavel-Eresko", self.Val("SN_Public"), self.Val("EIP"))

                #response = self.boto3ec2.create_nat_gateway(
                #    SubnetId = self.Val("SN_Public"),
                #    AllocationId = self.Val("EIP")
                #)

                #nat_gateway_id = response['NatGateway']['NatGatewayId']

                #self.addTag(nat_gateway_id, "Name", "nat-Pavel-Eresko")

                self.Val(field, id)

            elif pref == "KEY":
                key_name = self.Val(field)

                KeyPair.create(key_name)

            elif pref == "EC2":

                Name = "i-Pavel-Eresko-" + field.replace("EC2_", "")
                ImageId = AWS.Const["EC2.ImageId.Linux"]
                InstanceType = AWS.Const["EC2.InstanceType"]
                KeyName = self.Val("KEY")
                SubnetId = self.Val(field.replace("EC2_", "SN_"))
                Groups = [self.Val("SG")]
                AssociatePublicIpAddress = True
                PrivateIpAddress = ("10.3.0.10" if field == "EC2_Public" else "10.3.1.10")
                UserData = AWS.Const["EC2.UserData.Apache"]

                instance_id = EC2Instance.create(
                    Name=Name,
                    ImageId=ImageId,
                    InstanceType=InstanceType,
                    KeyName=KeyName,
                    SubnetId=SubnetId,
                    Groups=Groups,
                    AssociatePublicIpAddress=AssociatePublicIpAddress,
                    PrivateIpAddress=PrivateIpAddress,
                    UserData=UserData
                )

                self.Val(field, instance_id)


            elif pref == "SG":
                sg = SecurityGroup.create("Pavel-Eresko-SSH-HTTP" + field.replace("SG_", ""), self.Val("VPC"), "security group by Pavel Eresko")
                SecurityGroupRule.create(sg, 'tcp', 22, '0.0.0.0/0') # SSH (22)
                SecurityGroupRule.create(sg, 'tcp', 80, '0.0.0.0/0') # HTTP (80)
                self.Val(field, sg)

        except Exception as e:
            print(f"{e}")


    def Del_Clicked(self, field):
        pref = Prefix(field)

        try:
            if pref == "VPC":
                Vpc.delete(self.Val(field))
                self.Val(field, "")

            elif pref == "IGW":
                InternetGateway.delete(self.Val(field))
                self.Val(field, "")

            elif pref == "VPCIGW":
                InternetGatewayAttachment.delete(self.Val("IGW"), self.Val("VPC"))
                #response = self.boto3ec2.detach_internet_gateway(
                #        InternetGatewayId=self.Val("IGW"),
                #        VpcId = self.Val("VPC")
                #    )
                self.Val(field, False)

            elif pref == "SN":
                Subnet.delete(self.Val(field))
                self.Val(field, "")

            elif pref == "RTB":
                RouteTable.delete(self.Val(field))
                self.Val(field, "")

            elif pref == "RTBSN":
                RouteTableAssociation.delete(self.Val(field.replace("RTBSN_", "SN_")), self.Val(field.replace("RTBSN_", "RTB_")))

                #response = self.boto3ec2.describe_route_tables(
                #    RouteTableIds=[self.Val(field.replace("RTBSN_", "RTB_"))]
                #)
                #associations = response['RouteTables'][0].get('Associations', [])

                #association_id = ""
                #for assoc in associations:
                #    if 'SubnetId' in assoc and assoc['SubnetId'] == self.Val(field.replace("RTBSN_", "SN_")):
                #        association_id = assoc['RouteTableAssociationId']
                #        break

                #response = self.boto3ec2.disassociate_route_table(
                #    AssociationId=association_id
                #)
                self.Val(field, False)

            elif pref == "RT":
                Route.delete(self.Val(field.replace("RT_", "RTB_")), "0.0.0.0/0")
                #response = self.boto3ec2.delete_route(
                #    RouteTableId = self.Val(field.replace("RT_", "RTB_")),
                #    DestinationCidrBlock = "0.0.0.0/0"
                #)
                self.Val(field, False)

            elif pref == "KEY":
                KeyPair.delete(self.Val(field))

            elif pref == "EC2":
                EC2Instance.delete(self.Val(field))
                self.Val(field, "")

            elif pref == "SG":
                SecurityGroup.delete(self.Val(field))
                self.Val(field, "")

        except Exception as e:
            print(f"{e}")


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        self.save()
        event.accept()

    def save(self):
        xml = ET.Element("fields")
        for field in self.fields:
            val = self.Val(field)
            if isinstance(val, bool):
                val = "True" if val else "False"
            xml.set(field, val)

        with open("awsPrefixForm.cfg", "w") as xml_file:
            xml_file.write(prettify(xml))


    def load(self):
        try:
            xml = ET.parse("awsPrefixForm.cfg").getroot()
        except FileNotFoundError:
            return
        
        for field in self.fields:
            if field in xml.attrib:
                val = xml.attrib[field]
                self.Val(field, val)


    def __init__(self):
        super(MyWidget, self).__init__()
        loadUi('awsPrefixForm.ui', self)

        self.fields = []
        for layout in self.findChildren(QtWidgets.QHBoxLayout):
            self.CreateInput(layout.objectName().replace("_Layout", ""))

        self.Val("Region", 'eu-central-1')

#        self.boto3ec2 = boto3.client('ec2', region_name = self.Val("Region"))

        self.load()


if __name__ == '__main__':
    app = QApplication([])
    widget = MyWidget()
    widget.show()
    app.exec_()
