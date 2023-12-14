from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QVBoxLayout, QWidget
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap

import boto3

# https://diagrams.mingrammer.com/
from diagrams import Diagram, Cluster
from diagrams.aws import general, compute, database, network, storage, security

class md():
    def __init__(self, Class, GetObjects, Fields, Icon):
        self.Class = Class
        self.GetObjects = GetObjects
        self.Fields = Fields
        self.Icon = Icon

    def LoadObjects(self, MD, parent = None):
#        self.Objects = [self.Class(obj) for obj in self.GetObjects(parent)]
        self.Objects = {}
        lst = self.GetObjects(parent)
        for obj in lst:
            firstfield = next(iter(MD[self.Class].Fields))
            self.Objects[obj[firstfield]] = self.Class(MD, obj)

        return


class AWSObject:
    def __init__(self, MD, data):
        for key, value in data.items():
            if not key in MD[type(self)].Fields:
                continue
            field = MD[type(self)].Fields[key]
            if type(field) == list:
                if field[0] == str:
                    continue
                else:
                    MD[field[0]].LoadObjects(MD, value)
            elif field == list:
                continue
            #elif field == str or field == cEC2 or field == cReservation:
            else:
                #print(f"{key} = {value}")
                setattr(self, key, value)


class cReservation(AWSObject): pass
class cEC2(AWSObject): pass
class cInternetGateway(AWSObject): pass
class cInternetGatewayAttachment(AWSObject): pass
class cSecurityGroup(AWSObject): pass
class cSubnet(AWSObject): pass
class cNetworkAcl(AWSObject): pass
class cRouteTable(AWSObject): pass
class cVpc(AWSObject): pass

class MyWidget(QWidget):
    def __init__(self):
        super(MyWidget, self).__init__()
        loadUi('AWS-graph.ui', self)

        self.Graph.setScene(QGraphicsScene(self))

        self.bDraw.clicked.connect(self.Draw)

        self.MD = {
            cReservation: md(
                Class = cReservation,
                GetObjects = lambda lst=None: boto3.client('ec2').describe_instances()['Reservations'],
                Fields = {
                    "ReservationId" : cReservation,
                    "OwnerId" : str,
                    "Groups" : [str], # !!!
                    "Instances" : [cEC2],
                },
                Icon = compute.EC2
            ),

            cEC2: md(
                Class = cEC2,
                GetObjects = lambda lst=None: lst,
                Fields = {
                    "InstanceId" : cEC2,
                    "InstanceType" : str,
                    "PublicIpAddress" : str,
                    "PrivateIpAddress": str,
                    "SubnetId": cSubnet,
                },
                Icon = compute.EC2
            ),

            cInternetGateway: md(
                Class = cInternetGateway,
                GetObjects = lambda lst=None: boto3.client('ec2').describe_internet_gateways()['InternetGateways'],
                Fields = {
                    "InternetGatewayId" : cInternetGateway,
                },
                Icon = general.InternetGateway
            ),

            cInternetGatewayAttachment: md(
                Class = cInternetGatewayAttachment,
                GetObjects = lambda lst=None: lst,
                Fields = {
                    "VpcId" : cVpc,
                },
                Icon = general.InternetGateway
            ),

            cSecurityGroup: md(
                Class = cSecurityGroup,
                GetObjects = lambda lst=None: boto3.client('ec2').describe_security_groups()['SecurityGroups'],
                Fields = {
                    "GroupName" : str,
                    "GroupId" : str,
                    "VpcId" : cVpc,
                },
                Icon = security.SecurityHub
            ),

            cSubnet: md(
                Class = cSubnet,
                GetObjects = lambda lst=None: boto3.client('ec2').describe_subnets()['Subnets'],
                Fields = {
                    "SubnetId" : cSubnet,
                    "CidrBlock" : str,
                    "VpcId" : cVpc,
                    "AvailabilityZone" : str, ##!!!!!!!!!!!!!!!
                },
                Icon = network.PrivateSubnet

            ),

            cNetworkAcl: md(
                Class = cNetworkAcl,
                GetObjects = lambda lst=None: boto3.client('ec2').describe_network_acls()['NetworkAcls'],
                Fields = {
                    "NetworkAclId" : cNetworkAcl,
                },
                Icon = network.Nacl
            ),

            cRouteTable: md(
                Class = cRouteTable,
                GetObjects = lambda lst=None: boto3.client('ec2').describe_route_tables()['RouteTables'],
                Fields = {
                    "RouteTableId" : cRouteTable,
                },
                Icon = network.RouteTable
            ),

            cVpc: md(
                Class = cVpc,
                GetObjects = lambda lst=None: boto3.client('ec2').describe_vpcs()['Vpcs'],
                Fields = {
                    "VpcId" : cVpc,
                },
                Icon = network.VPCCustomerGateway
            ),

        }

        self.Draw()


    def Draw(self):
        
        self.MD[cVpc            ].LoadObjects(self.MD)
        self.MD[cReservation    ].LoadObjects(self.MD)
        self.MD[cSubnet         ].LoadObjects(self.MD)
        self.MD[cNetworkAcl     ].LoadObjects(self.MD)
        self.MD[cRouteTable     ].LoadObjects(self.MD)
        self.MD[cInternetGateway].LoadObjects(self.MD)

        with Diagram("graph", show=False):

            with Cluster("EC2"):
                for id, item in self.MD[cEC2].Objects.items():
                    icon = self.MD[cReservation].Icon(id)
                    setattr(item, "Icon", icon)

            with Cluster("Subnets"):
                for id, item in self.MD[cSubnet].Objects.items():
                    icon = self.MD[cSubnet].Icon(id)
                    setattr(item, "Icon", icon)

#            with Cluster("Network ACLs"):
#                for id, item in self.MD[cNetworkAcl].Objects.items():
#                    icon = self.MD[cNetworkAcl].Icon(id)
#                    setattr(item, "Icon", icon)

#            with Cluster("Route Tables"):
#                for id, item in self.MD[cRouteTable].Objects.items():
#                    icon = self.MD[cRouteTable].Icon(id)
#                    setattr(item, "Icon", icon)

#            with Cluster("Internet Gateways"):
#                for id, item in self.MD[cInternetGateway].Objects.items():
#                    icon = self.MD[cInternetGateway].Icon(id)
#                    setattr(item, "Icon", icon)

            with Cluster("VPCs"):
                for id, item in self.MD[cVpc].Objects.items():
                    icon = self.MD[cVpc].Icon(id)
                    setattr(item, "Icon", icon)


            for id, item in self.MD[cEC2].Objects.items():
                item.Icon >> self.MD[cSubnet].Objects[item.SubnetId].Icon
            
            for id, item in self.MD[cSubnet].Objects.items():
                item.Icon >> self.MD[cVpc].Objects[item.VpcId].Icon


        Diagram("Web Services", show=False).render()
        pixmap = QPixmap("graph.png")
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.Graph.scene().addItem(pixmap_item)

        #self.Graph.fitInView(self.Graph.scene().sceneRect()) # Autoscaling

if __name__ == '__main__':
    app = QApplication([])
    widget = MyWidget()
    widget.show()
    app.exec_()
