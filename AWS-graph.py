from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QVBoxLayout, QWidget
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap

import boto3

# https://diagrams.mingrammer.com/
#from diagrams import Diagram, Cluster
#from diagrams.aws import general, compute, database, network, storage, security

from graphviz import Digraph



class cParent:
    Icon = "AWS"
    Show = True

    def __init__(self, Data, parent, resp):
        if parent != None:
            setattr(self, "_Parent", parent)

        fields = type(self).Fields()
        for key, value in resp.items():
            if not key in fields:
                continue
            field = fields[key]
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
        firstfield = next(iter(self.Fields()))
        return getattr(self, firstfield)
    
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
        super().__init__(Data, None, {})
        self.Id = "root-" + 17*"0"

    @staticmethod
    def Fields():
        return {"Id": cRoot}
        
class cReservation(cParent): 
    ParentField = None
    Icon = "EC2"
    Show = False

    @staticmethod
    def Fields():
        return {
                    "ReservationId" : cReservation,
                    "OwnerId" : str,
                    "Groups" : [str], # !!!
                    "Instances" : [cEC2],
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_instances()['Reservations']
    
class cEC2(cParent): 
    ParentField = "SubnetId" # 
    Icon = "EC2"

    @staticmethod
    def Fields():
        return {
                    "InstanceId" : cEC2,
                    "_Parent" : cReservation,
                    "InstanceType" : str,
                    "PublicIpAddress" : str,
                    "PrivateIpAddress": str,
                    "SubnetId": cSubnet,
                }
    
# 'AmiLaunchIndex': 0
# 'ImageId': 'ami-0669b163befffbdfc'
# 'InstanceId': 'i-074df4a891ade9495'
# 'InstanceType': 't2.micro'
# 'KeyName': 'key-antony'
# 'LaunchTime': datetime.datetime(2023, 12, 14, 15, 31, 2, tzinfo=tzutc())
# 'Monitoring': {'State': 'disabled'}
# 'Placement': {'AvailabilityZone': 'eu-central-1b', 'GroupName': '', 'Tenancy': 'default'}
# 'PrivateDnsName': 'ip-10-222-2-11.eu-central-1.compute.internal'
# 'PrivateIpAddress': '10.222.2.11'
# 'ProductCodes': []
# 'PublicDnsName': ''
# 'State': {'Code': 16, 'Name': 'running'}
# 'StateTransitionReason': ''
# 'SubnetId': 'subnet-0abb2b25f63d39386'
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
# 'Tags': [{'Key': 'Name', 'Value': 'app-server-antony'}]
# 'VirtualizationType': 'hvm'
# 'CpuOptions': {'CoreCount': 1, 'ThreadsPerCore': 1}
# 'CapacityReservationSpecification': {'CapacityReservationPreference': 'open'}
# 'HibernationOptions': {'Configured': False}
# 'MetadataOptions': {'State': 'applied', 'HttpTokens': 'required', 'HttpPutResponseHopLimit': 2, 'HttpEndpoint': 'enabled', 'HttpProtocolIpv6': 'disabled', 'InstanceMetadataTags': 'disabled'}
# 'EnclaveOptions': {'Enabled': False}
# 'BootMode': 'uefi-preferred'
# 'PlatformDetails': 'Linux/UNIX'
# 'UsageOperation': 'RunInstances'
# 'UsageOperationUpdateTime': datetime.datetime(2023, 12, 14, 15, 31, 2, tzinfo=tzutc())
# 'PrivateDnsNameOptions': {'HostnameType': 'ip-name', 'EnableResourceNameDnsARecord': False, 'EnableResourceNameDn...AAAARecord': False}
# 'MaintenanceOptions': {'AutoRecovery': 'default'}
# 'CurrentInstanceBootMode': 'legacy-bios'

    
    @staticmethod
    def GetObjects(parent, lst):
        return lst

class cInternetGateway(cParent): 
    ParentField = None
    Icon = "Gateway"

    @staticmethod
    def Fields():
        return {
                    "InternetGatewayId" : cInternetGateway,
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_internet_gateways()['InternetGateways']

class cInternetGatewayAttachment(cParent): 
    ParentField = None # _Parent
    Icon = "Gateway"

    @staticmethod
    def Fields():
        return {
                    "VpcId" : cVpc,
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return lst
    
class cNATGateway(cParent): 
    ParentField = "SubnetId"
    Icon = "NATGateway"

    @staticmethod
    def Fields():
        return {
                    "NatGatewayId" : cNATGateway,
                    "SubnetId" : cSubnet,
                    "State" : str,
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_nat_gateways()['NatGateways']
    
class cSecurityGroup(cParent): 
    ParentField = "VpcId"

    @staticmethod
    def Fields():
        return {
                    "GroupName" : str,
                    "GroupId" : str,
                    "VpcId" : cVpc,
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
    ParentField = "VpcId"

    @staticmethod
    def Fields():
        return {
                    "SubnetId" : cSubnet,
                    "CidrBlock" : str,
                    "VpcId" : cVpc,
                    "AvailabilityZone" : str, ##!!!!!!!!!!!!!!!
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_subnets()['Subnets']
    
class cNetworkAcl(cParent): 
    ParentField = None
    Icon = "NetworkAccessControlList"

    @staticmethod
    def Fields():
        return {
                    "NetworkAclId" : cNetworkAcl,
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_network_acls()['NetworkAcls']
    
class cRouteTable(cParent): 
    ParentField = "VpcId"
    Icon = "RouteTable"

    @staticmethod
    def Fields():
        return {
                    "RouteTableId" : cRouteTable,
                    "VpcId" : cVpc,
                    "Routes" : [cRoute],
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_route_tables()['RouteTables']
    
class cRoute(cParent): 
    ParentField = None # _Parent
    Icon = "Route"

    @staticmethod
    def Fields():
        return {
                    #"_Parent" : cRouteTable,
                    "DestinationCidrBlock" : str,
                    "GatewayId" : cInternetGateway,
                    "InstanceId" : cEC2,
                    "NatGatewayId" : cNATGateway,
                    "NetworkInterfaceId" : cNetworkInterface,
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return lst
    
class cVpc(cParent): 
    ParentField = None
    Icon = "VPC"

    @staticmethod
    def Fields():
        return {
                    "VpcId" : cVpc,
                    "NetworkAclId" : cNetworkAcl,
                    'CidrBlock': str,
                    'DhcpOptionsId': str, #'dopt-0de83e37b426fcfda'
                    'State': 'available',
                    'OwnerId': '047989593255',
                    'InstanceTenancy': 'default',
#                    'CidrBlockAssociationSet': [{'AssociationId': 'vpc-cidr-assoc-070bb...bcc9c9695b', 'CidrBlock': '10.222.0.0/16', 'CidrBlockState': {...}}],
                    'IsDefault': bool,
                    'Tags': {"Key" : "Value"}
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_vpcs()['Vpcs']
    
    def GetView(self):
        return f"VPC {getattr(self, 'Tag_Name', "<>")} {self.CidrBlock}"
    
class cVpcEntry(cParent): 
    ParentField = None # _Parent
    Icon = "VPC"

    @staticmethod
    def Fields():
        return {
                    #"_Parent" : cVpc,
                    "RuleNumber" : int,
                    "Protocol" : str,
                    "PortRange" : str,
                    "RuleAction" : str,
                    "CidrBlock" : str,
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return lst
    
class cNetworkInterface(cParent): 
    ParentField = None # _Parent
#    Icon = "network.VPCElasticNetworkInterface"

    @staticmethod
    def Fields():
        return {
                    "NetworkInterfaceId" : cNetworkInterface,
                    "Status" : str,
                    "Attachment" : str, #    print("Attachment ID:", network_interface['Attachment']['AttachmentId'])
                    "VpcId" : cVpc,
                    "SubnetId" : cSubnet,
                    "PrivateIpAddresses" : str, # print("Private IP Addresses:", [private_ip['PrivateIpAddress'] for private_ip in network_interface['PrivateIpAddresses']])
                }
    
    @staticmethod
    def GetObjects(parent, lst):
        return boto3.client('ec2').describe_network_interfaces()['NetworkInterfaces']
    
class cS3(cParent): 
    ParentField = None
    Icon = "S3"

    @staticmethod
    def Fields():
        return {
                    "Name" : cS3,
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
                    if hasattr(obj, "_Parent") : continue
                else:
                    if (not hasattr(obj, "_Parent") or obj._Parent != par) \
                    : continue
                        #and obj != par \

                if not hasattr(par, "_Digraph"):
                    name = "cluster_" + obj.GetId()[-17:]
                    par._Context = par._Parent._Digraph.subgraph(name=name)
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
#       cParent.LoadObjects(self.Data, cNetworkAcl )
#       cParent.LoadObjects(self.Data, cRouteTable )
#       cParent.LoadObjects(self.Data, cInternetGateway)

        for clss, lst in self.Data.items():
            for id, obj in lst.items():
                par = root

                if obj.ParentField != None:
                    parcl = clss.Fields()[obj.ParentField]
                    if hasattr(obj, obj.ParentField):
                        if obj.ParentField == "_Parent":
                            par = obj._Parent
                        else:
                            parid = getattr(obj, obj.ParentField)
                            par = self.Data[parcl][parid]

                obj._Parent = par
                par.items.append(obj)

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
