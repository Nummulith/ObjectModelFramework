from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QVBoxLayout, QWidget
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap

import boto3

# https://diagrams.mingrammer.com/
#from diagrams import Diagram, Cluster
#from diagrams.aws import general, compute, database, network, storage, security

from graphviz import Digraph

fType = 0
fId = 1
fOwner = 2
fIn = 3
fOut = 4

class cParent:
    Icon = "AWS"
    Show = True

    def __init__(self, Data, parent, resp):
        if parent != None:
            setattr(self, "_Parent", parent)

        fields = type(self).Fields()
        for key, cfg in fields.items():
            if not key in resp:
                continue
            value = resp[key]
            field = fields[key][fType]
            if type(field) == list:
                if len(field) == 0:
                    #setattr(self, key, value)
                    continue
                if field[0] == str:
                    continue
                else:
                    field[0].LoadObjects(Data, field[0], self, value)
            elif field == list:
                continue
            #elif field == str or field == cEC2 or field == cReservation:
            elif type(field) == dict:
                tkkey, tkval = next(iter(field.items()))
                for pair in value:
                    setattr(self, "Tag_" + pair[tkkey], pair[tkval])
                continue
            else:
                #print(f"{key} = {value}")
                setattr(self, key, value)
        
        self.items = []

    def GetId(self):
        field = next((key for key, value in self.Fields().items() if value[fId]), None)
        return getattr(self, field)

    def GetOwner(self, Data):
        field = next(((key, value) for key, value in self.Fields().items() if value[fOwner]), (None, None))

        if field[0] == None:
            return None
        
        id = getattr(self, field[0])
        clss = field[1][fType]

        return Data[clss][id]

    def GetView(self):
        return self.GetId()

    @staticmethod
    def LoadObjects(Data, Class, parent = None, lst = None):
#        self.Objects = [self.Class(obj) for obj in self.GetObjects(parent)]
        if not Class in Data:
            Data[Class] = {}

        els = Class.GetObjects(parent, lst)
        for el in els:
            obj = Class(Data, parent, el)
            Data[Class][obj.GetId()] = obj


class cRoot(cParent):
    def __init__(self, Data):
        super().__init__(Data, None, {"Id": "root-" + 17*"0"})

    @staticmethod
    def Fields():
        return {"Id" : (cRoot,True,False,False,False)}
        
class cReservation(cParent): 
    Icon = "EC2"
    Show = False

    @staticmethod
    def Fields():
        return {
                    "ReservationId" : (cReservation,True,False,False,False),
                    "OwnerId"       : (str,False,False,False,False),
                    "Groups"        : ([str],False,False,False,False), # !!!
                    "Instances"     : ([cEC2],False,False,False,False),
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_instances()['Reservations']
    
class cEC2(cParent): 
    _ParentType : cReservation
    Icon = "EC2"

    @staticmethod
    def Fields():
        return {
                    "InstanceId" : (cEC2,True,False,False,False),
                    "InstanceType" : (str,False,False,False,False),
                    "PublicIpAddress" : (str,False,False,False,False),
                    "PrivateIpAddress" : (str,False,False,False,False),
                    "SubnetId" : (cSubnet,False,True,False,False),
                    'PlatformDetails' : (str,False,False,False,False),
                    'Tags' : ({"Key" : "Value"},False,False,False,False),
                }
    
# 'AmiLaunchIndex': 0
# 'ImageId': 'ami-0669b163befffbdfc'
# 'KeyName': 'key-antony'
# 'LaunchTime': datetime.datetime(2023, 12, 14, 15, 31, 2, tzinfo=tzutc())
# 'Monitoring': {'State': 'disabled'}
# 'Placement': {'AvailabilityZone': 'eu-central-1b', 'GroupName': '', 'Tenancy': 'default'}
# 'PrivateDnsName': 'ip-10-222-2-11.eu-central-1.compute.internal'
# 'ProductCodes': []
# 'PublicDnsName': ''
# 'State': {'Code': 16, 'Name': 'running'}
# 'StateTransitionReason': ''
# 'VpcId': 'vpc-055b28f7d73c69acf'
# 'Architecture': 'x86_64'
# 'BlockDeviceMappings': [{'DeviceName': '/dev/xvda', 'Ebs': {...}}]
# 'ClientToken': '5db5facc-d068-410c-a526-29dba78f8184'
# 'EbsOptimized': False
# 'EnaSupport': True
# 'Hypervisor': 'xen'
# 'NetworkInterfaces': [{'Attachment': {...}, 'Description': '', 'Groups': [...], 'Ipv6Addresses': [...], 'MacAddress': '06:02:cb:61:9c:7b', 'NetworkInterfaceId': 'eni-06ef5645d896ee146', 'OwnerId': '047989593255', 'PrivateIpAddress': '10.222.2.11', 'PrivateIpAddresses': [...], ...}]
# 'RootDeviceName': '/dev/xvda'
# 'RootDeviceType': 'ebs'
# 'SecurityGroups': [{'GroupName': 'secgrup-antony', 'GroupId': 'sg-0e050b1cd54e6fcc8'}]
# 'SourceDestCheck': True
# 'VirtualizationType': 'hvm'
# 'CpuOptions': {'CoreCount': 1, 'ThreadsPerCore': 1}
# 'CapacityReservationSpecification': {'CapacityReservationPreference': 'open'}
# 'HibernationOptions': {'Configured': False}
# 'MetadataOptions': {'State': 'applied', 'HttpTokens': 'required', 'HttpPutResponseHopLimit': 2, 'HttpEndpoint': 'enabled', 'HttpProtocolIpv6': 'disabled', 'InstanceMetadataTags': 'disabled'}
# 'EnclaveOptions': {'Enabled': False}
# 'BootMode': 'uefi-preferred'
# 'UsageOperation': 'RunInstances'
# 'UsageOperationUpdateTime': datetime.datetime(2023, 12, 14, 15, 31, 2, tzinfo=tzutc())
# 'PrivateDnsNameOptions': {'HostnameType': 'ip-name', 'EnableResourceNameDnsARecord': False, 'EnableResourceNameDn...AAAARecord': False}
# 'MaintenanceOptions': {'AutoRecovery': 'default'}
# 'CurrentInstanceBootMode': 'legacy-bios'

    
    @staticmethod
    def GetObjects(parent, lst):
        return lst

    def GetView(self):
        return f"{getattr(self, 'Tag_Name', "<>")} ({getattr(self, "PlatformDetails")})"
    #\n {getattr(self, "PublicIpAddress", "")} / {getattr(self, "PrivateIpAddress", "")}


class cInternetGateway(cParent): 
    Icon = "Gateway"

    @staticmethod
    def Fields():
        return {
                    "InternetGatewayId" : (cInternetGateway,True,False,False,False),
                    'OwnerId' : (str,False,False,False,False),
                    'Attachments' : ([cInternetGatewayAttachment],False,False,False,False),
                    'Tags' : ({"Key" : "Value"},False,False,False,False),
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_internet_gateways()['InternetGateways']

    def GetView(self):
        return f"{getattr(self, 'Tag_Name', "")}"

class cInternetGatewayAttachment(cParent): 
    _ParentType = cInternetGateway
    Icon = "Gateway"

    @staticmethod
    def Fields():
        return {
                    "VpcId" : (cVpc,False,False,False,False),
                    'State' : (str,False,False,False,False),
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return lst
    
    def GetId(self):
        return self._Parent.GetId() + " ??"
        field = next((key for key, value in self.Fields().items() if value[fId]), None)
        return getattr(self, field)

class cNATGateway(cParent): 
    Icon = "NATGateway"

    @staticmethod
    def Fields():
        return {
                    "NatGatewayId" : (cNATGateway,True,False,False,False),
                    "SubnetId" : (cSubnet,False,True,False,False),
                    "State" : (str,False,False,False,False),
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_nat_gateways()['NatGateways']
    
class cSecurityGroup(cParent): 
    @staticmethod
    def Fields():
        return {
                    "GroupName" : (str,False,False,False,False),
                    "GroupId" : (str,True,False,False,False),
                    "VpcId" : (cVpc,False,True,False,False),
#                    IpPermissions\IpRanges\
                        # for permission in group['IpPermissions']:
                        #     print(f"- From Port: {permission.get('FromPort', 'N/A')}")
                        #     print(f"  To Port: {permission.get('ToPort', 'N/A')}")
                        #     print(f"  Protocol: {permission.get('IpProtocol', 'N/A')}")
                        #     print("  IP Ranges:")
                        #     for ip_range in permission.get('IpRanges', []):
                        #         print(f"  - {ip_range.get('CidrIp', 'N/A')}")
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_security_groups()['SecurityGroups']
    
class cSubnet(cParent): 
    @staticmethod
    def Fields():
        return {
                    "SubnetId" : (cSubnet,True,False,False,False),
                    "CidrBlock" : (str,False,False,False,False),
                    "VpcId" : (cVpc,False,True,False,False),
                    "AvailabilityZone" : (str,False,False,False,False), ##!!!!!!!!!!!!!!!
                    'AvailabilityZoneId' : (str,False,False,False,False), ##!!!!!!!!!!!!!!!
                    'Tags' : ({"Key" : "Value"},False,False,False,False),
                }
    
# 'AvailableIpAddressCount': 251
# 'DefaultForAz': False
# 'MapPublicIpOnLaunch': False
# 'MapCustomerOwnedIpOnLaunch': False
# 'State': 'available'
# 'OwnerId': '047989593255'
# 'AssignIpv6AddressOnCreation': False
# 'Ipv6CidrBlockAssociationSet': []
# 'SubnetArn': 'arn:aws:ec2:eu-central-1:047989593255:subnet/subnet-06678d33e23eba72f'
# 'EnableDns64': False
# 'Ipv6Native': False
# 'PrivateDnsNameOptionsOnLaunch': {'HostnameType': 'ip-name', 'EnableResourceNameDnsARecord': False, 'EnableResourceNameDn...AAAARecord': False}


    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_subnets()['Subnets']
    
    def GetView(self):
        return f"{getattr(self, 'Tag_Name', "<>")} ({getattr(self, "CidrBlock", "")})"



class cNetworkAcl(cParent): 
    Icon = "NetworkAccessControlList"

    @staticmethod
    def Fields():
        return {
                    "NetworkAclId" : (cNetworkAcl,True,False,False,False),
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_network_acls()['NetworkAcls']
    
class cRouteTable(cParent): 
    Icon = "RouteTable"

    @staticmethod
    def Fields():
        return {
                    "RouteTableId" : (cRouteTable,True,False,False,False),
                    "VpcId" : (cVpc,False,True,False,False),
                    "Routes" : ([cRoute],False,False,False,False),
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_route_tables()['RouteTables']
    
class cRoute(cParent): 
    _ParentType = cRouteTable
    Icon = "Route"

    @staticmethod
    def Fields():
        return {
                    "DestinationCidrBlock" : (str,False,False,False,False),
                    "GatewayId" : (cInternetGateway,False,False,False,False),
                    "InstanceId" : (cEC2,False,False,False,False),
                    "NatGatewayId" : (cNATGateway,False,False,False,False),
                    "NetworkInterfaceId" : (cNetworkInterface,False,False,False,False),
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return lst
    
class cVpc(cParent): 
    Icon = "VPC"

    @staticmethod
    def Fields():
        return {
                    "VpcId"           : (cVpc,True,False,False,False),
                    "NetworkAclId"    : (cNetworkAcl,False,False,False,False),
                    'CidrBlock'       : (str,False,False,False,False),
                    'DhcpOptionsId'   : (str,False,False,False,False), #'dopt-0de83e37b426fcfda'
                    'State'           : (str,False,False,False,False),
                    'OwnerId'         : (str,False,False,False,False), #'047989593255'
                    'InstanceTenancy' : (str,False,False,False,False),
#                    'CidrBlockAssociationSet' : [{'AssociationId': 'vpc-cidr-assoc-070bb...bcc9c9695b', 'CidrBlock': '10.222.0.0/16', 'CidrBlockState': {...}}],
                    'IsDefault'       : (bool,False,False,False,False),
                    'Tags'            : ({"Key" : "Value"},False,False,False,False)
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_vpcs()['Vpcs']
    
    def GetView(self):
        return f"VPC {getattr(self, 'Tag_Name', "<>")} {self.CidrBlock}"
    
class cVpcEntry(cParent): 
    _ParentType = cVpc
    Icon = "VPC"

    @staticmethod
    def Fields():
        return {
                    "RuleNumber" : (int,False,False,False,False),
                    "Protocol"   : (str,False,False,False,False),
                    "PortRange"  : (str,False,False,False,False),
                    "RuleAction" : (str,False,False,False,False),
                    "CidrBlock"  : (str,False,False,False,False),
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return lst
    
class cNetworkInterface(cParent): 
#    Icon = "network.VPCElasticNetworkInterface"

    @staticmethod
    def Fields():
        return {
                    "NetworkInterfaceId" : (cNetworkInterface,True,False,False,False),
                    "Status"             : (str,False,False,False,False),
                    "Attachment"         : (str,False,False,False,False), #    print("Attachment ID:", network_interface['Attachment']['AttachmentId'])
                    "VpcId"              : (cVpc,False,False,False,False),
                    "SubnetId"           : (cSubnet,False,False,False,False),
                    "PrivateIpAddresses" : (str,False,False,False,False), # print("Private IP Addresses:", [private_ip['PrivateIpAddress'] for private_ip in network_interface['PrivateIpAddresses']])
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_network_interfaces()['NetworkInterfaces']
    
class cS3(cParent): 
    Icon = "S3"

    @staticmethod
    def Fields():
        return {
                    "Name" : (cS3,True,False,False,False),
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('s3').list_buckets()['Buckets']


class MyWidget(QWidget):
    def __init__(self):
        super(MyWidget, self).__init__()
        loadUi('AWS-graph.ui', self)

        self.Graph.setScene(QGraphicsScene(self))

        self.bDraw.clicked.connect(self.Draw)

        self.Draw()

    def NodeLabel(self, obj):
        return f'''<
            <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
                <TR>
                    <TD BGCOLOR="#A9DFBF" PORT="p1"><B>{obj.GetView()}</B></TD>
                </TR>
                <TR>
                    <TD BGCOLOR="white" PORT="p2"><IMG SRC="icons/{type(obj).Icon}.png"/></TD>
                </TR>
                <TR>
                    <TD BGCOLOR="#A9DFBF" PORT="p3"><FONT POINT-SIZE="7.0">{obj.GetId()[-17:]}</FONT></TD>
                </TR>
            </TABLE>
        >'''

    def ClusterLabel(self, obj):
        return f'''<
            <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4">
                <TR>
                    <TD ROWSPAN="2"><IMG SRC="icons/{type(obj).Icon}.png"/></TD>
                    <TD><B>{obj.GetView()}</B></TD>
                </TR>
                <TR>
                    <TD><FONT POINT-SIZE="7.0">{obj.GetId()[-17:]}</FONT></TD>
                </TR>
            </TABLE>
        >'''

    def DrawRec(self, par):
        for clss, list in self.Data.items():
            if not clss.Show: continue

            for id, obj in list.items():
                if par == None:
                    if hasattr(obj, "_Owner") : continue
                else:
                    if (not hasattr(obj, "_Owner") or obj._Owner != par) \
                    : continue
                        #and obj != par \

                if not hasattr(par, "_Digraph"):
                    name = "cluster_" + obj.GetId()[-17:]
                    par._Context = par._Owner._Digraph.subgraph(name=name)
                    par._Digraph = par._Context.__enter__()
#                    par._Digraph.attr(label='cluster\n' + par.GetId()) # + par.GetId()
                    par._Digraph.attr(label=self.ClusterLabel(par)) # + par.GetId()
                    par._Digraph.attr(style='filled', fillcolor='#D4E6F1')

                    par._Digraph.node(name=par.GetId(), shape='point', width='0.1')
                
                
                if len(obj.items) == 0:
                    par._Digraph.node(name=obj.GetId(), shape='plaintext', label=self.NodeLabel(obj))
                else:
                    self.DrawRec(obj)

                #print(f"{par}.{par.GetId()} -> {obj}.{obj.GetId()} ")
        
        if hasattr(par, "_Context"):
            par._Context.__exit__(None, None, None)
            par._Context = None

        if hasattr(par, "_Digraph"):
            par._Digraph = None


    def Draw(self):
        
        self.Data = {}

        root = cRoot(self.Data)
        cParent.LoadObjects(self.Data, cVpc        )
        cParent.LoadObjects(self.Data, cSubnet     )
        cParent.LoadObjects(self.Data, cReservation)
        cParent.LoadObjects(self.Data, cInternetGateway)
        
#       cParent.LoadObjects(self.Data, cNetworkAcl )
#       cParent.LoadObjects(self.Data, cRouteTable )

        for clss, lst in self.Data.items():
            for id, obj in lst.items():
                owner = obj.GetOwner(self.Data)
                if owner == None:
                    owner = root

                # if obj.ParentField != None:
                #     parcl = clss.Fields()[obj.ParentField][fType]
                #     if hasattr(obj, obj.ParentField):
                #         if obj.ParentField == "_Parent":
                #             owner = obj._Parent
                #         else:
                #             parid = getattr(obj, obj.ParentField)
                #             owner = self.Data[parcl][parid]

                obj._Owner = owner
                owner.items.append(obj)

        dot = Digraph('AWS_Structure', format='png')

        root._Digraph = dot

        self.DrawRec(root)

        # if hasattr(root, "_Context"):
        #     root._Context.__exit__(None, None, None)
        # for clss, lst in self.Data.items():
        #     for id, obj in lst.items():
        #         if hasattr(obj, "_Context"):
        #             obj._Context.__exit__(None, None, None)



#       !!!!!!!!!!!!!!!!!
           
#       With
        if False:
            with dot.subgraph(name='cluster_subnet') as subnet:
                subnet.attr(label='Subnet Cluster') 
                subnet.attr(style='filled', fillcolor='#D4E6F1')

                for id, item in self.Data[cEC2].items():
                    subnet.node(name=f'EC2_{id}', shape='plaintext', label=self.NodeLabel(item))

                    break

#       It works
        if False:
            context0 = dot.subgraph(name='cluster_subnet0')
            subnet0 = context0.__enter__()
    #        with dot.subgraph(name='cluster_subnet') as subnet:
            subnet0.attr(label='Subnet Cluster 0')  # Задаем имя кластера
            subnet0.attr(style='filled', fillcolor='#D4E6F1')  # Цветной фон кластера

            context1 = dot.subgraph(name='cluster_subnet1')
            subnet1 = context1.__enter__()
    #        with dot.subgraph(name='cluster_subnet') as subnet:
            subnet1.attr(label='Subnet Cluster 1')  # Задаем имя кластера
            subnet1.attr(style='filled', fillcolor='#D4E6F1')  # Цветной фон кластера

            for i in range(0, 4):
                node_label = f'Node {i}'
                sn=subnet0 if i % 2 == 0 else subnet1
                sn.node(name=f'Node_{i}', shape='plaintext', label=self.NodeLabel(f'Node_{i}', f'{i}'))
                
#            subnet0.node(name='EC2_1', shape='plaintext', label=self.NodeLabel("1234", "id0"))
#            subnet1.node(name='EC2_2', shape='plaintext', label=self.NodeLabel("4321", "id1"))
            
            context0.__exit__(None, None, None)
            context1.__exit__(None, None, None)


#       nested
        if False:
            context5 = dot.subgraph(name='cluster_subnet0')
            subnet5 = context5.__enter__()
    #        with dot.subgraph(name='cluster_subnet') as subnet:
            subnet5.attr(label='Common')  # Задаем имя кластера
            subnet5.attr(style='filled', fillcolor='#D4FFF1')  # Цветной фон кластера

            context0 = subnet5.subgraph(name='cluster_subnet0')
            subnet0 = context0.__enter__()
    #        with dot.subgraph(name='cluster_subnet') as subnet:
            subnet0.attr(label='Subnet Cluster 0')  # Задаем имя кластера
            subnet0.attr(style='filled', fillcolor='#D4E6F1')  # Цветной фон кластера

            context1 = subnet5.subgraph(name='cluster_subnet1')
            subnet1 = context1.__enter__()
    #        with dot.subgraph(name='cluster_subnet') as subnet:
            subnet1.attr(label='Subnet Cluster 1')  # Задаем имя кластера
            subnet1.attr(style='filled', fillcolor='#D4E6F1')  # Цветной фон кластера

            for i in range(0, 4):
                node_label = f'Node {i}'
                sn=subnet0 if i % 2 == 0 else subnet1
                sn.node(name=f'Node_{i}', shape='plaintext', label=self.NodeLabel(f'Node_{i}', f'{i}'))
                
#            subnet0.node(name='EC2_1', shape='plaintext', label=self.NodeLabel("1234", "id0"))
#            subnet1.node(name='EC2_2', shape='plaintext', label=self.NodeLabel("4321", "id1"))
            
            context0.__exit__(None, None, None)
            context1.__exit__(None, None, None)
            context5.__exit__(None, None, None)


        if False:
            context0 = dot.subgraph(name='cluster_subnet2')
            subnet0 = context0.__enter__()
            subnet0.attr(label='Subnet Cluster 2')  # Задаем имя кластера
            subnet0.attr(style='filled', fillcolor='#D4E6F1')  # Цветной фон кластера
            subnet0.node(name='EC2_1', shape='plaintext', label=self.NodeLabel("1234", "id0"))
            context0.__exit__(None, None, None)


        # Добавляем связи
        dot.edge('vpc-055b28f7d73c69acf:p1', 'subnet-00956c35e071ae718')
#        dot.edge('vpc-055b28f7d73c69acf:p1', 'cluster_0abb2b25f63d39386')



#       !!!!!!!!!!!!!!!!!

        # Сохраняем диаграмму в файл
        dot.render('AWS-graph', format='png', cleanup=True)

        #pixmap = QPixmap("AWS-graph.png")
        #pixmap_item = QGraphicsPixmapItem(pixmap)
        #self.Graph.scene().addItem(pixmap_item)

        #self.Graph.fitInView(self.Graph.scene().sceneRect()) # Autoscaling

#        self.close()


if __name__ == '__main__':
    app = QApplication([])
    widget = MyWidget()
#    widget.show()
#    app.exec_()
